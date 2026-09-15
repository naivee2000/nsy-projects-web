"""Linear scores, beautiful arrays, modulo reduction, flower game, and tree XOR."""
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

def stock_oracle(a):
    prices=a[0];best=0
    for mask in range(1,1<<len(prices)):
        chosen=[i for i in range(len(prices)) if mask>>i&1]
        if all(prices[i]-i==prices[chosen[0]]-chosen[0] for i in chosen):best=max(best,sum(prices[i] for i in chosen))
    return best
def random_stock(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
def beautiful_oracle(a):
    nums,k=a;n=len(nums);best=float('inf')
    for mask in range(1<<n):
        if all(any(nums[i]>=k or mask>>i&1 for i in range(start,start+3)) for start in range(max(0,n-2))):
            best=min(best,sum(max(0,k-nums[i]) for i in range(n) if mask>>i&1))
    return best
def random_beautiful(r):return [[r.randint(0,10) for _ in range(r.randint(1,9))],r.randint(1,10)]
def modulo_oracle(a):
    @lru_cache(None)
    def solve(state):
        answer=len(state)
        for i in range(len(state)):
            for j in range(len(state)):
                if i!=j and state[i]>0 and state[j]>0:
                    nxt=tuple(sorted([state[x] for x in range(len(state)) if x not in (i,j)]+[state[i]%state[j]]))
                    answer=min(answer,solve(nxt))
        return answer
    return solve(tuple(sorted(a[0])))
def random_modulo(r):return [[r.randint(1,12) for _ in range(r.randint(1,6))]]
def flower_oracle(a):return sum((x+y)%2==1 for x in range(1,a[0]+1) for y in range(1,a[1]+1))
def random_flower(r):return [r.randint(1,100),r.randint(1,100)]
def tree_xor_oracle(a):
    nums,k,edges=a;best=sum(nums)
    for mask in range(1<<len(edges)):
        values=nums[:]
        for e,(u,v) in enumerate(edges):
            if mask>>e&1:values[u]^=k;values[v]^=k
        best=max(best,sum(values))
    return best
def random_tree_xor(r):
    n=r.randint(2,9);edges=[[i,r.randrange(i)] for i in range(1,n)]
    return [[r.randint(0,31) for _ in range(n)],r.randint(0,31),edges]

STOCK='''def maximum_linear_stock_score(prices):
    totals={}
    for index,price in enumerate(prices):totals[price-index]=totals.get(price-index,0)+price
    return max(totals.values())
'''
BEAUTIFUL='''def minimum_beautiful_array_increments(nums,k):
    first=second=third=0
    for value in nums:
        first,second,third=second,third,min(first,second,third)+max(0,k-value)
    return min(first,second,third)
'''
MODULO='''def minimum_modulo_array_length(nums):
    smallest=min(nums)
    if any(value%smallest for value in nums):return 1
    return (nums.count(smallest)+1)//2
'''
FLOWER='''def winning_flower_pairs(n,m):
    odd_n=(n+1)//2;odd_m=(m+1)//2
    return odd_n*(m//2)+(n//2)*odd_m
'''
TREE_XOR='''def maximum_tree_value_sum(nums,k,edges):
    even,odd=0,float('-inf')
    for value in nums:
        even,odd=max(even+value,odd+(value^k)),max(odd+value,even+(value^k))
    return even
'''

BATCH={
2898:entry('maximum_linear_stock_score',[('prices','list[int]')],'int',['arrays','hash-maps'],['1 <= len(prices) <= 100,000; prices are positive.','A valid selection contains indices whose price minus index is the same.','Its score is the sum of selected prices; return the maximum score.'],[([[1,5,3,7,8]],'Prices at indices 1, 3, and 4 share price-index value four and sum to twenty.'),([[2,3,4]],'All three entries share price-index value two and total nine.')],[[x] for x in [[1],[1,5,3,7,8],[2,3,4],[5,1],[4,4,4],[1,2,3,4],[4,3,2,1],[10,1,12],[3,8,5,10],[2,10,4,12],[7,7],[1,9,3,11,5],[100,1,102],[5,6,20,8]]],STOCK,[STOCK.replace('price-index','price+index'),STOCK.replace('max(totals.values())','sum(prices)')],['Groups along the opposite diagonal.','Selects every price even when their linear keys differ.'],stock_oracle,random_stock,['Rearrange the linear condition as price-index = constant.','Accumulate prices by that invariant in a hash map.','For each index and price, add price to totals[price-index]; return the largest total.','Every valid selection lies in exactly one invariant group, and positive prices make taking its whole group optimal.'],'O(n)','O(n)',5),
2919:entry('minimum_beautiful_array_increments',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming'],['1 <= len(nums) <= 100,000; nums values are nonnegative.','Incrementing one element by one costs one operation.','Make every contiguous subarray of length at least three contain a value at least k; return minimum cost.'],[([[2,3,0,0,2],4],'Raising selected positions to four costs three and covers every length-three window.'),([[0,1,3,3],5],'Choosing the two final positions costs four, which is minimum.')],[[n,k] for n,k in [([1],5),([1,2],5),([2,3,0,0,2],4),([0,1,3,3],5),([5,0,0],5),([0,0,5],5),([0,0,0],1),([1,1,1,1],3),([3,0,0,3],3),([0,2,0,2,0],3),([10,1,1,1],5),([1,10,1,1,10],5),([4,4,4],4),([2,7,1,0,5,1],6)]],BEAUTIFUL,[BEAUTIFUL.replace('min(first,second,third)','first',1),BEAUTIFUL.replace('max(0,k-value)','k-value')],['Forces the state from exactly three positions ago instead of choosing the cheapest recent state.','Allows already-large values to contribute negative cost.'],beautiful_oracle,random_beautiful,['It is enough to ensure every length-three window contains a qualifying position.','Track the minimum cost when the latest chosen/qualified position is one, two, or three steps back.','Shift three costs; the new chosen cost is min(states)+max(0,k-value).','A gap of three unqualified positions is forbidden, so these three states describe every feasible prefix.'],'O(n)','O(1)',6),
3012:entry('minimum_modulo_array_length',[('nums','list[int]')],'int',['arrays','math'],['1 <= len(nums) <= 100,000; nums contains positive integers.','Replace any chosen pair by one value equal to the first modulo the second.','Return the smallest length reachable after repeated operations.'],[([[1,4,3,1]],'A non-multiple of the minimum permits producing a smaller remainder and ultimately one value.'),([[2,4,6,8]],'All values are multiples of two and only one minimum occurs, so one value can remain.')],[[x] for x in [[1],[1,1],[1,4,3,1],[2,4,6,8],[2,2,4,6],[3,6,9],[3,3,3],[4,6],[5,10,15,20],[6,10,14],[7,7,14,21],[2,3,4],[10,20,30,40],[8,8,16,24,32]]],MODULO,[MODULO.replace('any(value%smallest for value in nums)','all(value%smallest for value in nums)'),MODULO.replace('+1','+2')],['Tests whether every value has a remainder instead of whether any does.','Rounds the count of minimum values incorrectly.'],modulo_oracle,random_modulo,['The current minimum controls whether a still smaller positive remainder can be created.','If any value is not divisible by the minimum, repeated modulo reductions can reach one remaining value.','Otherwise only minimum copies matter; return ceil(count/2).','Pairs of minimum values turn into zero and eliminate two copies, while an odd leftover requires one final value.'],'O(n)','O(1)',5),
3021:entry('winning_flower_pairs',[('n','int'),('m','int')],'int',['math','counting'],['1 <= n,m <= 100,000.','For each 1 <= x <= n and 1 <= y <= m, players alternately remove one flower and Alice moves first.','Count pairs for which Alice takes the last flower.'],[([3,2],'Exactly the three pairs with opposite parities have an odd total and are winning.'),([1,1],'Two total flowers let Bob take the last flower, so this pair is not winning for Alice.')],[[n,m] for n,m in [(1,1),(1,2),(2,1),(2,2),(3,2),(3,3),(4,5),(5,4),(10,10),(7,8),(8,7),(99,100),(100,101),(1000,999)]],FLOWER,[FLOWER.replace('(m//2)','odd_m',1),FLOWER.replace('+','-',1)],['Counts odd-odd pairs instead of odd-even pairs.','Subtracts one parity combination from the other.'],flower_oracle,random_flower,['Alice wins exactly when x+y is odd, meaning one lane count is odd and the other even.','Count odd and even choices independently in each range.','Return odd(n)*even(m)+even(n)*odd(m).','The two opposite-parity cases are disjoint and cover every winning pair.'],'O(1)','O(1)',5),
3068:entry('maximum_tree_value_sum',[('nums','list[int]'),('k','int'),('edges','list[list[int]]')],'int',['trees','dynamic programming','bit manipulation'],['nums describes a connected tree with n nodes and n-1 edges.','An operation chooses an edge and XORs both endpoint values with k.','Return the maximum achievable sum after any number of operations.'],[([[1,2,1],3,[[0,1],[0,2]]],'Toggle edge 0-2 to obtain values 2,2,2 and total six.'),([[2,3],7,[[0,1]]],'Either toggle both endpoints or neither; the unchanged sum five is larger.')],[[n,k,e] for n,k,e in [([1,2],3,[[0,1]]),([1,2,1],3,[[0,1],[0,2]]),([2,3],7,[[0,1]]),([7,7,7],1,[[0,1],[1,2]]),([0,0],5,[[0,1]]),([1,1,1,1],2,[[0,1],[1,2],[2,3]]),([8,4,2],7,[[0,1],[0,2]]),([5,10,15],3,[[0,1],[1,2]]),([3,6,9,12],4,[[0,1],[0,2],[0,3]]),([31,0],31,[[0,1]]),([2,8,1,16],15,[[0,1],[1,2],[2,3]]),([4,4,4],4,[[0,1],[1,2]]),([1,9,2,8,3],6,[[0,1],[0,2],[2,3],[2,4]]),([10,20,30],0,[[0,1],[1,2]])]],TREE_XOR,[TREE_XOR.replace('return even','return max(even,odd)'),TREE_XOR.replace("odd=0,float('-inf')","odd=0,0")],['Allows an odd number of toggled nodes, which no set of edges can create.','Starts the odd-parity state as reachable before processing any node.'],tree_xor_oracle,random_tree_xor,['Every edge operation toggles two nodes, so the number of toggled nodes is even.','In a connected tree, every even-size node subset can be produced by edge operations.','Scan values while tracking best sums for an even or odd number of chosen XOR values.','The two-state transition considers keeping or XORing each node; only the final even state is feasible.'],'O(n)','O(1)',8),
}
