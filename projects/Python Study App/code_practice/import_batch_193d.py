"""Ship capacity, reverse degree, prefix cost, pair merging, and divisibility."""
from .import_batch_055 import entry

def ship_oracle(a):return min(a[0]*a[0],a[2]//a[1])
def random_ship(r):return [r.randint(1,100),r.randint(1,100),r.randint(1,100000)]
def degree_oracle(a):return sum((26-(ord(c)-97))*i for i,c in enumerate(a[0],1))
def random_degree(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,50)))]
def costs_oracle(a):return [min(a[0][:i+1]) for i in range(len(a[0]))]
def random_costs(r):return [[r.randint(1,100) for _ in range(r.randint(1,40))]]
def removal_oracle(a):
    nums=a[0][:];operations=0
    while any(x>y for x,y in zip(nums,nums[1:])):
        best=min(nums[i]+nums[i+1] for i in range(len(nums)-1));i=next(i for i in range(len(nums)-1) if nums[i]+nums[i+1]==best)
        nums[i:i+2]=[best];operations+=1
    return operations
def random_removal(r):return [[r.randint(-20,30) for _ in range(r.randint(1,12))]]
def divisible_oracle(a):return sum(a[0])%a[1]
def random_divisible(r):return [[r.randint(0,100) for _ in range(r.randint(1,40))],r.randint(1,30)]

SHIP='''def maximum_ship_containers(n,w,maxWeight):
    return min(n*n,maxWeight//w)
'''
DEGREE='''def reverse_degree(s):
    return sum((26-(ord(char)-ord('a')))*position for position,char in enumerate(s,1))
'''
COSTS='''def minimum_cost_to_each_position(cost):
    answer=[]
    best=float('inf')
    for value in cost:
        best=min(best,value)
        answer.append(best)
    return answer
'''
REMOVAL='''def minimum_leftmost_pair_removals(nums):
    values=nums[:]
    operations=0
    while any(left>right for left,right in zip(values,values[1:])):
        index=min(range(len(values)-1),key=lambda i:(values[i]+values[i+1],i))
        values[index:index+2]=[values[index]+values[index+1]]
        operations+=1
    return operations
'''
DIVISIBLE='''def minimum_decrements_for_divisible_sum(nums,k):
    return sum(nums)%k
'''

BATCH={
3492:entry('maximum_ship_containers',[('n','int'),('w','int'),('maxWeight','int')],'int',['math','greedy'],['An n by n deck has n squared container positions.','Every container weighs exactly w and total weight cannot exceed maxWeight.','Return the greatest number of containers that fit both limits.'],[([2,3,15],'The deck has four cells and the weight limit permits five containers, so four fit.'),([3,5,12],'Weight permits only two containers despite nine deck cells.')],[[n,w,m] for n,w,m in [(1,1,1),(1,2,1),(2,3,15),(3,5,12),(10,1,50),(4,10,160),(4,10,159),(5,7,20),(2,100,1000),(100,2,3),(6,6,216),(7,8,400),(3,1,100),(9,9,80)]],SHIP,[SHIP.replace('n*n','n'),SHIP.replace('maxWeight//w','maxWeight/w')],['Uses only n deck positions instead of n squared.','Returns a noninteger fractional capacity.'],ship_oracle,random_ship,['Deck area limits the count to n squared.','Integer division maxWeight//w gives the weight-limited count.','Both constraints must hold simultaneously.','The smaller of the two independent capacities is achievable and maximal.'],'O(1)','O(1)',3),
3498:entry('reverse_degree',[('s','str')],'int',['strings','math'],['Map a to 26, b to 25, and so on through z to 1.','Multiply each mapped value by its one-indexed position in s.','Return the sum of all products.'],[(['abc'],'The weighted values are 26*1 + 25*2 + 24*3 = 148.'),(['z'],'z has reversed value one at position one.')],[[s] for s in ['a','z','az','za','abc','xyz','aaa','zzz','leetcode','python','m','alphabet','code','reverse']],DEGREE,[DEGREE.replace('26-','25-'),DEGREE.replace('enumerate(s,1)','enumerate(s)')],['Shifts every reverse-alphabet value down by one.','Uses zero-indexed string positions.'],degree_oracle,random_degree,['Convert each character to its zero-based ordinary alphabet offset.','Subtract that offset from 26 for its reversed value.','Multiply by the one-based string position.','Summing each independent contribution implements the definition directly.'],'O(n)','O(1)',3),
3502:entry('minimum_cost_to_each_position',[('cost','list[int]')],'list[int]',['arrays','prefix minima'],['You begin behind all listed positions and may pay a person’s cost to swap ahead to that position.','After moving ahead, positions passed from behind can be reached without paying a higher earlier cost again.','Return the minimum cost to reach every position from left to right.'],[([[5,3,4,1,3,2]],'Prefix minima are [5,3,3,1,1,1].'),([[2,2,2]],'Every position has minimum reachable cost two.')],[[x] for x in [[1],[5,3,4,1,3,2],[2,2,2],[1,2,3],[3,2,1],[10,1],[1,10],[9,8,7,6],[4,5,2,8],[100,50,75],[3,1,4,1,5],[7,7,1,7],[2,9,3,9],[6,5,6,4]]],COSTS,[COSTS.replace("best=float('inf')","best=float('-inf')").replace('min(best,value)','max(best,value)'),COSTS.replace('best=float(\'inf\')','best=0')],['Tracks finite prefix maxima rather than minima.','Initializes the best cost to zero and incorrectly makes every result zero.'],costs_oracle,random_costs,['Scan positions in order.','Maintain the smallest cost seen so far.','That earlier or current person is the cheapest way to reach the current position.','Appending each prefix minimum yields all answers in one pass.'],'O(n)','O(n)',3),
3507:entry('minimum_leftmost_pair_removals',[('nums','list[int]')],'int',['arrays','simulation'],['While nums is not nondecreasing, find the adjacent pair with minimum sum, choosing the leftmost on ties.','Replace that pair by its sum.','Return the number of operations until the array becomes nondecreasing.'],[([[5,2,3,1]],'Two prescribed merges make the array nondecreasing.'),([[1,2,3]],'The array is already nondecreasing, so zero operations are needed.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[3,2,1],[5,2,3,1],[0,0,0],[-1,-2,-3],[3,1,2],[2,2,1],[10,1,1,10],[4,3,2,5],[1,3,2,4],[5,1,4,2]]],REMOVAL,[REMOVAL.replace('values[i]+values[i+1],i','-(values[i]+values[i+1]),i'),REMOVAL.replace('left>right','left>=right')],['Selects the maximum-sum adjacent pair.','Treats equal neighbors as an ordering violation.'],removal_oracle,random_removal,['Test whether any adjacent inversion remains.','Choose the minimum adjacent sum with index as the tie breaker.','Splice that sum in place of its two operands.','The operation is deterministic, so direct simulation until sorted gives the required count.'],'O(n^2)','O(n)',3),
3512:entry('minimum_decrements_for_divisible_sum',[('nums','list[int]'),('k','int')],'int',['arrays','math','modular arithmetic'],['One operation decreases any array element by one.','Return the minimum operations needed to make the total array sum divisible by k.','Elements may be decreased repeatedly.'],[([[3,9,7],5],'The sum is nineteen; decreasing by four reaches fifteen, divisible by five.'),([[4,1],5],'The sum is already divisible by five, so zero operations are needed.')],[[n,k] for n,k in [([1],1),([1],2),([3,9,7],5),([4,1],5),([0],7),([10],3),([1,2,3],4),([5,5,5],5),([9,9],10),([2,4,6],7),([100,1],10),([0,0,1],2),([7,8,9],6),([3,3,3],4)]],DIVISIBLE,[DIVISIBLE.replace('%k','//k'),DIVISIBLE.replace('sum(nums)','sum(nums)+1')],['Uses quotient instead of remainder.','Adds one to the total before measuring the remainder.'],divisible_oracle,random_divisible,['Let total be the current sum.','Each decrement lowers total by exactly one.','The remainder total modulo k is the number of decrements needed to reach the previous multiple.','Fewer decrements leave a positive remainder, so this count is minimal.'],'O(n)','O(1)',3),
}
