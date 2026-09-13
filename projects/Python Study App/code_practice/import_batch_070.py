"""Reviewed interval, symmetry, string-DP, window, stock, and bit-code imports."""
from itertools import combinations

from .import_batch_055 import entry


def squares_oracle(args):
    placed=[];answer=[];highest=0
    for left,size in args[0]:
        right=left+size;base=0
        for old_left,old_right,height in placed:
            if max(left,old_left)<min(right,old_right):base=max(base,height)
        height=base+size;placed.append((left,right,height));highest=max(highest,height);answer.append(highest)
    return answer


def lower_oracle(args):
    return ''.join(chr(ord(char)+32) if 'A'<=char<='Z' else char for char in args[0])


def canonical_shape(cells):
    variants=[]
    for swap in (False,True):
        for sx in (-1,1):
            for sy in (-1,1):
                points=[(sx*(c if swap else r),sy*(r if swap else c)) for r,c in cells]
                min_r=min(r for r,c in points);min_c=min(c for r,c in points)
                variants.append(tuple(sorted((r-min_r,c-min_c) for r,c in points)))
    return min(variants)


def islands_two_oracle(args):
    grid=args[0];rows,columns=len(grid),len(grid[0]);seen=set();shapes=set()
    for row in range(rows):
        for column in range(columns):
            if not grid[row][column] or (row,column) in seen:continue
            stack=[(row,column)];seen.add((row,column));cells=[]
            while stack:
                r,c=stack.pop();cells.append((r,c))
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            shapes.add(canonical_shape(cells))
    return len(shapes)


def delete_sum_oracle(args):
    first,second=args;best=0
    for size in range(1,min(len(first),len(second))+1):
        left={''.join(first[i] for i in indices) for indices in combinations(range(len(first)),size)}
        right={''.join(second[i] for i in indices) for indices in combinations(range(len(second)),size)}
        for shared in left&right:best=max(best,sum(map(ord,shared)))
    return sum(map(ord,first))+sum(map(ord,second))-2*best


def products_oracle(args):
    nums,k=args;return sum(1 for left in range(len(nums)) for right in range(left+1,len(nums)+1) if product_values(nums[left:right])<k)


def product_values(values):
    result=1
    for value in values:result*=value
    return result


def stock_oracle(args):
    prices,fee=args;states={(False,0):0}
    for price in prices:
        following=dict(states)
        for (holding,bought),profit in states.items():
            if holding:following[(False,0)]=max(following.get((False,0),-10**9),profit+price-fee)
            else:following[(True,price)]=max(following.get((True,price),-10**9),profit-price)
        states=following
    return max(profit for (holding,_),profit in states.items() if not holding)


def one_bit_oracle(args):
    bits=args[0]
    reachable={0}
    for index in range(len(bits)):
        if index not in reachable:continue
        reachable.add(index+(1 if bits[index]==0 else 2))
    return len(bits)-1 in reachable


def random_squares(rng):return [[[rng.randint(1,20),rng.randint(1,8)] for _ in range(rng.randint(1,9))]]
def random_lower(rng):return [''.join(rng.choice('abcXYZ09!? ') for _ in range(rng.randint(1,30)))]
def random_islands(rng):
    rows,columns=rng.randint(1,6),rng.randint(1,6);return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]
def random_delete(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(0,8))),''.join(rng.choice('abcd') for _ in range(rng.randint(0,8)))]
def random_products(rng):return [[rng.randint(1,10) for _ in range(rng.randint(1,14))],rng.randint(0,100)]
def random_stock(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,12))],rng.randint(0,8)]
def random_bits(rng):
    encoded=[]
    while len(encoded)<rng.randint(1,12):encoded.extend([0] if rng.random()<.5 else [1,rng.randrange(2)])
    encoded=encoded[:max(1,len(encoded))];encoded[-1]=0
    return [encoded]


SQUARES='''\
def falling_square_heights(positions):
    intervals=[];answer=[];global_height=0
    for left,size in positions:
        right=left+size;base=0
        for old_left,old_right,height in intervals:
            if max(left,old_left)<min(right,old_right):base=max(base,height)
        height=base+size;intervals.append((left,right,height))
        global_height=max(global_height,height);answer.append(global_height)
    return answer
'''
LOWER='''\
def ascii_lowercase(s):
    return ''.join(chr(ord(char)+32) if 'A'<=char<='Z' else char for char in s)
'''
ISLANDS='''\
def distinct_islands_with_symmetry(grid):
    rows,columns=len(grid),len(grid[0]);seen=set();shapes=set()
    def canonical(cells):
        variants=[]
        for swap in (False,True):
            for sx in (-1,1):
                for sy in (-1,1):
                    points=[(sx*(c if swap else r),sy*(r if swap else c)) for r,c in cells]
                    low_r=min(r for r,c in points);low_c=min(c for r,c in points)
                    variants.append(tuple(sorted((r-low_r,c-low_c) for r,c in points)))
        return min(variants)
    for row in range(rows):
        for column in range(columns):
            if not grid[row][column] or (row,column) in seen:continue
            cells=[];stack=[(row,column)];seen.add((row,column))
            while stack:
                r,c=stack.pop();cells.append((r,c))
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            shapes.add(canonical(cells))
    return len(shapes)
'''
DELETE='''\
def minimum_ascii_delete_sum(s1, s2):
    dp=[sum(map(ord,s2[index:])) for index in range(len(s2)+1)]
    for left in range(len(s1)-1,-1,-1):
        following=[0]*(len(s2)+1);following[-1]=ord(s1[left])+dp[-1]
        for right in range(len(s2)-1,-1,-1):
            if s1[left]==s2[right]:following[right]=dp[right+1]
            else:following[right]=min(ord(s1[left])+dp[right],ord(s2[right])+following[right+1])
        dp=following
    return dp[0]
'''
PRODUCTS='''\
def subarray_product_count(nums, k):
    if k<=1:return 0
    product=1;left=0;answer=0
    for right,value in enumerate(nums):
        product*=value
        while product>=k:
            product//=nums[left];left+=1
        answer+=right-left+1
    return answer
'''
STOCK='''\
def stock_profit_with_fee(prices, fee):
    cash=0;holding=-prices[0]
    for price in prices[1:]:
        old_cash=cash
        cash=max(cash,holding+price-fee)
        holding=max(holding,old_cash-price)
    return cash
'''
BITS='''\
def final_character_is_one_bit(bits):
    index=0
    while index<len(bits)-1:index+=2 if bits[index] else 1
    return index==len(bits)-1
'''


SQUARE_TOUCH=SQUARES.replace("max(left,old_left)<min(right,old_right)","max(left,old_left)<=min(right,old_right)")
SQUARE_CURRENT=SQUARES.replace('answer.append(global_height)','answer.append(height)')
LOWER_ALL="def ascii_lowercase(s):\n    return ''.join(chr(ord(c)+32) if '@'<=c<='[' else c for c in s)\n"
LOWER_AZ=LOWER.replace("'A'<=char<='Z'","'A'<char<'Z'")
ISLAND_TRANSLATION=ISLANDS.replace('return min(variants)','return variants[0]')
ISLAND_AREA="def distinct_islands_with_symmetry(grid):\n    return len({sum(row) for row in grid})\n"
DELETE_LENGTH="def minimum_ascii_delete_sum(s1,s2):\n    return abs(len(s1)-len(s2))\n"
DELETE_CHARS=DELETE.replace('ord(s1[left])','1').replace('ord(s2[right])','1')
PRODUCTS_LE=PRODUCTS.replace('product>=k','product>k')
PRODUCTS_FIXED="def subarray_product_count(nums,k):\n    return sum(value<k for value in nums)\n"
STOCK_ONCE="def stock_profit_with_fee(prices,fee):\n    return max(0,max(prices[j]-prices[i]-fee for i in range(len(prices)) for j in range(i+1,len(prices)))) if len(prices)>1 else 0\n"
STOCK_EACH=STOCK.replace('holding+price-fee','holding+price')
BITS_PREVIOUS="def final_character_is_one_bit(bits):\n    return len(bits)<2 or bits[-2]==0\n"
BITS_LAST="def final_character_is_one_bit(bits):\n    return bits[-1]==0\n"


def lesson(a,b,c,d):return [a,b,c,d],d
BATCH={
699:entry('falling_square_heights',[('positions','list[list[int]]')],'list[int]',['intervals','simulation'],['1 <= len(positions) <= 1,000; each square is [left, side length].','Squares stack only when horizontal interiors overlap; touching edges do not overlap. Return global height after each drop.'],[([[[1,2],[2,3],[6,1]]],'The first two interiors overlap and stack to height five; the third leaves the global maximum unchanged.'),([[[100,100],[200,100]]],'Touching at coordinate 200 does not overlap, so both heights remain one hundred.')],[[p] for p in ([[1,1]],[[1,2],[3,2]],[[1,2],[2,2]],[[1,5],[2,1]],[[2,1],[1,5]],[[1,2],[10,3],[2,2]],[[5,3],[4,2],[6,2]],[[1,10],[2,2],[3,1]],[[1,2],[4,2],[2,3]],[[10,1],[9,3],[12,2]],[[1,3],[3,3],[5,3]],[[1,2],[2,1],[3,2],[2,4]])],SQUARES,[SQUARE_TOUCH,SQUARE_CURRENT],['Treats touching edges as overlap.','Returns each new square’s height instead of the running global maximum.'],squares_oracle,random_squares,*lesson('A falling square rests on the highest earlier square whose horizontal interior overlaps it.','Keep prior half-open intervals and their final heights.','For each [left,right), find maximum height among strict overlaps, add size, then append running maximum.','Earlier squares never move, so direct interval comparison produces the exact support height; half-open boundaries exclude edge touching.'),'O(n²)','O(n)',8),
709:entry('ascii_lowercase',[('s','str')],'str',['strings'],['1 <= len(s) <= 100; s contains printable characters.','Convert ASCII A through Z to lowercase and leave every other character unchanged.'],[(['Hello'],'Only H changes, producing hello.'),(['here'],'A lowercase string remains unchanged.')],[[s] for s in ('A','Z','AZ','aZ','123','Hello@WORLD','[ABC]','Python 3','I','ALREADY LOWER','!AaZz','MiXeD')],LOWER,[LOWER_ALL,LOWER_AZ],['Uses an overly broad ASCII interval and alters adjacent punctuation.','Uses strict bounds and fails to convert A and Z.'],lower_oracle,random_lower,*lesson('Uppercase ASCII letters occupy one contiguous code-point range exactly 32 before lowercase.','Transform only characters between A and Z.','If A<=c<=Z emit chr(ord(c)+32), else emit c.','The explicit bounds prevent punctuation or digits from being altered.'),'O(len(s))','O(len(s))',3),
711:entry('distinct_islands_with_symmetry',[('grid','list[list[int]]')],'int',['matrices','geometry'],['Grid cells are zero or one and islands connect orthogonally.','Shapes are equivalent under translation, rotation, or reflection.'],[([[[1,1,0,0,0],[1,0,0,0,0],[0,0,0,0,1],[0,0,0,1,1]]],'The two L shapes match after rotation.'),([[[1,1,0,1],[1,0,0,1]]],'The L shape and length-two line are distinct.')],[[g] for g in ([[0]],[[1]],[[1,0,1]],[[1,1],[1,1]],[[1,0],[0,1]],[[1,1,0],[1,0,1]],[[1,1,0],[0,1,1]],[[1,0,0],[1,1,0],[0,0,1]],[[1,1,0,1],[0,1,0,1]],[[1,0,1],[1,0,1]],[[0,1,0],[1,1,0],[0,0,1]],[[1,1,0,0],[0,1,0,1],[0,0,0,1]])],ISLANDS,[ISLAND_TRANSLATION,ISLAND_AREA],['Normalizes translation only and treats rotated copies as distinct.','Compares row totals instead of connected geometric shapes.'],islands_two_oracle,random_islands,*lesson('A planar shape has eight rotation/reflection orientations.','Generate all signed coordinate swaps, translate each to the origin, and choose one canonical tuple.','Flood-fill cells; transform by swap/no-swap and both axis signs; normalize minima; take lexicographic minimum.','Equivalent shapes generate the same set of eight normalized orientations, so their minima match exactly.'),'O(rows*columns*log cells)','O(rows*columns)',8),
712:entry('minimum_ascii_delete_sum',[('s1','str'),('s2','str')],'int',['dynamic-programming','strings'],['Strings contain lowercase letters.','Delete characters from either string until equal while minimizing the sum of deleted ASCII values.'],[(['sea','eat'],'Keeping ea deletes s and t, whose ASCII values total 231.'),(['delete','leet'],'Keeping let yields a minimum deletion sum of 403.')],[[a,b] for a,b in (('',''),('a',''),('','b'),('a','a'),('a','b'),('ab','ba'),('abc','ac'),('seat','eat'),('x','xyz'),('aaa','aa'),('az','za'),('park','spake'))],DELETE,[DELETE_LENGTH,DELETE_CHARS],['Minimizes deleted character count instead of ASCII value.','Assigns every deletion unit cost rather than its character code.'],delete_sum_oracle,random_delete,*lesson('The decision at two suffixes is keep equal leading characters or delete one unequal leader.','Use suffix dynamic programming with one rolling row.','If characters match take diagonal; otherwise min(ord(left)+below, ord(right)+right).','Every valid common result begins with both equal leaders or omits at least one unequal leader, making the recurrence exhaustive.'),'O(len(s1)*len(s2))','O(len(s2))',5),
713:entry('subarray_product_count',[('nums','list[int]'),('k','int')],'int',['sliding-windows','arrays'],['All nums values are positive; 0 <= k <= 1,000,000.','Count contiguous subarrays whose product is strictly less than k.'],[([[10,5,2,6],100],'The eight valid subarrays include all singles plus [10,5], [5,2], [2,6], and [5,2,6].'), ([[1,2,3],0],'No positive product is less than zero.')],[[n,k] for n,k in (([1],1),([1],2),([2],2),([1,1],2),([10,5,2,6],10),([2,3,4],25),([1,2,1],3),([5,5,5],126),([1,1,1],1),([3,1,2],7),([100],100),([2,2,2,2],9))],PRODUCTS,[PRODUCTS_LE,PRODUCTS_FIXED],['Uses less-than-or-equal instead of the strict threshold.','Counts only one-element subarrays.'],products_oracle,random_products,*lesson('With positive values, shrinking the left edge can only decrease a window product.','Maintain the longest valid window ending at each right index.','Multiply the new value; divide from left while product>=k; add window length.','Every suffix of a valid positive-product window is also valid, so right-left+1 counts exactly the new subarrays.'),'O(n)','O(1)',5),
714:entry('stock_profit_with_fee',[('prices','list[int]'),('fee','int')],'int',['dynamic-programming','greedy'],['1 <= len(prices) <= 50,000; prices are positive and fee is nonnegative.','Hold at most one share; pay the fee per completed transaction and maximize final profit.'],[([[1,3,2,8,4,9],2],'Buying at one and four, then selling at eight and nine, yields eight after fees.'), ([[1,3,7,5,10,3],3],'One combined transaction from one to ten yields six.')],[[p,f] for p,f in (([1],0),([1,2],0),([2,1],0),([1,2],2),([1,5,3,8],1),([5,4,3,2,1],1),([1,3,2,8,4,9],0),([1,3,2,8,4,9],10),([2,5,1,7],2),([1,10,1,10],3),([3,3,3],0),([10,1,10,1,10],5))],STOCK,[STOCK_ONCE,STOCK_EACH],['Allows only one transaction and misses multiple profitable trades.','Never subtracts transaction fees.'],stock_oracle,random_stock,*lesson('After each day, only the best cash state and best one-share state matter.','Update cash by selling and holding by buying or keeping.','cash=max(cash,hold+price-fee); hold=max(hold,old_cash-price).','Any longer history ending in the same holding status is dominated by the one with greater profit.'),'O(n)','O(1)',5),
717:entry('final_character_is_one_bit',[('bits','list[int]')],'bool',['arrays','simulation'],['bits is a valid encoding ending in zero.','A zero starts a one-bit character; a one starts a two-bit character. Determine whether the final zero stands alone.'],[([[1,0,0]],'The first two bits form a two-bit character, leaving the final zero alone.'), ([[1,1,1,0]],'The encoding splits as 11 and 10, so the last zero belongs to a two-bit character.')],[[b] for b in ([0],[0,0],[1,0],[0,1,0],[1,1,0],[1,0,0,0],[0,1,1,0],[1,1,0,0],[0,0,1,0],[1,0,1,0,0],[1,1,1,1,0],[0,1,1,1,0])],BITS,[BITS_PREVIOUS,BITS_LAST],['Looks only at the penultimate bit and ignores how preceding ones are grouped.','Returns true for every valid encoding merely because the final bit is zero.'],one_bit_oracle,random_bits,*lesson('Parsing is deterministic because each leading bit fixes the character width.','Walk from the start until reaching or passing the final index.','Advance one on zero and two on one while index<n-1; accept exactly when index==n-1.','There is no branching in a valid encoding, so the unique parse directly reveals whether the final zero begins its own character.'),'O(n)','O(1)',3),
}
