"""Top subarray values, frequency groups, stair costs, removed walks, and swap components."""
from collections import Counter
from itertools import permutations, product
from .import_batch_055 import entry


def subarray_oracle(args):
    nums,k=args;values=[]
    for left in range(len(nums)):
        low=high=nums[left]
        for right in range(left,len(nums)):
            low=min(low,nums[right]);high=max(high,nums[right]);values.append(high-low)
    return sum(sorted(values,reverse=True)[:k])

def random_subarray(rng):
    n=rng.randint(1,8);return [[rng.randint(0,20) for _ in range(n)],rng.randint(1,n*(n+1)//2)]

def frequency_oracle(args):
    counts=Counter(args[0]);frequencies=set(counts.values())
    chosen=max(frequencies,key=lambda frequency:(sum(value==frequency for value in counts.values()),frequency))
    return ''.join(sorted(character for character,value in counts.items() if value==chosen))

def random_frequency(rng):return [''.join(chr(97+rng.randrange(8)) for _ in range(rng.randint(1,30)))]

def stairs_oracle(args):
    n,costs=args
    def visit(step):
        if step==n:return 0
        return min(costs[nxt-1]+(nxt-step)**2+visit(nxt) for nxt in range(step+1,min(n,step+3)+1))
    return visit(0)

def random_stairs(rng):
    n=rng.randint(1,9);return [n,[rng.randint(1,20) for _ in range(n)]]

def point_oracle(args):
    s,k=args;points=set();moves={'U':(0,1),'D':(0,-1),'L':(-1,0),'R':(1,0)}
    for start in range(len(s)-k+1):
        x=y=0
        for character in s[:start]+s[start+k:]:
            dx,dy=moves[character];x+=dx;y+=dy
        points.add((x,y))
    return len(points)

def random_point(rng):
    n=rng.randint(1,18);return [''.join(rng.choice('UDLR') for _ in range(n)),rng.randint(1,n)]

def swap_oracle(args):
    nums,swaps=args;n=len(nums);adj=[[] for _ in nums]
    for a,b in swaps:adj[a].append(b);adj[b].append(a)
    seen=set();groups=[]
    for start in range(n):
        if start in seen:continue
        stack=[start];seen.add(start);group=[]
        while stack:
            node=stack.pop();group.append(node)
            for nxt in adj[node]:
                if nxt not in seen:seen.add(nxt);stack.append(nxt)
        groups.append(group)
    arrangements=[list(set(permutations([nums[index] for index in group]))) for group in groups]
    answer=None
    for choices in product(*arrangements):
        candidate=nums[:]
        for group,values in zip(groups,choices):
            for index,value in zip(group,values):candidate[index]=value
        score=sum(value if index%2==0 else -value for index,value in enumerate(candidate))
        answer=score if answer is None else max(answer,score)
    return answer

def random_swap(rng):
    n=rng.randint(2,7);nums=[rng.randint(1,12) for _ in range(n)];pairs=[]
    for a in range(n):
        for b in range(a+1,n):
            if rng.random()<.25:pairs.append([a,b])
    return [nums,pairs]


SUBARRAY='''def maximum_total_subarray_value(nums,k):
    import heapq
    n=len(nums);levels=n.bit_length();logs=[0]*(n+1)
    for size in range(2,n+1):logs[size]=logs[size//2]+1
    maximum=[nums[:]];minimum=[nums[:]]
    for level in range(1,levels):
        span=1<<(level-1);width=n-(1<<level)+1
        maximum.append([max(maximum[level-1][i],maximum[level-1][i+span]) for i in range(width)])
        minimum.append([min(minimum[level-1][i],minimum[level-1][i+span]) for i in range(width)])
    def value(left,right):
        level=logs[right-left+1];start=right-(1<<level)+1
        return max(maximum[level][left],maximum[level][start])-min(minimum[level][left],minimum[level][start])
    heap=[(-value(left,n-1),left,n-1) for left in range(n)];heapq.heapify(heap);answer=0
    for _ in range(k):
        negative,left,right=heapq.heappop(heap);answer-=negative
        if right>left:heapq.heappush(heap,(-value(left,right-1),left,right-1))
    return answer
'''

FREQUENCY='''def majority_frequency_characters(s):
    from collections import Counter,defaultdict
    groups=defaultdict(list)
    for character,frequency in Counter(s).items():groups[frequency].append(character)
    chosen=max(groups,key=lambda frequency:(len(groups[frequency]),frequency))
    return ''.join(sorted(groups[chosen]))
'''

STAIRS='''def minimum_stair_climbing_cost(n,costs):
    best=[0]+[float('inf')]*n
    for step in range(1,n+1):
        best[step]=costs[step-1]+min(best[previous]+(step-previous)**2 for previous in range(max(0,step-3),step))
    return best[n]
'''

POINTS='''def distinct_points_after_removal(s,k):
    moves={'U':(0,1),'D':(0,-1),'L':(-1,0),'R':(1,0)};prefix=[(0,0)]
    for character in s:
        dx,dy=moves[character];x,y=prefix[-1];prefix.append((x+dx,y+dy))
    total_x,total_y=prefix[-1];points=set()
    for end in range(k,len(s)+1):
        before_x,before_y=prefix[end-k];after_x,after_y=prefix[end]
        points.add((total_x-after_x+before_x,total_y-after_y+before_y))
    return len(points)
'''

SWAPS='''def maximum_alternating_sum_with_swaps(nums,swaps):
    parent=list(range(len(nums)))
    def find(node):
        while parent[node]!=node:
            parent[node]=parent[parent[node]];node=parent[node]
        return node
    for first,second in swaps:
        a=find(first);b=find(second)
        if a!=b:parent[b]=a
    groups={}
    for index,value in enumerate(nums):groups.setdefault(find(index),[]).append((index,value))
    answer=0
    for members in groups.values():
        values=sorted(value for _,value in members);positive=sum(index%2==0 for index,_ in members)
        answer+=sum(values[-positive:]) if positive else 0
        answer-=sum(values[:len(values)-positive])
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

A_CASES=[[a,k] for a,k in (([7],1),([1,2],1),([1,2],3),([2,2,2],6),([5,1,4],3),([0,10,0],4),([4,2,5,1],4),([1,9,2,8],5),([3,1,6,2,5],7),([0,1,0,1,0],10),([10,0,9,1,8,2],8),([6,5,4,3,2,1],12))]
F_CASES=[[s] for s in ('a','aabbc','abbccc','aabbccddd','zzzyyyxxw','abcabcde','mississippi','qwertyqwerty','aaaabbbbccccdd','abacabad','xyyzzzwwww','leetcodepractice')]
T_CASES=[[len(c),c] for c in ([7],[1,1],[10,1],[2,9,1],[5,1,6,3],[3,3,3,3,3],[9,8,3],[1,10,1,10,1,10],[4,2,7,1,8,3],[20,1,20,1,20,1,20],[6,5,4,3,2,1,9],[2,8,5,1,7,3,9,4])]
P_CASES=[[s,k] for s,k in (('U',1),('UU',1),('UD',1),('UDLR',3),('RRLL',2),('URDL',1),('LLLLR',3),('UDUDUD',2),('RULDRU',3),('UUURRRDDD',4),('LRLRUDUD',5),('RUDLURDLUR',2))]
W_CASES=[[a,b] for a,b in (([1,2],[]),([1,2],[[0,1]]),([1,2,3],[[0,1]]),([3,1,2],[[0,2],[1,2]]),([5,4,3,2],[[0,2],[1,3]]),([1,9,2,8],[[0,1],[2,3]]),([7,1,5,3],[[0,3]]),([2,2,9,1],[[0,1],[1,2]]),([10,1,9,2,8],[[0,2],[2,4]]),([1,6,2,5,3,4],[[0,1],[1,2],[3,4],[4,5]]),([8,7,6,5,4,3],[[0,5],[1,4],[2,3]]),([4,1,7,2,9,3,6],[[0,1],[1,2],[2,3],[4,5]]))]

BATCH={
3691:entry('maximum_total_subarray_value',[('nums','list[int]'),('k','int')],'int',['arrays','heaps','range queries'],['One to 50,000 nonnegative integers, each at most one billion.','Choose exactly k distinct nonempty subarrays; overlapping is allowed.','k is at most 100,000 and at most n(n+1)/2.'],[([[1,3,2],2],'The ranges [1,3] and [1,3,2] each contribute two, totaling four.'),([[4,2,5,1],3],'Three different ranges each attain value four, totaling twelve.')],A_CASES,SUBARRAY,[SUBARRAY.replace('for _ in range(k):','for _ in range(k-1):'),SUBARRAY.replace('answer-=negative','answer+=negative')],['Selects only k minus one subarrays.','Adds the negative heap key instead of the subarray value.'],subarray_oracle,random_subarray,lesson('For a fixed left endpoint, extending the right endpoint never decreases max minus min.','Each left endpoint forms a sorted stream of values; merge the n streams with a max heap.','Use static range minimum/maximum queries, seed each stream at right=n-1, and push its preceding right endpoint after every pop.','The heap always exposes the largest unchosen head, so k pops are exactly the globally largest k distinct subarray values.'),'O(n log n + k log n)','O(n log n)',8),
3692:entry('majority_frequency_characters',[('s','str')],'str',['strings','hash maps','counting'],['s contains one to 100 lowercase English letters.','Group distinct letters by their occurrence count.','Choose the largest group, breaking ties toward the higher occurrence count; return its letters alphabetically.'],[(['aaabbbccdddde'],'Frequency three contains a and b, more letters than any other group, so return ab.'),(['pfpfgi'],'Frequencies one and two each contain two letters; frequency two wins the tie, so return fp.')],F_CASES,FREQUENCY,[FREQUENCY.replace('frequency:(len(groups[frequency]),frequency)','frequency:(len(groups[frequency]),-frequency)'),FREQUENCY.replace('len(groups[frequency])','sum(ord(c) for c in groups[frequency])')],['Breaks tied group sizes toward the lower frequency.','Chooses by character-code total rather than number of distinct characters.'],frequency_oracle,random_frequency,lesson('Count each character first, then invert that mapping into frequency groups.','Compare groups by the pair (number of distinct letters, frequency).','A maximum pair implements both the main rule and the required tie-break; sorting only normalizes the returned order.','Every letter belongs to exactly one frequency group, so comparing those group keys examines every valid answer.'),'O(n + alphabet log alphabet)','O(alphabet)',3),
3693:entry('minimum_stair_climbing_cost',[('n','int'),('costs','list[int]')],'int',['arrays','dynamic programming'],['n equals the length of costs and is at most 100,000.','Landing on step i pays costs[i-1]; step zero is free.','Each jump advances one, two, or three steps and additionally costs the square of its length.'],[([4,[1,2,3,4]],'An optimal sequence 0→1→2→4 costs 2+3+8=13.'),([4,[5,1,6,2]],'Jumps 0→2→4 cost 1+4 plus 2+4, totaling eleven.')],T_CASES,STAIRS,[STAIRS.replace('max(0,step-3)','max(0,step-2)'),STAIRS.replace('(step-previous)**2','step-previous')],['Forbids legal jumps of length three.','Charges jump length instead of its square.'],stairs_oracle,random_stairs,lesson('Only the cheapest cost of reaching each earlier step matters.','For step i, try the at most three predecessors i-1, i-2, and i-3.','Add the landing cost and squared jump length to each predecessor state and keep the minimum.','Every valid path reaches i from exactly one of those predecessors, so the recurrence is exhaustive and optimal.'),'O(n)','O(n)',5),
3694:entry('distinct_points_after_removal',[('s','str'),('k','int')],'int',['strings','prefix sums','sliding windows'],['s has one to 100,000 moves drawn from U, D, L, and R.','Remove exactly one contiguous substring of length k.','Count distinct final coordinates over every possible removal.'],[(['LUL',1],'The three removals end at (-1,1), (-2,0), and (-1,1), giving two distinct points.'),(['UDLR',4],'Removing the entire walk leaves the origin as the only endpoint.')],P_CASES,POINTS,[POINTS.replace('range(k,len(s)+1)','range(k,len(s))'),POINTS.replace('total_x-after_x+before_x','total_x-after_x-before_x')],['Skips the removal window ending at the final character.','Subtracts rather than restores the displacement before the removed window.'],point_oracle,random_point,lesson('The endpoint after removal equals the full-walk endpoint minus the removed window displacement.','Store prefix x/y coordinates so every window displacement is available in constant time.','For each window end, subtract prefix[end]-prefix[end-k] from the total and add the resulting coordinate to a set.','This formula is exactly the displacement of all retained moves, and the set removes duplicate endpoints.'),'O(n)','O(n)',5),
3695:entry('maximum_alternating_sum_with_swaps',[('nums','list[int]'),('swaps','list[list[int]]')],'int',['arrays','union find','greedy','sorting'],['nums has two to 100,000 positive integers.','Each allowed index pair may be swapped any number of times and in any order.','Maximize the sum at even indices minus the sum at odd indices.'],[([[1,2,3],[[0,2],[1,2]]],'All indices connect, so place the two largest values at even indices for a maximum of four.'),([[1,2,3],[[1,2]]],'Only indices one and two exchange; keeping the original order gives the maximum two.')],W_CASES,SWAPS,[SWAPS.replace('values=sorted(value for _,value in members)','values=sorted((value for _,value in members),reverse=True)'),SWAPS.replace('index%2==0','index%2==1')],['Sorts each component in the opposite direction before assigning signs.','Counts negative rather than positive positions in each component.'],swap_oracle,random_swap,lesson('Unlimited swaps along graph edges permit any permutation inside each connected component.','For each component, place its largest values in positive even-index slots and its smallest values in negative odd-index slots.','Use union-find to build components, sort their values, and sum the largest positive-slot count minus the rest.','An exchange argument shows that assigning a larger value to a positive slot never hurts; components are independent, so their optima add.'),'O((n+m) α(n) + n log n)','O(n)',8),
}
