"""Distinct suffixes, divisible triples, binary swaps, alternating deletion, and costs."""
from itertools import combinations
from .import_batch_055 import entry


def distinct_oracle(args):
    values=args[0];operations=0
    while len(values)!=len(set(values)):
        values=values[3:];operations+=1
    return operations

def random_distinct(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,40))]]

def triple_oracle(args):
    return max((sum(items) for items in combinations(args[0],3) if sum(items)%3==0),default=0)

def random_triple(rng):return [[rng.randint(1,100) for _ in range(rng.randint(3,12))]]

def swaps_oracle(args):
    nums,s=args;seen={s};stack=[s];best=0
    while stack:
        state=stack.pop();best=max(best,sum(value for value,bit in zip(nums,state) if bit=='1'))
        for i in range(len(state)-1):
            if state[i:i+2]=='01':
                nxt=state[:i]+'10'+state[i+2:]
                if nxt not in seen:seen.add(nxt);stack.append(nxt)
    return best

def random_swaps(rng):
    n=rng.randint(1,9);return [[rng.randint(1,30) for _ in range(n)],''.join(rng.choice('01') for _ in range(n))]

def remaining_oracle(args):
    values=list(range(1,args[0]+1));left=True
    while len(values)>1:
        if left:values=values[::2]
        else:values=values[(len(values)-1)%2::2]
        left=not left
    return values[0]

def random_remaining(rng):return [rng.randint(1,200)]

def deletion_oracle(args):
    s,cost=args;total=sum(cost)
    return min(total-sum(value for char,value in zip(s,cost) if char==keep) for keep in set(s))

def random_deletion(rng):
    n=rng.randint(1,30);return [''.join(rng.choice('abcd') for _ in range(n)),[rng.randint(1,50) for _ in range(n)]]


DISTINCT='''def minimum_operations_for_distinct(nums):
    seen=set()
    for index in range(len(nums)-1,-1,-1):
        if nums[index] in seen:return index//3+1
        seen.add(nums[index])
    return 0
'''

TRIPLE='''def maximum_divisible_triple_sum(nums):
    groups=[[] for _ in range(3)]
    for value in nums:groups[value%3].append(value)
    for group in groups:group.sort(reverse=True)
    answer=0
    for counts in ((3,0,0),(0,3,0),(0,0,3),(1,1,1)):
        if all(len(groups[r])>=counts[r] for r in range(3)):
            answer=max(answer,sum(sum(groups[r][:counts[r]]) for r in range(3)))
    return answer
'''

TRIPLE_WRONG_1='''def maximum_divisible_triple_sum(nums):
    values=sorted(nums,reverse=True)[:3]
    return sum(values) if sum(values)%3==0 else 0
'''
TRIPLE_WRONG_2='''def maximum_divisible_triple_sum(nums):
    best=0
    for a in range(len(nums)):
        for b in range(a+1,len(nums)):
            if (nums[a]+nums[b])%3==0:best=max(best,nums[a]+nums[b])
    return best
'''

SWAPS='''def maximum_binary_swap_score(nums,s):
    from heapq import heappop,heappush
    available=[];answer=0
    for value,bit in zip(nums,s):
        heappush(available,-value)
        if bit=='1':answer-=heappop(available)
    return answer
'''

SWAPS_WRONG_1='''def maximum_binary_swap_score(nums,s):
    return sum(value for value,bit in zip(nums,s) if bit=='1')
'''
SWAPS_WRONG_2=SWAPS.replace('heappush(available,-value)','heappush(available,value)').replace('answer-=heappop(available)','answer+=heappop(available)')

REMAINING='''def last_alternating_remaining(n):
    first=1;step=1;left=True;length=n
    while length>1:
        if not left and length%2==0:first+=step
        length=(length+1)//2;step*=2;left=not left
    return first
'''

DELETE='''def minimum_equal_character_deletion_cost(s,cost):
    totals={};overall=0
    for char,value in zip(s,cost):totals[char]=totals.get(char,0)+value;overall+=value
    return overall-max(totals.values())
'''

def lesson(a,b,c,d):return [a,b,c,d]

D_CASES=[[[*v]] for v in ([1],[1,2],[1,1],[3,8,3,6,5,8],[1,2,3,4],[1,2,1,3],[1,2,3,1],[5,5,5,5],[1,2,3,4,1,2,3],[9,8,7,9],[1,1,2,2,3,3,4],[4,3,2,1,4,5,6,7],[1,2,3,4,5,6,1],[7,6,5,4,3,2,1,7,8,9])]
T_CASES=[[[*v]] for v in ([1,2,3],[4,2,3,1],[3,6,9],[1,1,1],[2,2,2],[1,2,4],[6,4,3,2,1],[5,8,11,14],[10,20,30,40],[7,7,8,9],[1,3,5,7,9],[100,99,98,97],[2,5,8,11,14],[6,12,1,2,3],[50,49,48,47,46])]
S_CASES=[[a,b] for a,b in (([5],'0'),([5],'1'),([2,1,5,2,3],'01010'),([10,1],'01'),([1,10],'01'),([4,8,2],'001'),([4,8,2],'101'),([9,1,8,2],'0101'),([1,2,3,4],'1111'),([7,3,9,1,8],'00101'),([2,20,3,19,4,18],'010101'),([5,1,10,2,9],'01100'),([3,30,2,20,1],'00111'),([8,6,7,5,3,0,9],'0101010'))]
R_CASES=[[n] for n in (1,2,3,4,5,6,7,8,9,10,15,16,31,100)]
C_CASES=[[s,c] for s,c in (('a',[5]),('ab',[1,2]),('aa',[4,7]),('aabaac',[1,2,3,4,1,10]),('abc',[10,1,1]),('aba',[5,100,5]),('zzxy',[1,2,8,9]),('abcd',[1,1,1,1]),('bbbaa',[3,4,5,20,1]),('cabca',[8,1,7,2,9]),('xxyyzz',[1,10,2,20,3,30]),('leetcode',[1,2,3,4,5,6,7,8]),('ababab',[6,5,4,3,2,1]),('mississippi',[1,2,3,4,5,6,7,8,9,10,11]))]

BATCH={
3779:entry('minimum_operations_for_distinct',[('nums','list[int]')],'int',['arrays','hash maps'],['nums contains between one and 100,000 positive integers.','One operation removes the first three elements, or all remaining elements when fewer than three remain.','Stop as soon as all remaining elements are distinct.'],[([[3,8,3,6,5,8]],'Removing the first three leaves [6,5,8], whose values are distinct, so one operation suffices.'),([[1,2,3,4]],'The original array is already distinct, so no operation is needed.')],D_CASES,DISTINCT,[DISTINCT.replace('index//3+1','(index+1)//3'),DISTINCT.replace('index//3+1','index//3')],['Rounds the required removed prefix down at duplicate index zero.','Omits the operation containing the duplicate boundary.'],distinct_oracle,random_distinct,lesson('After k operations, exactly the suffix beginning at index 3k remains.','Scan backward while maintaining the distinct suffix seen so far.','At the first repeated value at index i, remove through the block containing i: floor(i/3)+1 operations.','Every later suffix is distinct by the scan, while retaining index i preserves its duplicate.'),'O(n)','O(n)',5),
3780:entry('maximum_divisible_triple_sum',[('nums','list[int]')],'int',['arrays','greedy','sorting'],['nums contains 3 to 100,000 positive integers.','Select exactly three distinct positions.','Return the maximum sum divisible by three, or zero if no eligible triple exists.'],[([[4,2,3,1]],'Choosing 4, 3, and 2 produces the maximum divisible sum, nine.'),([[1,1,1]],'The only triple sums to three, which is divisible by three.')],T_CASES,TRIPLE,[TRIPLE_WRONG_1,TRIPLE_WRONG_2],['Checks only the three largest values even when a smaller replacement makes the sum divisible.','Selects only two numbers rather than exactly three.'],triple_oracle,random_triple,lesson('Only each number’s remainder modulo three matters for feasibility.','A valid triple uses remainder counts 3-0-0, 0-3-0, 0-0-3, or 1-1-1.','Sort each remainder group descending and evaluate the four possible patterns.','For a fixed remainder pattern, choosing its largest members maximizes the sum; the patterns exhaust all divisible triples.'),'O(n log n)','O(n)',5),
3781:entry('maximum_binary_swap_score',[('nums','list[int]'),('s','str')],'int',['arrays','strings','greedy','heaps'],['nums and s have equal length up to 100,000 and nums values are positive.','An operation changes an adjacent 01 in s to 10.','Maximize the sum of nums[i] at positions containing one.'],[([[2,1,5,2,3],'01010'],'The two ones can move left without crossing, and the best reachable selected values sum to seven.'),([[10,1],'01'],'Swap 01 to 10 so the selected value becomes ten.')],S_CASES,SWAPS,[SWAPS_WRONG_1,SWAPS_WRONG_2],['Never performs any beneficial swap.','Chooses the smallest available prefix value for each one rather than the largest.'],swaps_oracle,random_swaps,lesson('The kth one may move left across zeros but cannot pass an earlier one.','When scanning a one, it may occupy any still-unused position in the prefix.','Push every prefix value into a max-heap and take the largest whenever a one is encountered.','This greedily assigns each ordered one its best currently reachable unused position; exchanging a smaller choice for the maximum can only improve the score.'),'O(n log n)','O(n)',6),
3782:entry('last_alternating_remaining',[('n','int')],'int',['math','recursion','simulation'],['1≤n≤10^15.','Starting from [1..n], alternately delete every second item counted from the left and then from the right.','The first item counted from either side is kept; return the sole survivor.'],[([8],'Keeping alternating positions from the left, right, then left yields [1,3,5,7], [3,7], and finally 3.'),([5],'The rounds produce [1,3,5], then [1,5], then 1.')],R_CASES,REMAINING,[REMAINING.replace('if not left and length%2==0','if left or length%2==0'),REMAINING.replace('length%2==0','length%2==1')],['Uses the classic variant that deletes the first item from the left instead of keeping it.','Moves the first survivor on odd right-to-left rounds instead of even ones.'],remaining_oracle,random_remaining,lesson('The remaining sequence is always an arithmetic progression described by first, step, and length.','A left round keeps positions 0,2,…; a right round starts at position one only when the current length is even.','Update the first value for that even right round, double the step, and replace length by ceil(length/2).','These state updates exactly describe the retained indices, and logarithmically many rounds reduce the length to one.'),'O(log n)','O(1)',8),
3784:entry('minimum_equal_character_deletion_cost',[('s','str'),('cost','list[int]')],'int',['strings','hash maps','greedy'],['s and cost have equal length up to 100,000.','Deleting s[i] costs cost[i], which is positive.','Delete characters until every remaining character is identical, minimizing total cost.'],[(['aabaac',[1,2,3,4,1,10]],'Keeping c saves cost ten, the largest character total, so deleting all other positions costs eleven.'),(['aba',[5,100,5]],'Keeping b saves cost one hundred, so delete the two a characters for ten.')],C_CASES,DELETE,[DELETE.replace('max(totals.values())','min(totals.values())'),DELETE.replace('totals[char]=totals.get(char,0)+value','totals[char]=totals.get(char,0)+1')],['Keeps the character with the smallest total saved cost.','Chooses by frequency instead of the total deletion cost saved.'],deletion_oracle,random_deletion,lesson('Choosing the final character determines exactly which positions must be deleted.','Compute the total cost and the cost sum belonging to each character.','Keep the character with the largest saved cost and subtract that amount from the total.','Every feasible result keeps one character class, so maximizing saved cost is equivalent to minimizing deleted cost.'),'O(n)','O(k)',5),
}
