"""Modulo patterns, permutation operations, sales, lighting, and binary generation."""
from collections import deque
from itertools import product
from .import_batch_055 import entry

def modulo_oracle(a):
    nums,k=a;return min(sum(min(abs(v%k-(x if i%2==0 else y)),k-abs(v%k-(x if i%2==0 else y))) for i,v in enumerate(nums)) for x in range(k) for y in range(k) if x!=y)
def random_modulo(r):return [[r.randint(0,50) for _ in range(r.randint(2,12))],r.randint(2,8)]
def sort_oracle(a):
    start=tuple(a[0]);target=tuple(range(len(start)));seen={start};q=deque([(start,0)])
    while q:
        state,d=q.popleft()
        if state==target:return d
        for nxt in (state[::-1],state[1:]+state[:1]):
            if nxt not in seen:seen.add(nxt);q.append((nxt,d+1))
    return -1
def random_sort(r):
    nums=list(range(r.randint(1,7)));r.shuffle(nums);return [nums]
def sale_oracle(a):
    items,budget=a;n=len(items);best=0;cheap=min(p for _,p in items)
    for mask in range(1<<n):
        cost=sum(items[i][1] for i in range(n) if mask>>i&1)
        if cost<=budget:
            promoted=sum(sum(items[j][0]%items[i][0]==0 for j in range(n)) for i in range(n) if mask>>i&1)
            best=max(best,promoted+(budget-cost)//cheap)
    return best
def random_sale(r):return [[[r.randint(1,12),r.randint(1,10)] for _ in range(r.randint(1,7))],r.randint(0,30)]
def energy_oracle(a):
    n,brightness,intervals=a;times=set()
    for left,right in intervals:times.update(range(left,right+1))
    bulbs=next(used for used in range(n+1) if used*3>=brightness)
    return bulbs*len(times)
def random_energy(r):
    n=r.randint(1,10);return [n,r.randint(1,n),[[r.randint(0,12),r.randint(12,20)] for _ in range(r.randint(1,6))]]
def strings_oracle(a):
    n,k=a;return [''.join(bits) for bits in product('01',repeat=n) if '11' not in ''.join(bits) and sum(i for i,b in enumerate(bits) if b=='1')<=k]
def random_strings(r):return [r.randint(1,9),r.randint(0,30)]

MODULO='''def minimum_modulo_alternating_operations(nums,k):
    values=[value%k for value in nums];answer=float('inf')
    for even in range(k):
        for odd in range(k):
            if even==odd:continue
            cost=0
            for i,value in enumerate(values):
                target=even if i%2==0 else odd;distance=abs(target-value);cost+=min(distance,k-distance)
            answer=min(answer,cost)
    return answer
'''
SORT='''def minimum_permutation_sort_operations(nums):
    n=len(nums);zero=nums.index(0)
    def ordered(step):return all(nums[(zero+(i-1)*step)%n]<nums[(zero+i*step)%n] for i in range(1,n))
    answer=float('inf')
    if ordered(1):answer=min(answer,zero,n-zero+2)
    if ordered(-1):answer=min(answer,zero+2,n-zero)
    return -1 if answer==float('inf') else answer
'''
SALE='''def maximum_sale_items(items,budget):
    best=[0]*(budget+1);cheapest=min(price for _,price in items)
    for factor,price in items:
        reward=sum(other%factor==0 for other,_ in items)
        for spent in range(budget,price-1,-1):best[spent]=max(best[spent],best[spent-price]+reward)
    return max(value+(budget-spent)//cheapest for spent,value in enumerate(best))
'''
ENERGY='''def minimum_brightness_energy(n,brightness,intervals):
    intervals=sorted(map(list,intervals));merged=[]
    for left,right in intervals:
        if not merged or merged[-1][1]<left:merged.append([left,right])
        else:merged[-1][1]=max(merged[-1][1],right)
    return ((brightness+2)//3)*sum(right-left+1 for left,right in merged)
'''
STRINGS='''def valid_binary_strings_with_cost(n,k):
    answer=[]
    def visit(i,cost,path):
        if i==n:answer.append(path);return
        visit(i+1,cost,path+'0')
        if (not path or path[-1]=='0') and cost+i<=k:visit(i+1,cost+i,path+'1')
    visit(0,0,'');return answer
'''

BATCH={
3937:entry('minimum_modulo_alternating_operations',[('nums','list[int]'),('k','int')],'int',['arrays','enumeration'],['len(nums)>=2 and k>=2.','One operation changes one value by one in either direction; residues wrap modulo k.','Choose distinct even- and odd-index residues and minimize operations.'],[([[1,4,2,8],3],'Choosing residues one and two needs two unit changes.'),([[0,1,0,1],2],'The array already alternates between distinct residues, so no operation is needed.')],[[n,k] for n,k in [([0,0],2),([0,1],2),([1,4,2,8],3),([0,1,0,1],2),([1,1,1],3),([2,5,8,11],3),([0,4,0,4],5),([7,7],4),([1,2,3,4,5],3),([9,0,9],10),([2,0,2,0],3),([5,10,15,20],6),([3,8,13],5),([1,7,2,8,3,9],4)]],MODULO,[MODULO.replace('if even==odd:continue',''),MODULO.replace('min(distance,k-distance)','distance')],['Allows the two target residues to be equal.','Ignores circular residue distance across zero.'],modulo_oracle,random_modulo,['Only residues matter, and there are k choices for each parity.','Enumerate distinct target residues and add circular distance for every element.','Use min(abs difference, k-abs difference), retaining the cheapest pair.','Each unit edit moves one step around the residue cycle, so circular distance is exact.'],'O(k^2*n)','O(n)',5),
3942:entry('minimum_permutation_sort_operations',[('nums','list[int]')],'int',['arrays','math'],['nums is a permutation of 0 through n-1.','An operation either reverses the whole array or rotates it left by one.','Return the fewest operations to sort ascending, or -1.'],[([[0,2,1]],'Two full reversals/rotations can sort this reachable orientation.'),([[0,1,2]],'The permutation is already sorted.')],[[x] for x in [[0],[0,1],[1,0],[0,2,1],[2,0,1],[1,2,0],[2,1,0],[0,1,2,3],[3,0,1,2],[1,0,3,2],[3,2,1,0],[2,3,0,1],[1,2,3,0],[0,3,2,1]]],SORT,[SORT.replace('zero,n-zero+2','zero+1,n-zero+2'),SORT.replace('return -1 if','return 0 if')],['Adds an operation to the direct forward-rotation case.','Returns zero rather than -1 for unreachable orientations.'],sort_oracle,random_sort,['Rotations and full reversal can only produce a cyclic ascending or cyclic descending order.','Locate zero and test both directions around the cycle.','For each valid orientation, compare direct rotations with two reversals plus rotations.','The dihedral orbit contains exactly these two orientations, so all other permutations are unreachable.'],'O(n)','O(1)',5),
3946:entry('maximum_sale_items',[('items','list[list[int]]'),('budget','int')],'int',['dynamic programming','knapsack'],['Each item type is [factor,price], and budget is nonnegative.','The first promotional purchase of a type also yields one free copy of every type whose factor is divisible by it; later purchases still yield the bought copy.','Maximize total purchased and free copies.'],[([[[6,2],[2,6],[3,4]],9],'Choosing promotions and spending the remainder on the cheapest type yields four items.'),([[[1,3]],10],'One promotion plus two further copies obtains three items.')],[[i,b] for i,b in [([[1,1]],0),([[1,3]],10),([[6,2],[2,6],[3,4]],9),([[1,2],[2,3]],5),([[2,5],[4,1]],6),([[3,4],[6,4]],8),([[1,10],[2,2],[4,3]],9),([[5,7]],6),([[2,2],[3,3],[6,5]],10),([[4,1],[8,8]],3),([[1,5],[2,5],[3,5]],15),([[7,2],[14,4],[21,6]],12),([[2,9],[4,9]],18),([[1,1],[1,2]],5)]],SALE,[SALE.replace('range(budget,price-1,-1)','range(price,budget+1)'),SALE.replace('(budget-spent)//cheapest','0')],['Turns each promotion into an unbounded knapsack item and awards its free copies repeatedly.','Forgets that leftover budget can buy additional ordinary copies.'],sale_oracle,random_sale,['Each promotion is available at most once, which is a 0/1 knapsack choice.','Its reward is the number of factors divisible by the purchased factor.','Update budget states backward, then spend each leftover amount on the globally cheapest ordinary copy.','Every plan separates uniquely into first promotional purchases and nonpromotional repeat purchases.'],'O(types^2+types*budget)','O(budget)',5),
3951:entry('minimum_brightness_energy',[('n','int'),('brightness','int'),('intervals','list[list[int]]')],'int',['intervals','greedy'],['There are n bulbs in a line; an active interior bulb can illuminate its own and adjacent positions.','During every inclusive time interval, total illuminated positions must be at least brightness; overlapping requirements are not additive.','Return minimum bulb-on time units.'],[([5,5,[[6,12]]],'Two bulbs cover at least five positions for seven time units, costing fourteen.'),([3,3,[[1,2],[2,4]]],'The union is times one through four and one bulb suffices, costing four.')],[[n,b,i] for n,b,i in [(1,1,[[0,0]]),(3,3,[[1,2],[2,4]]),(5,5,[[6,12]]),(4,1,[[0,5]]),(6,6,[[1,1]]),(5,4,[[0,2],[5,6]]),(10,10,[[0,9]]),(2,2,[[3,3],[3,3]]),(8,7,[[1,4],[4,8]]),(3,1,[[0,0],[2,2]]),(9,9,[[10,12],[1,2]]),(4,3,[[0,3],[4,6]]),(7,2,[[5,10]]),(5,5,[[0,0],[2,4],[3,6]])]],ENERGY,[ENERGY.replace('(brightness+2)//3','brightness//3'),ENERGY.replace("merged[-1][1]<left","merged[-1][1]+1<left")],['Rounds required active bulbs down.','Merges merely adjacent time intervals using the wrong overlap rule.'],energy_oracle,random_energy,['One active bulb contributes illumination to at most three positions, so ceil(brightness/3) bulbs are necessary and sufficient.','Merge overlapping required time intervals so shared times are paid once.','Multiply required bulbs by the total inclusive length of the interval union.','The spatial optimum is identical at each required time, while interval union accounts for exactly those times.'],'O(t log t)','O(t)',5),
3955:entry('valid_binary_strings_with_cost',[('n','int'),('k','int')],'list[str]',['backtracking','strings'],['n is positive and k is nonnegative.','A valid length-n binary string has no adjacent ones.','Its cost is the sum of zero-based indices containing one; return every valid string with cost at most k in lexicographic order.'],[([3,1],'The valid strings within cost one are 000, 010, and 100.'),([2,0],'Strings 00 and 10 have cost zero and no adjacent ones.')],[[n,k] for n,k in [(1,0),(1,1),(2,0),(2,1),(3,1),(3,3),(4,0),(4,2),(4,6),(5,3),(5,10),(6,4),(7,8),(8,20)]],STRINGS,[STRINGS.replace("path+'0'","path+'1'",1),STRINGS.replace("and cost+i<=k","")],['Takes the one-branch where the zero-branch belongs and produces duplicates/invalid order.','Ignores the cost limit on newly placed ones.'],strings_oracle,random_strings,['Build the answer left to right so adjacent and cost constraints are local.','Always branch to zero; branch to one only after zero and within remaining cost.','At index i recurse with unchanged cost for zero or cost+i for allowed one.','Every accepted string has one unique decision path, and zero-first traversal gives lexicographic order.'],'O(2^n)','O(n)',5),
}
BATCH[3942]['boundaries'].append([[0,2,1,3]])
