"""Dynamic tree distances, ranked palindromes, digit DP, inversion thresholds, and instruction simulation."""
from functools import lru_cache

from .import_batch_055 import entry


def tree_distance_oracle(args):
    n, edges, queries = args
    graph = [[] for _ in range(n + 1)]
    weights = {}
    for u, v, weight in edges:
        graph[u].append(v); graph[v].append(u); weights[tuple(sorted((u, v)))] = weight
    parent = [0] * (n + 1)
    stack = [1]
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor != parent[node]:
                parent[neighbor] = node; stack.append(neighbor)
    answer = []
    for query in queries:
        if query[0] == 1:
            weights[tuple(sorted((query[1], query[2])))] = query[3]
        else:
            node = query[1]; distance = 0
            while node != 1:
                distance += weights[tuple(sorted((node, parent[node])))]; node = parent[node]
            answer.append(distance)
    return answer


def random_tree_distance(rng):
    n = rng.randint(1, 10); edges = []
    for node in range(2, n + 1):
        edges.append([rng.randint(1, node - 1), node, rng.randint(1, 15)])
    queries = []
    for _ in range(rng.randint(1, 18)):
        if edges and rng.randrange(2):
            u, v, _ = rng.choice(edges); queries.append([1, u, v, rng.randint(1, 15)])
        else:
            queries.append([2, rng.randint(1, n)])
    return [n, edges, queries]


def kth_palindrome_oracle(args):
    from itertools import permutations
    text, order = args
    half = []
    for char in sorted(set(text)):
        half.extend([char] * (text.count(char) // 2))
    center = next((char for char in text if text.count(char) % 2), '')
    choices = sorted(set(permutations(half)))
    if order > len(choices):
        return ''
    left = ''.join(choices[order - 1])
    return left + center + left[::-1]


def random_kth_palindrome(rng):
    half = ''.join(rng.choice('abcd') for _ in range(rng.randint(0, 6)))
    center = rng.choice('abcd') if rng.randrange(2) else ''
    return [half + center + half[::-1], rng.randint(1, 30)]


def base_digits(value, base):
    if value == 0:
        return [0]
    result = []
    while value:
        result.append(value % base); value //= base
    return result[::-1]


def nondecreasing_numbers_oracle(args):
    left, right, base = args
    total = 0
    for value in range(int(left), int(right) + 1):
        digits = base_digits(value, base)
        total += all(digits[i] <= digits[i + 1] for i in range(len(digits) - 1))
    return total


def random_nondecreasing_numbers(rng):
    left = rng.randint(1, 180); right = rng.randint(left, min(240, left + 50))
    return [str(left), str(right), rng.randint(2, 10)]


def inversion_threshold_oracle(args):
    nums, needed = args
    differences = sorted(nums[i] - nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > nums[j])
    return differences[needed - 1] if len(differences) >= needed else -1


def random_inversion_threshold(rng):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(1, 12))]
    return [nums, rng.randint(1, len(nums) * (len(nums) - 1) // 2 + 3)]


def instruction_oracle(args):
    instructions, values = args
    index = 0; score = 0; visited = set()
    while 0 <= index < len(values) and index not in visited:
        visited.add(index)
        if instructions[index] == 'add':
            score += values[index]; index += 1
        else:
            index += values[index]
    return score


def random_instruction(rng):
    size = rng.randint(1, 18)
    return [[rng.choice(('add', 'jump')) for _ in range(size)], [rng.randint(-8, 8) for _ in range(size)]]


TREE_DISTANCE = '''def dynamic_root_distances(n, edges, queries):
    graph=[[] for _ in range(n+1)]
    for u,v,weight in edges:graph[u].append((v,weight));graph[v].append((u,weight))
    parent=[0]*(n+1);depth=[0]*(n+1);start=[0]*(n+1);end=[0]*(n+1);edge_weight=[0]*(n+1);timer=0
    stack=[(1,0,0,0)]
    while stack:
        node,par,distance,state=stack.pop()
        if state==0:
            start[node]=timer;timer+=1;parent[node]=par;depth[node]=distance;stack.append((node,par,distance,1))
            for neighbor,weight in reversed(graph[node]):
                if neighbor!=par:edge_weight[neighbor]=weight;stack.append((neighbor,node,distance+weight,0))
        else:end[node]=timer-1
    bit=[0]*(n+2)
    def add(index,delta):
        index+=1
        while index<len(bit):bit[index]+=delta;index+=index&-index
    def prefix(index):
        index+=1;total=0
        while index:total+=bit[index];index-=index&-index
        return total
    answer=[]
    for query in queries:
        if query[0]==1:
            u,v,weight=query[1:];child=v if parent[v]==u else u;delta=weight-edge_weight[child];edge_weight[child]=weight
            add(start[child],delta);add(end[child]+1,-delta)
        else:
            node=query[1];answer.append(depth[node]+prefix(start[node]))
    return answer
'''


KTH_PALINDROME = '''def kth_palindromic_rearrangement(s, k):
    from collections import Counter
    from math import comb
    counts=Counter(s);middle=next((char for char,count in counts.items() if count%2),'')
    half=[counts[chr(code)]//2 for code in range(97,123)];remaining=sum(half)
    def ways(cap):
        total=1;used=0
        for count in half:
            if count:
                total*=comb(used+count,count);used+=count
                if total>=cap:return cap
        return total
    left=[]
    if ways(k)<k:return ''
    while remaining:
        chosen=False
        for index,count in enumerate(half):
            if not count:continue
            half[index]-=1;amount=ways(k)
            if amount>=k:
                left.append(chr(97+index));remaining-=1;chosen=True;break
            k-=amount;half[index]+=1
        if not chosen:return ''
    first=''.join(left)
    return first+middle+first[::-1]
'''


NONDECREASING = '''def count_nondecreasing_base_digits(l, r, b):
    from functools import lru_cache
    modulo=1000000007
    def count(bound):
        value=int(bound);digits=[]
        if value==0:digits=[0]
        while value:digits.append(value%b);value//=b
        digits=digits[::-1]
        @lru_cache(None)
        def solve(position,last,started,tight):
            if position==len(digits):return 1
            limit=digits[position] if tight else b-1;total=0
            for digit in range(limit+1):
                next_tight=tight and digit==limit
                if not started and digit==0:total+=solve(position+1,0,False,next_tight)
                elif not started or digit>=last:total+=solve(position+1,digit,True,next_tight)
            return total%modulo
        return solve(0,0,False,True)
    return (count(r)-count(str(int(l)-1)))%modulo
'''


INVERSION_THRESHOLD = '''def minimum_inversion_threshold(nums, k):
    values=sorted(set(nums));size=len(values)
    def count(threshold):
        from bisect import bisect_right
        bit=[0]*(size+1);total=0
        def prefix(index):
            result=0
            while index:result+=bit[index];index-=index&-index
            return result
        for value in nums:
            low=bisect_right(values,value);high=bisect_right(values,value+threshold)
            total+=prefix(high)-prefix(low)
            index=low
            while index<=size:bit[index]+=1;index+=index&-index
        return total
    high=max(nums)-min(nums)
    if count(high)<k:return -1
    low=1
    while low<high:
        middle=(low+high)//2
        if count(middle)>=k:high=middle
        else:low=middle+1
    return low
'''


INSTRUCTIONS = '''def calculate_instruction_score(instructions, values):
    visited=set();index=0;score=0
    while 0<=index<len(values) and index not in visited:
        visited.add(index)
        if instructions[index]=='add':score+=values[index];index+=1
        else:index+=values[index]
    return score
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


TREE_CASES=[list(case) for case in [
    (2,[[1,2,7]],[[2,2],[1,1,2,4],[2,2]]),(3,[[1,2,2],[1,3,4]],[[2,1],[2,3],[1,1,3,7],[2,2],[2,3]]),
    (1,[],[[2,1]]),(4,[[1,2,2],[2,3,1],[3,4,5]],[[2,4],[2,3],[1,2,3,3],[2,2],[2,3]]),
    (5,[[1,2,1],[1,3,2],[2,4,3],[2,5,4]],[[2,4],[1,1,2,9],[2,4],[2,3]]),
    (3,[[1,2,5],[2,3,6]],[[1,2,1,2],[2,3],[1,2,3,1],[2,3]]),
    (2,[[1,2,1]],[[1,2,1,8],[1,1,2,3],[2,2]]),(4,[[4,2,4],[2,1,3],[2,3,5]],[[2,4],[1,4,2,1],[2,4]]),
    (6,[[1,2,2],[1,3,3],[2,4,4],[2,5,5],[3,6,6]],[[2,5],[2,6],[1,2,5,1],[2,5]]),
    (3,[[3,1,9],[2,3,8]],[[2,2],[1,3,2,2],[2,2]]),(5,[[1,2,1],[2,3,1],[3,4,1],[4,5,1]],[[2,5],[1,3,4,10],[2,5]]),
    (4,[[1,4,7],[4,2,2],[4,3,3]],[[2,2],[2,3],[1,1,4,1],[2,2]]),(2,[[2,1,10]],[[2,1],[2,2]]),
    (7,[[1,2,1],[1,3,1],[2,4,1],[2,5,1],[3,6,1],[3,7,1]],[[1,2,5,5],[2,5],[2,7]])
]]
PAL_CASES=[[s,k] for s,k in [('abba',2),('aa',2),('bacab',1),('z',1),('a',2),('aabb',1),('aabb',3),('abcba',2),('aabbcc',4),('aaaabbbb',5),('racecar',1),('noon',2),('zzxyxzz',3),('aabbccddee',20)]]
DIGIT_CASES=[[l,r,b] for l,r,b in [('23','28',8),('2','7',2),('1','1',10),('1','20',10),('8','15',2),('10','99',10),('1','100',3),('50','120',7),('99','111',10),('1','255',16 if False else 8),('300','360',6),('5','80',4),('1000','1100',10),('1','500',5)]]
THRESHOLD_CASES=[[nums,k] for nums,k in [([1,2,3,4,3,2,1],7),([10,9,9,9,1],4),([1],1),([1,2,3],1),([3,2,1],1),([3,2,1],3),([5,5,5],1),([4,1,3,2],2),([100,1],1),([2,1,2,1],3),([9,7,5,3],5),([1,10,2,9,3],4),([6,1,5,2,4,3],8),([8,3,7,4,6,5],6)]]
INSTRUCTION_CASES=[[instructions,values] for instructions,values in [
    (['jump','add','add','jump','add','jump'],[2,1,3,1,-2,-3]),(['jump','add','add'],[3,1,1]),(['jump'],[0]),
    (['add'],[5]),(['add','add'],[-2,3]),(['jump','add'],[-1,4]),(['add','jump'],[1,-1]),
    (['jump','add','jump'],[1,2,-2]),(['add','add','jump'],[3,4,5]),(['jump','jump','add'],[2,-1,7]),
    (['add','jump','add','jump'],[2,2,5,-3]),(['jump','add','add'],[-2,10,20]),(['add','jump','add'],[-5,0,9]),
    (['jump','add','jump','add','add'],[3,4,2,6,8])
]]


BATCH={
3515:entry('dynamic_root_distances',[('n','int'),('edges','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['trees','fenwick trees','euler tours'],['edges form a weighted undirected tree rooted at node 1 with up to 100,000 nodes.','An update [1,u,v,w] changes one existing edge weight; a query [2,x] asks for the current root-to-x distance.','Return answers for distance queries in their original order.'],[([2,[[1,2,7]],[[2,2],[1,1,2,4],[2,2]]],'Node two is first distance seven; updating its only edge changes the next answer to four.'),([3,[[1,2,2],[1,3,4]],[[2,1],[2,3],[1,1,3,7],[2,3]]],'The root has distance zero, and updating edge 1-3 changes only node three’s distance.')],TREE_CASES,TREE_DISTANCE,[TREE_DISTANCE.replace('add(end[child]+1,-delta)','pass'),TREE_DISTANCE.replace('depth[node]+prefix(start[node])','prefix(start[node])')],['Starts each subtree update but never ends it, so later unrelated Euler positions inherit the change.','Returns only accumulated updates and omits every original root distance.'],tree_distance_oracle,random_tree_distance,lesson('Changing a parent edge shifts the distance of every node in exactly one rooted subtree by the same delta.','Euler-tour each subtree into a contiguous interval, then use Fenwick range-add and point-query updates.','Compute parent, base distance, and entry/exit times; range-add each edge delta to its child subtree and point-query requested nodes.','Euler intervals contain exactly the descendants whose paths use the updated edge, so base distance plus accumulated deltas is current.'),'O((n+q) log n)','O(n)',8),
3518:entry('kth_palindromic_rearrangement',[('s','str'),('k','int')],'str',['strings','combinatorics','greedy'],['s is a lowercase palindrome of length up to 10,000; k is one-based and at most 1,000,000.','Distinct rearrangements producing the same palindrome count once.','Return the k-th lexicographically smallest palindromic rearrangement, or an empty string when fewer than k exist.'],[(['abba',2],'The ordered choices are abba then baab, so the second is baab.'),(['aa',2],'Only aa exists, so there is no second distinct palindrome.')],PAL_CASES,KTH_PALINDROME,[KTH_PALINDROME.replace('for index,count in enumerate(half):','for index,count in reversed(list(enumerate(half))):'),KTH_PALINDROME.replace('if amount>=k:','if amount>k:')],['Tries left-half characters from largest to smallest, reversing lexicographic order.','Skips a block when its size equals k even though the desired arrangement is inside that block.'],kth_palindrome_oracle,random_kth_palindrome,lesson('Only the left half needs ranking; its mirrored half and the optional center are forced.','Construct the left half greedily, counting capped multiset permutations for each possible next character.','Temporarily consume each letter in ascending order; keep it if its completion block contains k, otherwise subtract that block.','Lexicographic permutations form consecutive prefix blocks, so block counting selects exactly the k-th distinct half without enumerating all arrangements.'),'O(n * alphabet^2)','O(alphabet+n)',8),
3519:entry('count_nondecreasing_base_digits',[('l','str'),('r','str'),('b','int')],'int',['digit dynamic programming','strings','number bases'],['l and r are decimal strings of up to 100 digits with 1 <= l <= r; 2 <= b <= 10.','A number qualifies when its base-b digits never decrease from left to right.','Return the inclusive-range count modulo 1,000,000,007.'],[(['23','28',8],'In base eight the range is 27 through 34; only 27, 33, and 34 qualify.'),(['2','7',2],'The qualifying binary representations are 11 and 111, giving two.')],DIGIT_CASES,NONDECREASING,[NONDECREASING.replace('digit>=last','digit>last'),NONDECREASING.replace("count(str(int(l)-1))","count(l)")],['Requires strictly increasing digits and wrongly rejects repeated digits such as 11.','Subtracts the count through l instead of l-1, turning the inclusive range into an exclusive one.'],nondecreasing_numbers_oracle,random_nondecreasing_numbers,lesson('Counting up to a bound needs only the previous chosen digit, whether a nonzero digit has started, and whether the prefix is tight.','Convert the decimal bound to base b, then use digit DP and subtract counts through l-1 from counts through r.','At each position try digits up to the tight limit, allowing leading zeros or digits at least the previous started digit.','The state captures exactly the prefix restrictions; every qualifying representation follows one path and inclusion-exclusion makes the range inclusive.'),'O(log_b(r) * b^2)','O(log_b(r) * b)',8),
3520:entry('minimum_inversion_threshold',[('nums','list[int]'),('k','int')],'int',['arrays','binary search','fenwick trees'],['nums has up to 10,000 positive integers and k is positive.','A qualifying inversion has i<j, nums[i]>nums[j], and difference at most the chosen threshold.','Return the smallest threshold producing at least k pairs, or -1 when the array has fewer than k inversions.'],[([[1,2,3,4,3,2,1],7],'Threshold two includes eight inversions, while threshold one includes fewer than seven.'),([[10,9,9,9,1],4],'Three difference-one inversions are insufficient; threshold eight also includes the 9-to-1 pairs.')],THRESHOLD_CASES,INVERSION_THRESHOLD,[INVERSION_THRESHOLD.replace('prefix(high)-prefix(low)','prefix(high)-prefix(max(0,low-1))'),INVERSION_THRESHOLD.replace('value+threshold','value+threshold-1')],['Includes equal-valued earlier elements even though inversions require strict inequality.','Counts only differences strictly below the threshold and loses boundary pairs.'],inversion_threshold_oracle,random_inversion_threshold,lesson('The number of inversions whose difference is at most x is monotone in x, enabling binary search.','For each candidate x, scan left to right and use a Fenwick tree to count prior values in (value, value+x].','Reject when even the maximum difference has fewer than k pairs; otherwise binary-search the first sufficient x.','Fenwick range counts enforce index order and value bounds, while monotonicity proves the first sufficient threshold is minimal.'),'O(n log n log V)','O(n)',7),
3522:entry('calculate_instruction_score',[('instructions','list[str]'),('values','list[int]')],'int',['arrays','simulation','hash sets'],['instructions and values have equal length up to 100,000.','At add, add the aligned value and advance one; at jump, move by the aligned signed offset without changing score.','Stop before executing an out-of-bounds or previously executed index, and return the score.'],[([['jump','add','add','jump','add','jump'],[2,1,3,1,-2,-3]],'The path 0,2,3,4,5 scores three then minus two before jumping back to visited index two.'),([['jump','add','add'],[3,1,1]],'The first jump lands just beyond the array, so the score stays zero.')],INSTRUCTION_CASES,INSTRUCTIONS,[INSTRUCTIONS.replace("if instructions[index]=='add'","if instructions[index]=='jump'"),INSTRUCTIONS.replace('index+=values[index]','index=values[index]')],['Treats jump instructions as additions and add instructions as jumps.','Interprets a jump value as an absolute index rather than a relative offset.'],instruction_oracle,random_instruction,lesson('The process is deterministic, so the first repeated index begins a loop and must stop the simulation.','Track executed indices in a set and apply exactly one rule at each new in-bounds position.','While the index is valid and unseen, mark it; either add and increment or jump by the signed offset.','Each instruction executes at most once, and the loop condition matches both specified stopping conditions.'),'O(n)','O(n)',5),
}
