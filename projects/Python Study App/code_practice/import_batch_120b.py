"""Second reviewed group of workbook batch 120."""
from functools import lru_cache
from itertools import product
from .import_batch_055 import entry

def moves_o(a):
 target,doubles=a;dist={(1,0):0};queue=[(1,0)]
 for value,used in queue:
  if value==target:return dist[(value,used)]
  for nxt,nu in ((value+1,used),(value*2,used+1)):
   if nxt<=target and nu<=doubles and (nxt,nu) not in dist:dist[(nxt,nu)]=dist[(value,used)]+1;queue.append((nxt,nu))
def questions_o(a):
 questions=a[0]
 def solve(i):return 0 if i>=len(questions) else max(solve(i+1),questions[i][0]+solve(i+questions[i][1]+1))
 return solve(0)
def runtime_o(a):
 n,batteries=a
 return max(t for t in range(sum(batteries)//n+1) if sum(min(x,t) for x in batteries)>=n*t)
def ranges_o(a):
 first,second=a;answer=0
 for left in range(len(first)):
  for right in range(left,len(first)):
   for choices in product((0,1),repeat=right-left+1):
    balance=sum(first[i] if choices[i-left]==0 else -second[i] for i in range(left,right+1))
    answer+=balance==0
 return answer%(10**9+7)
def candy_o(a):
 costs=tuple(a[0]);n=len(costs)
 @lru_cache(None)
 def solve(mask):
  remaining=[i for i in range(n) if mask>>i&1];best=sum(costs[i] for i in remaining)
  for f in remaining:
   paid=[i for i in remaining if i!=f and costs[i]>=costs[f]]
   for x in range(len(paid)):
    for y in range(x+1,len(paid)):best=min(best,costs[paid[x]]+costs[paid[y]]+solve(mask^(1<<f)^(1<<paid[x])^(1<<paid[y])))
  return best
 return solve((1<<n)-1)
def rmoves(r):return [r.randint(1,100),r.randint(0,8)]
def rquestions(r):return [[[r.randint(1,20),r.randint(0,6)] for _ in range(r.randint(1,12))]]
def rruntime(r):
 m=r.randint(1,8);n=r.randint(1,m);return [n,[r.randint(0,20) for _ in range(m)]]
def rranges(r):
 n=r.randint(1,7);return [[r.randint(0,8) for _ in range(n)],[r.randint(0,8) for _ in range(n)]]
def rcandy(r):return [[r.randint(1,20) for _ in range(r.randint(1,7))]]

MOVES='''\
def minimum_target_moves(target,max_doubles):
    moves=0
    while target>1 and max_doubles:
        if target%2:target-=1;moves+=1
        else:target//=2;max_doubles-=1;moves+=1
    return moves+target-1
'''
QUESTIONS='''\
def maximum_brainpower_points(questions):
    dp=[0]*(len(questions)+1)
    for index in range(len(questions)-1,-1,-1):
        points,skip=questions[index];next_index=min(len(questions),index+skip+1)
        dp[index]=max(dp[index+1],points+dp[next_index])
    return dp[0]
'''
RUNTIME='''\
def maximum_computer_runtime(n,batteries):
    low,high=0,sum(batteries)//n
    while low<high:
        middle=(low+high+1)//2
        if sum(min(value,middle) for value in batteries)>=n*middle:low=middle
        else:high=middle-1
    return low
'''
RANGES='''\
def balanced_choice_ranges(nums1,nums2):
    mod=10**9+7;states={};answer=0
    for first,second in zip(nums1,nums2):
        current={}
        current[first]=current.get(first,0)+1
        current[-second]=current.get(-second,0)+1
        for balance,count in states.items():
            current[balance+first]=(current.get(balance+first,0)+count)%mod
            current[balance-second]=(current.get(balance-second,0)+count)%mod
        states=current;answer=(answer+states.get(0,0))%mod
    return answer
'''
CANDY='''\
def minimum_candy_purchase_cost(cost):
    values=sorted(cost,reverse=True)
    return sum(value for index,value in enumerate(values) if index%3!=2)
'''
def L(*x):return list(x)
BATCH={
2139:entry('minimum_target_moves',[('target','int'),('max_doubles','int')],'int',['math','greedy'],['Start at score one; each move increments by one or doubles, with at most max_doubles doublings.','Scores never need to exceed target.','Return the minimum moves to reach target.'],[([5,0],'Without doubling, four increments move from one to five.'),([19,2],'Working backward uses two halvings and the necessary decrements for seven moves.')],[[t,d] for t,d in [(1,0),(1,5),(2,0),(2,1),(3,1),(4,1),(4,2),(5,1),(8,3),(10,1),(10,10),(31,2),(32,5),(100,3)]],MOVES,[MOVES.replace('if target%2','if target%2==0'),MOVES.replace('moves+target-1','moves+target')],['Decrements even targets and halves odd targets, reversing the optimal parity rule.','Adds one unnecessary final increment.'],moves_o,rmoves,L('Reverse the process: decrement odd targets and halve even targets while doublings remain.','A reverse halving replaces the only useful final doubling; an odd target must first lose one increment.','Loop while target>1 and doubles remain, then add target-1 remaining decrements.','Each greedy reverse step is forced or dominates repeated decrements, and after doublings run out only unit moves remain.'),'O(log target+target without doubles)','O(1)',5),
2140:entry('maximum_brainpower_points',[('questions','list[list[int]]')],'int',['arrays','dynamic programming'],['Each question is [points,brainpower] and questions are considered in order.','Solving index i earns points and forces skipping the next brainpower questions; skipping earns nothing and moves one step.','Return the maximum obtainable points.'],[([[[3,2],[4,3],[4,4],[2,5]]],'Solving questions zero and three earns five points, the maximum.'),([[[1,1],[2,2],[3,3],[4,4],[5,5]]],'Skipping to the final question earns five, exceeding any compatible earlier combination.')],[[q] for q in [[[1,0]],[[1,1],[2,0]],[[5,10],[1,0]],[[1,0],[2,0],[3,0]],[[10,1],[1,0],[10,0]],[[3,2],[4,3],[4,4],[2,5]],[[5,0],[1,5],[5,0]],[[2,1],[4,1],[6,1]],[[9,3],[1,0],[1,0],[9,0]],[[1,2],[10,0],[1,0]],[[7,1],[8,0],[9,2],[10,0]],[[100,100],[99,0]],[[4,2],[3,0],[3,0],[4,0]],[[1,1],[1,1],[1,1],[1,1]]]],QUESTIONS,[QUESTIONS.replace('index+skip+1','index+skip'),QUESTIONS.replace('dp[index+1]','dp[index]')],['Skips one fewer question after solving.','Compares against the current uncomputed state instead of the value from skipping.'],questions_o,rquestions,L('The best future score depends only on the next available question index.','Compute backward: choose between skipping to i+1 and solving then jumping to i+brainpower+1.','dp[i]=max(dp[i+1],points+dp[min(n,i+skip+1)]).','These are the two exhaustive first decisions, and backward DP supplies their already-optimal suffix values.'),'O(n)','O(n)',5),
2141:entry('maximum_computer_runtime',[('n','int'),('batteries','list[int]')],'int',['binary search','greedy','resource allocation'],['There are at least n batteries and battery swaps are instantaneous.','One battery powers at most one computer at a time, but its charge may contribute across computers over time.','Return the maximum whole minutes all n computers can run simultaneously.'],[([2,[3,3,3]],'Nine total charge minutes can be shared to keep both computers running for four full minutes.'),([2,[1,1,1,1]],'Four units of charge run two computers for two minutes.')],[[n,b] for n,b in [(1,[1]),(1,[10,20]),(2,[1,1]),(2,[3,3,3]),(3,[1,1,1]),(3,[10,10,3,5]),(2,[100,1]),(4,[4,4,4,4]),(2,[0,10,10]),(3,[2,2,10,10]),(5,[1,2,3,4,5]),(2,[5,5,5,5,5]),(3,[8,1,1,1]),(4,[20,1,1,1,1])]],RUNTIME,[RUNTIME.replace('min(value,middle)','value'),RUNTIME.replace('>=n*middle','>n*middle')],['Lets one oversized battery contribute more than the candidate time to multiple computers.','Rejects exact-capacity schedules that use all available charge.'],runtime_o,rruntime,L('For a candidate time t, each battery can contribute at most t charge because it cannot power multiple computers simultaneously.','Feasibility is sum(min(b,t))>=n*t and is monotone, so binary-search t.','Search zero through total_charge//n for the greatest feasible integer.','The capped-charge condition is necessary and sufficient under free swapping, and monotonicity makes the upper-bound search exact.'),'O(batteries log(total/n))','O(1)',8),
2143:entry('balanced_choice_ranges',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','dynamic programming','hash maps'],['The arrays have equal positive length and contain nonnegative integers.','For each contiguous range, choose at every position either nums1 value for the first sum or nums2 value for the second sum.','Count choices whose two sums are equal, modulo 1000000007; different ranges or choices count separately.'],[([[1,2,5],[2,6,3]],'Exactly three range-and-choice combinations balance the two selected sums.'),([[0,0],[0,0]],'Every nonempty range and every binary choice balances, totaling eight.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([0],[0]),([1,2],[2,1]),([0,0],[0,0]),([1,1],[1,1]),([1,2,3],[3,2,1]),([1,2,5],[2,6,3]),([2,2],[1,3]),([5,0,5],[0,5,0]),([1,3,1],[2,2,2]),([4,1,2],[3,2,2]),([0,1,0],[1,0,1]),([2,4,6,8],[1,3,5,7])]],RANGES,[RANGES.replace('states=current','states={**states,**current}'),RANGES.replace('states.get(0,0)','current.get(0,0)//2')],['Keeps ranges from earlier endpoints alive and extends noncontiguous choices.','Divides balanced counts by two and undercounts distinct choices.'],ranges_o,rranges,L('Represent choosing nums1 as a positive balance change and nums2 as a negative change.','Maintain counts of balances for ranges ending at the previous index, then start or extend ranges at the current index.','Build current from +a and -b starts plus both transitions from every prior balance; add current[0].','Each state corresponds uniquely to a range ending here and its choices, so zero balance counts exactly the new balanced ranges.'),'O(n*distinct balances)','O(distinct balances)',8),
2144:entry('minimum_candy_purchase_cost',[('cost','list[int]')],'int',['arrays','greedy','sorting'],['Candy costs are positive.','For every two paid candies, one candy costing no more than either paid candy may be free.','Return the minimum total paid cost to obtain all candies.'],[([[1,2,3]],'Pay for costs three and two and receive cost one free, totaling five.'),([[6,5,7,9,2,2]],'Sorted groups let costs five and two be free, so the minimum paid total is twenty-three.')],[[c] for c in [[1],[1,2],[1,2,3],[3,3,3],[1,2,3,4],[1,2,3,4,5],[1,2,3,4,5,6],[10,1,1],[5,5,1,1,1,1],[9,8,7,6],[2,2,2,2,2],[100,50,25],[4,3,2,1,1,1],[8,6,4,2,1]]],CANDY,[CANDY.replace('reverse=True','reverse=False'),CANDY.replace('index%3!=2','index%3!=1')],['Sorts ascending and gives away candies that are too expensive relative to the paid pair.','Makes every second candy free rather than every third candy.'],candy_o,rcandy,L('To maximize the free discount, sort descending and group each two expensive paid candies with the next cheaper candy.','In descending order, every third candy can legally be free and choosing any cheaper one instead cannot save more.','Sum values whose sorted index modulo three is not two.','An exchange argument pairs each free candy with the nearest two preceding paid costs, maximizing every free contribution without violating its price limit.'),'O(n log n)','O(n)',3)
}
