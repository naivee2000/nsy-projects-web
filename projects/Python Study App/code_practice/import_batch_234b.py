"""No-zero sums, unequal endpoints, Fibonacci runs, point partitions, and transactions."""
from itertools import product
from .import_batch_055 import entry


def nozero_oracle(args):
    n=args[0]
    return sum('0' not in str(first) and '0' not in str(n-first) for first in range(1,n))

def random_nozero(rng):return [rng.randint(2,500)]

def distance_oracle(args):
    words=args[0];answer=0
    for first in range(len(words)):
        for second in range(first+1,len(words)):
            if words[first]!=words[second]:answer=max(answer,second-first+1)
    return answer

def random_distance(rng):
    pool=['a','b','c','aa','ab'];return [[rng.choice(pool) for _ in range(rng.randint(1,15))]]

def fibonacci_oracle(args):
    nums=args[0];answer=1
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            if all(nums[index]==nums[index-1]+nums[index-2] for index in range(left+2,right+1)):
                answer=max(answer,right-left+1)
    return answer

def random_fibonacci(rng):return [[rng.randint(1,30) for _ in range(rng.randint(3,15))]]

def partition_oracle(args):
    points=args[0];n=len(points)
    if n==2:return 0
    answer=0
    for mask in range(1,1<<(n-1)):
        distances=[]
        for i in range(n):
            for j in range(i+1,n):
                if (mask>>i&1)==(mask>>j&1):
                    distances.append(abs(points[i][0]-points[j][0])+abs(points[i][1]-points[j][1]))
        if distances:answer=max(answer,min(distances))
    return answer

def random_partition(rng):
    n=rng.randint(2,9);return [[[rng.randint(-8,8),rng.randint(-8,8)] for _ in range(n)]]

def transaction_oracle(args):
    balances={0:0}
    for value in args[0]:
        updated=dict(balances)
        for balance,count in balances.items():
            if balance+value>=0:updated[balance+value]=max(updated.get(balance+value,-1),count+1)
        balances=updated
    return max(balances.values())

def random_transaction(rng):return [[rng.randint(-12,12) for _ in range(rng.randint(1,13))]]


NOZERO='''def count_no_zero_pairs(n):
    digits=list(map(int,str(n)))[::-1]+[0];dp={(0,1,1):1}
    for position,target in enumerate(digits):
        next_dp={}
        for (carry,alive_a,alive_b),ways in dp.items():
            choices_a=[(digit,1) for digit in range(1,10)]+([(0,0)] if alive_a and position>0 else []) if alive_a else [(0,0)]
            choices_b=[(digit,1) for digit in range(1,10)]+([(0,0)] if alive_b and position>0 else []) if alive_b else [(0,0)]
            for digit_a,next_a in choices_a:
                for digit_b,next_b in choices_b:
                    total=digit_a+digit_b+carry
                    if total%10==target:
                        state=(total//10,next_a,next_b);next_dp[state]=next_dp.get(state,0)+ways
        dp=next_dp
    return dp.get((0,0,0),0)
'''

DISTANCE='''def maximum_unequal_word_distance(words):
    answer=0;n=len(words)
    for index,word in enumerate(words):
        if word!=words[0]:answer=max(answer,index+1)
        if word!=words[-1]:answer=max(answer,n-index)
    return answer
'''

FIBONACCI='''def longest_fibonacci_subarray(nums):
    if len(nums)<3:return len(nums)
    answer=current=2
    for index in range(2,len(nums)):
        if nums[index]==nums[index-1]+nums[index-2]:current+=1;answer=max(answer,current)
        else:current=2
    return answer
'''

PARTITION='''def maximum_partition_factor(points):
    if len(points)==2:return 0
    distances=sorted({abs(a[0]-b[0])+abs(a[1]-b[1]) for i,a in enumerate(points) for b in points[i+1:]})
    def possible(limit):
        colors=[-1]*len(points)
        for start in range(len(points)):
            if colors[start]!=-1:continue
            colors[start]=0;stack=[start]
            while stack:
                node=stack.pop()
                for other in range(len(points)):
                    if other==node:continue
                    distance=abs(points[node][0]-points[other][0])+abs(points[node][1]-points[other][1])
                    if distance>=limit:continue
                    if colors[other]==colors[node]:return False
                    if colors[other]==-1:colors[other]=colors[node]^1;stack.append(other)
        return True
    low=0;high=len(distances)-1;answer=0
    while low<=high:
        middle=(low+high)//2
        if possible(distances[middle]):answer=distances[middle];low=middle+1
        else:high=middle-1
    return answer
'''

TRANSACTIONS='''def maximum_safe_transactions(transactions):
    import heapq
    selected=[];balance=0
    for value in transactions:
        balance+=value;heapq.heappush(selected,value)
        while balance<0:
            removed=heapq.heappop(selected);balance-=removed
    return len(selected)
'''

def lesson(a,b,c,d):return [a,b,c,d]

N_CASES=[[n] for n in (3,4,9,10,12,20,25,99,100,101,250,499)]
D_CASES=[[[*words]] for words in (['a'],['a','a'],['a','b'],['a','b','a'],['x','x','y','x'],['a','b','c','a','b'],['z','z','z'],['ab','ab','cd','ab','ef'],['a','b','b','b','a','c'],['one','two','one','two'],['q','q','q','r'],['aa','ab','aa','aa','ab','aa'])]
F_CASES=[[[*values]] for values in ([1,2,3],[1,1,2,3,5],[2,2,4,6,10],[1,2,4],[5,2,7,9,17],[3,3,6,9,15,24],[1,1,1],[8,13,21,34,55,2],[4,7,11,18,29],[9,1,10,11,21,32],[2,3,5,8,13,21,34],[100,100,200,300,500,1])]
P_CASES=[[[list(point) for point in values]] for values in (((0,0),(1,1)),((0,0),(0,2),(10,0)),((0,0),(0,3),(3,0),(3,3)),((0,0),(1,0),(2,0)),((0,0),(0,0),(3,3)),((-1,-1),(1,1),(2,-2)),((0,0),(2,1),(4,0),(2,-1)),((1,2),(3,4),(5,6),(7,8)),((-3,0),(0,3),(3,0),(0,-3),(0,0)),((0,0),(1,2),(3,1),(4,4),(7,0)),((2,2),(2,-2),(-2,2),(-2,-2),(0,0)),((0,1),(1,0),(0,-1),(-1,0),(3,3),(4,4)))]
T_CASES=[[[*values]] for values in ([1],[-1],[0],[2,-1],[1,-2,2],[5,-10,4,3],[3,-2,3,-2,1,-2],[-1,-2,-4],[4,-5,-2,6,-1],[10,-9,-2,-5],[2,-3,1,-1,4,-6,2],[0,-1,2,-2,3,-3])]

BATCH={
3704:entry('count_no_zero_pairs',[('n','int')],'int',['dynamic programming','math','digit dp'],['n is between two and 10^15.','Both a and b are positive and their decimal representations contain no zero digit.','Count ordered pairs (a,b) satisfying a+b=n.'],[([2],'Only the ordered pair (1,1) qualifies.'),([11],'Eight ordered pairs from (2,9) through (9,2) qualify; pairs containing ten do not.')],N_CASES,NOZERO,[NOZERO.replace('range(1,10)','range(10)'),NOZERO.replace("return dp.get((0,0,0),0)","return dp.get((0,0,0),0)//2")],['Allows zero as an active decimal digit.','Incorrectly treats the ordered pairs as unordered.'],nozero_oracle,random_nozero,lesson('Process the decimal addition from least significant digit to most significant digit.','Track the carry and whether each addend still has digits; active digits are one through nine, while a number may end after its first digit.','A digit DP tries compatible digit pairs at each position and requires both numbers and the final carry to end together.','The state records exactly the information passed to the next column, so every no-zero ordered addition is counted once.'),'O(log n)','O(1)',8),
3706:entry('maximum_unequal_word_distance',[('words','list[str]')],'int',['arrays','strings'],['words contains up to 100,000 nonempty lowercase strings.','The inclusive distance between indices i and j is |i-j|+1.','Return the maximum distance whose endpoint words differ, or zero if every word is equal.'],[([['leetcode','leetcode','codeforces']],'The first and last words differ, so their inclusive distance is three.'),([['a','b','c','a','a']],'Indices one and four contain different words and have inclusive distance four.')],D_CASES,DISTANCE,[DISTANCE.replace('index+1','index'),DISTANCE.replace('n-index','n-index-1')],['Forgets the inclusive plus one for pairs measured from the first index.','Forgets the inclusive plus one for pairs measured from the last index.'],distance_oracle,random_distance,lesson('At least one endpoint of an optimal unequal pair can be moved to an array boundary.','Compare every word with the first and last words and measure the corresponding inclusive distance.','Take the largest valid first-to-index or index-to-last candidate.','If an optimal pair uses neither boundary, a boundary word must differ from at least one of its endpoint words and yields no shorter a span.'),'O(n)','O(1)',5),
3708:entry('longest_fibonacci_subarray',[('nums','list[int]')],'int',['arrays'],['nums contains three to 100,000 positive integers.','A contiguous subarray is Fibonacci when every element from the third onward equals the previous two summed.','Length-one and length-two subarrays always qualify.'],[([[1,1,1,1,2,3,5,1]],'The run [1,1,2,3,5] has length five.'),([[5,2,7,9,16]],'Every element from the third onward is the sum of its predecessors, so the answer is five.')],F_CASES,FIBONACCI,[FIBONACCI.replace('else:current=2','else:current=1'),FIBONACCI.replace('nums[index-1]+nums[index-2]','nums[index-1]-nums[index-2]')],['Restarts a broken run at length one instead of the final two elements.','Checks a difference recurrence instead of the Fibonacci sum.'],fibonacci_oracle,random_fibonacci,lesson('A failed equality ends only the longer run; its final two values can begin the next candidate.','Scan once while storing the length of the Fibonacci run ending at the current index.','Extend on a valid sum and otherwise reset the run length to two.','The state is exactly the longest valid subarray ending at each position, so its maximum is the global answer.'),'O(n)','O(1)',5),
3710:entry('maximum_partition_factor',[('points','list[list[int]]')],'int',['graphs','binary search','bipartite graphs'],['Two to 500 Cartesian points may contain negative coordinates or duplicates.','Split all points into exactly two nonempty groups.','The factor is the minimum Manhattan distance between points in the same group; a two-point input has factor zero.'],[([[[0,0],[0,2],[2,0],[2,2]]],'Coloring opposite corners together gives within-group distance four.'),([[[0,0],[0,1],[10,0]]],'Putting the first point alone leaves the other pair at Manhattan distance eleven.')],P_CASES,PARTITION,[PARTITION.replace('if distance>=limit:continue','if distance>limit:continue'),PARTITION.replace("abs(points[node][0]-points[other][0])+abs(points[node][1]-points[other][1])","max(abs(points[node][0]-points[other][0]),abs(points[node][1]-points[other][1]))")],['Treats pairs exactly at the candidate factor as conflicts.','Uses Chebyshev distance instead of Manhattan distance in the conflict graph.'],partition_oracle,random_partition,lesson('For a proposed factor d, every pair closer than d must be placed in opposite groups.','Those required separations form a graph; the factor is feasible exactly when that graph is bipartite.','Binary-search the distinct Manhattan distances and test each conflict graph by two-coloring.','A valid coloring produces the split, while an odd conflict cycle proves no two groups can separate every too-close pair.'),'O(n² log n)','O(n²)',8),
3711:entry('maximum_safe_transactions',[('transactions','list[int]')],'int',['arrays','greedy','heaps'],['transactions contains up to 100,000 signed amounts processed in their original order.','Any transaction may be skipped; the running balance starts at zero and may never become negative.','Return the maximum number that can be retained.'],[([[2,-5,3,-1,-2]],'Skipping negative five lets the other four transactions finish with balance two.'),([[-1,-2,-3]],'Every available transaction would immediately make the balance negative, so keep none.')],T_CASES,TRANSACTIONS,[TRANSACTIONS.replace('removed=heapq.heappop(selected);balance-=removed','removed=selected.pop();balance-=removed'),TRANSACTIONS.replace('removed=heapq.heappop(selected);balance-=removed','removed=value;selected.remove(value);heapq.heapify(selected);balance-=removed')],['Removes an arbitrary heap-array tail rather than the most negative selected transaction.','Always rejects the current transaction instead of replacing a worse earlier choice.'],transaction_oracle,random_transaction,lesson('When the balance turns negative, at least one selected transaction must be discarded.','Discarding the most negative selected value restores the most balance while losing only one transaction.','Maintain selected values in a min-heap and repeatedly remove its minimum whenever the balance is negative.','The greedy exchange never leaves less balance than removing any other single choice, preserving the best chance to keep all later transactions.'),'O(n log n)','O(n)',6),
}
