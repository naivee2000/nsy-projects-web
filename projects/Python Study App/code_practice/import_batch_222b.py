"""Sorted submatrices, cyclic shift costs, removable ranges, fruit paths, and chunks."""
from collections import Counter
from itertools import permutations,product
from .import_batch_055 import entry


def sorted_matrix_oracle(args):
    grid,k=args;rows=len(grid);cols=len(grid[0]);answer=0
    for top in range(rows):
        for bottom in range(top,rows):
            for left in range(cols):
                for right in range(left,cols):
                    valid=True
                    for row in range(top,bottom+1):
                        values=grid[row][left:right+1]
                        if max(values)>k or any(values[i]<values[i+1] for i in range(len(values)-1)):valid=False;break
                    answer+=valid
    return answer


def random_sorted_matrix(rng):
    rows=rng.randint(1,4);cols=rng.randint(1,4)
    return [[[rng.randint(1,9) for _ in range(cols)] for _ in range(rows)],rng.randint(1,9)]


def shift_oracle(args):
    s,t,next_cost,previous_cost=args;answer=0
    for source,target in zip(s,t):
        a=ord(source)-97;b=ord(target)-97;forward=backward=0;current=a
        while current!=b:forward+=next_cost[current];current=(current+1)%26
        current=a
        while current!=b:backward+=previous_cost[current];current=(current-1)%26
        answer+=min(forward,backward)
    return answer


def random_shift(rng):
    n=rng.randint(1,12)
    return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n)),''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n)),[rng.randint(0,12) for _ in range(26)],[rng.randint(0,12) for _ in range(26)]]


def removable_oracle(args):
    nums,queries=args;best=None
    for mask in range(1<<len(queries)):
        kept=[queries[i] for i in range(len(queries)) if mask>>i&1]
        if all(sum(left<=index<=right for left,right in kept)>=need for index,need in enumerate(nums)):
            count=len(kept);best=count if best is None else min(best,count)
    return -1 if best is None else len(queries)-best


def random_removable(rng):
    n=rng.randint(1,8);queries=[]
    for _ in range(rng.randint(1,9)):
        left=rng.randrange(n);queries.append([left,rng.randrange(left,n)])
    return [[rng.randint(0,4) for _ in range(n)],queries]


def child_paths(n,start,moves):
    paths=[]
    def visit(path):
        if len(path)==n:
            if path[-1]==(n-1,n-1):paths.append(path)
            return
        row,col=path[-1]
        for dr,dc in moves:
            nr,nc=row+dr,col+dc
            if 0<=nr<n and 0<=nc<n:visit(path+[(nr,nc)])
    visit([start]);return paths


def fruit_oracle(args):
    fruits=args[0];n=len(fruits);diagonal=[(i,i) for i in range(n)]
    upper=child_paths(n,(0,n-1),((1,-1),(1,0),(1,1)))
    lower=child_paths(n,(n-1,0),((-1,1),(0,1),(1,1)))
    return max(sum(fruits[row][col] for row,col in set(diagonal+first+second)) for first in upper for second in lower)


def random_fruit(rng):
    n=rng.randint(2,5);return [[[rng.randint(0,9) for _ in range(n)] for _ in range(n)]]


def chunk_oracle(args):
    s,t,k=args;size=len(s)//k;chunks=[s[i:i+size] for i in range(0,len(s),size)]
    return any(''.join(order)==t for order in set(permutations(chunks)))


def random_chunk(rng):
    k=rng.randint(1,6);size=rng.randint(1,4);chunks=[''.join(rng.choice('abc') for _ in range(size)) for _ in range(k)]
    s=''.join(chunks);letters=list(s);rng.shuffle(letters);t=''.join(letters)
    return [s,t,k]


SORTED_MATRIX='''def count_sorted_bounded_submatrices(grid,k):
    rows=len(grid);cols=len(grid[0]);width=[0]*rows;answer=0
    for column in range(cols):
        for row in range(rows):
            if grid[row][column]>k:width[row]=0
            elif column and grid[row][column-1]>=grid[row][column]:width[row]+=1
            else:width[row]=1
        stack=[];ending_sum=0
        for value in width:
            count=1
            while stack and stack[-1][0]>=value:
                old,amount=stack.pop();ending_sum-=old*amount;count+=amount
            stack.append((value,count));ending_sum+=value*count;answer+=ending_sum
    return answer
'''

SHIFT='''def minimum_cyclic_shift_cost(s,t,next_cost,previous_cost):
    forward=[0]*53;backward=[0]*53
    for index in range(52):
        forward[index+1]=forward[index]+next_cost[index%26]
        backward[index+1]=backward[index]+previous_cost[(index+1)%26]
    answer=0
    for source,target in zip(s,t):
        a=ord(source)-97;b=ord(target)-97
        clockwise=forward[b+26 if b<a else b]-forward[a]
        counter=backward[a+26 if a<b else a]-backward[b]
        answer+=min(clockwise,counter)
    return answer
'''

REMOVABLE='''def maximum_removable_zero_queries(nums,queries):
    import heapq
    ordered=sorted(queries);heap=[];ending=[0]*(len(nums)+1);active=cursor=selected=0
    for index,need in enumerate(nums):
        active+=ending[index]
        while cursor<len(ordered) and ordered[cursor][0]<=index:
            heapq.heappush(heap,-ordered[cursor][1]);cursor+=1
        while active<need and heap and -heap[0]>=index:
            right=-heapq.heappop(heap);active+=1;selected+=1;ending[right+1]-=1
        if active<need:return -1
    return len(queries)-selected
'''

FRUIT='''def maximum_three_child_fruits(fruits):
    n=len(fruits);negative=-10**30;upper=[negative]*n;upper[n-1]=fruits[0][n-1]
    for row in range(1,n-1):
        current=[negative]*n
        for column in range(row+1,n):
            current[column]=max(upper[column],upper[column-1],upper[column+1] if column+1<n else negative)+fruits[row][column]
        upper=current
    lower=[negative]*n;lower[n-1]=fruits[n-1][0]
    for column in range(1,n-1):
        current=[negative]*n
        for row in range(column+1,n):
            current[row]=max(lower[row],lower[row-1],lower[row+1] if row+1<n else negative)+fruits[row][column]
        lower=current
    return sum(fruits[i][i] for i in range(n))+upper[n-1]+lower[n-1]
'''

CHUNKS='''def can_rearrange_equal_chunks(s,t,k):
    from collections import Counter
    size=len(s)//k
    return Counter(s[index:index+size] for index in range(0,len(s),size))==Counter(t[index:index+size] for index in range(0,len(t),size))
'''


def lesson(a,b,c,d):return [a,b,c,d]


MATRIX_CASES=[[g,k] for g,k in [([[1]],1),([[2]],1),([[3,2,1]],3),([[1,2,3]],3),([[3],[2],[1]],2),([[1,1],[1,1]],1),([[2,1],[3,2]],2),([[3,2],[1,2]],3),([[5,4,3],[2,2,1]],4),([[1,3],[2,1]],2),([[9,8],[7,6]],5),([[4,3,2],[4,2,1],[5,3,1]],4),([[1,2],[2,1],[1,1]],1),([[6,5,7],[4,3,2]],6)]]
ONES=[1]*26;ZERO=[0]*26
SHIFT_CASES=[[s,t,n,p] for s,t,n,p in [('a','a',ONES,ONES),('a','b',ONES,ONES),('a','z',ONES,ONES),('z','a',ONES,ONES),('abc','bcd',ONES,ONES),('xyz','abc',ONES,ONES),('az','za',[i for i in range(26)],[25-i for i in range(26)]),('hello','world',ONES,ONES),('aaa','bbb',[5]*26,[1]*26),('mmm','aaa',[2]*26,[3]*26),('code','code',ZERO,ZERO),('q','e',[i%5 for i in range(26)],[i%7 for i in range(26)]),('wrap','wxyz',[3]*26,[4]*26),('leetcode','practice',[1+(i%3) for i in range(26)],[1+(i%4) for i in range(26)])]]
REMOVABLE_CASES=[[a,q] for a,q in [([0],[[0,0]]),([1],[[0,0]]),([2],[[0,0]]),([2],[[0,0],[0,0]]),([1,1],[[0,1]]),([1,2],[[0,1],[1,1]]),([1,1,1],[[0,2],[0,1],[1,2]]),([2,0,2],[[0,2],[0,2],[1,1],[0,0]]),([3,1],[[0,1],[0,0],[0,0]]),([1,2,1],[[0,2],[1,1],[0,2]]),([0,0],[[0,0],[1,1],[0,1]]),([4],[[0,0]]*4),([2,3,2],[[0,2],[1,2],[0,1],[1,1]]),([1,1,2,1],[[0,3],[2,2],[1,3]])]]
FRUIT_CASES=[[[row[:] for row in grid]] for grid in [[[1,1],[1,2]],[[0,0],[0,0]],[[1,2],[3,4]],[[1,2,3],[4,5,6],[7,8,9]],[[9,0,1],[0,9,0],[1,0,9]],[[1,9,1],[2,1,8],[7,6,3]],[[0,1,0],[5,0,4],[0,3,0]],[[1,2,3,4],[4,3,2,1],[5,6,7,8],[8,7,6,5]],[[9,1,1,1],[1,9,1,8],[1,1,9,8],[7,7,7,9]],[[0,5,0,2],[4,0,6,0],[0,7,0,8],[3,0,9,0]],[[2,2,2],[2,2,2],[2,2,2]],[[1,0,0,1],[0,1,1,0],[0,1,1,0],[1,0,0,1]],[[3,1,4],[1,5,9],[2,6,5]],[[8,0],[0,7]]]]
CHUNK_CASES=[[s,t,k] for s,t,k in [('a','a',1),('ab','ba',1),('ab','ba',2),('abcd','abdc',2),('aabbcc','ccbbaa',3),('abcabc','abcabc',2),('abcabc','bcabca',3),('aaaa','aaaa',4),('aabb','bbaa',2),('abcdef','defabc',2),('abcdef','badcfe',3),('abab','baba',2),('aaabbb','ababab',3),('abcdabcd','cdabcdab',4)]]


BATCH={
3359:entry('count_sorted_bounded_submatrices',[('grid','list[list[int]]'),('k','int')],'int',['matrices','monotonic stacks','dynamic programming'],['grid has 1–1,000 rows and columns with positive values; k is positive.','Count rectangular submatrices whose maximum is at most k and whose values in every selected row are non-increasing left to right.','Single-cell submatrices satisfy the ordering condition when their value is at most k.'],[([[[4,3,2,1],[8,7,6,1]],3],'Eight rectangles lie entirely in bounded row segments that never increase to the right.'),([[[1,1,1],[1,1,1],[1,1,1]],1],'Every one of the 36 rectangular submatrices is bounded and row-wise non-increasing.')],MATRIX_CASES,SORTED_MATRIX,[SORTED_MATRIX.replace('grid[row][column-1]>=grid[row][column]','grid[row][column-1]>grid[row][column]'),SORTED_MATRIX.replace('stack[-1][0]>=value','stack[-1][0]<=value')],['Requires strict decreases and incorrectly breaks equal adjacent values.','Maintains maxima instead of minima across row intervals.'],sorted_matrix_oracle,random_sorted_matrix,lesson('For each right column, every row has a maximum valid width ending there.','A rectangle’s valid left choices equal the minimum width across its selected row interval.','Update row widths from the bound and non-increasing rule, then sum all contiguous-row subarray minima with a monotonic stack.','Each rectangle is counted at its unique right edge, and its limiting row width gives exactly its allowed left edges.'),'O(rows*cols)','O(rows)',8),
3361:entry('minimum_cyclic_shift_cost',[('s','str'),('t','str'),('next_cost','list[int]'),('previous_cost','list[int]')],'int',['strings','prefix sums'],['s and t have the same length up to 100,000; both cost arrays contain 26 nonnegative values.','Moving forward from letter j costs next_cost[j]; moving backward from j costs previous_cost[j], with alphabet wraparound.','Return the sum of the cheaper directional route for every independent character position.'],[(['abab','baba',[100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[1,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],'The cheapest wrapped routes cost one, zero, one, and zero, totaling two.'),(['leet','code',ONES,ONES],'The four shortest cyclic distances are 9,10,1,11, totaling 31.')],SHIFT_CASES,SHIFT,[SHIFT.replace('previous_cost[(index+1)%26]','previous_cost[index%26]'),SHIFT.replace('min(clockwise,counter)','clockwise')],['Charges the backward edge using its destination rather than source letter.','Always shifts forward even when the backward route is cheaper.'],shift_oracle,random_shift,lesson('Every character transforms independently along a 26-node weighted cycle.','Duplicate the alphabet and prefix-sum forward and backward edge costs to handle wraparound.','Compute both directional interval costs for each source-target pair and add their minimum.','A cycle has exactly two simple directional routes; nonnegative costs make the cheaper one optimal.'),'O(len(s)+26)','O(26)',5),
3362:entry('maximum_removable_zero_queries',[('nums','list[int]'),('queries','list[list[int]]')],'int',['arrays','greedy','priority queues'],['nums and queries each contain up to 100,000 entries.','A retained range may independently decrement every covered index by zero or one.','Remove as many whole queries as possible while retaining enough coverage at every index, or return -1.'],[([[2,0,2],[[0,2],[0,2],[1,1]]],'The two full ranges satisfy indices zero and two, so the middle-only query is removable.'),([[1,1,1,1],[[1,3],[0,2],[1,3],[1,2]]],'Keeping ranges [0,2] and [1,3] covers all indices, allowing two removals.')],REMOVABLE_CASES,REMOVABLE,[REMOVABLE.replace('heapq.heappush(heap,-ordered[cursor][1])','heapq.heappush(heap,ordered[cursor][1])').replace('-heap[0]>=index','heap[0]>=index').replace('right=-heapq.heappop(heap)','right=heapq.heappop(heap)'),REMOVABLE.replace('ending[right+1]-=1','ending[right]-=1')],['Selects the earliest-ending available range instead of preserving the farthest reach.','Expires a selected inclusive range at its final covered index.'],removable_oracle,random_removable,lesson('When index i lacks coverage, some currently available query must be kept.','Choose the range ending farthest right so the forced selection helps the most future indices.','Sort by start, push eligible ends into a max-heap, and record each selected range’s expiration in a difference array.','The exchange choice never hurts current coverage and dominates any shorter available range for every later position.'),'O((n+q) log q)','O(n+q)',6),
3363:entry('maximum_three_child_fruits',[('fruits','list[list[int]]')],'int',['matrices','dynamic programming','paths'],['fruits is an n by n nonnegative matrix with 2 <= n <= 1,000.','Three children start at the top-left, top-right, and bottom-left and make exactly n-1 allowed moves to bottom-right.','A room’s fruit counts once even if several children visit it; maximize the collected total.'],[([[[1,2,3,4],[5,6,8,7],[9,10,11,12],[13,14,15,16]]],'The diagonal child and optimal upper-right and lower-left paths collect ten distinct rooms totaling 100.'),([[[1,1],[1,1]]],'The starts and shared destination cover all four rooms exactly once.')],FRUIT_CASES,FRUIT,[FRUIT.replace('upper[n-1]=fruits[0][n-1]','upper[n-1]=0'),FRUIT.replace('upper[n-1]+lower[n-1]','max(upper[n-1],lower[n-1])')],['Omits the fruit in the upper child’s starting room.','Keeps only one side child’s contribution instead of both disjoint triangular paths.'],fruit_oracle,random_fruit,lesson('Exactly n-1 moves force the top-left child to follow the main diagonal.','The other children remain in disjoint triangles until the shared destination, so optimize their paths independently.','Run row-wise DP above the diagonal and column-wise DP below it; add both pre-destination scores to the diagonal sum.','Triangle separation prevents double counting, and each DP transition enumerates the three legal predecessor positions.'),'O(n²)','O(n)',8),
3365:entry('can_rearrange_equal_chunks',[('s','str'),('t','str'),('k','int')],'bool',['strings','hash maps'],['s and t are equal-length lowercase anagrams of length up to 200,000; k divides their length.','Split both strings at the same k equal-size block boundaries.','Return whether reordering whole blocks from s, without editing inside a block, can form t.'],[(['abcd','cdab',2],'The source blocks ab and cd can be swapped to form target blocks cd and ab.'),(['aabbcc','bbaacc',3],'Both strings contain exactly the length-two blocks aa, bb, and cc.')],CHUNK_CASES,CHUNKS,[CHUNKS.replace('len(s)//k','k'),CHUNKS.replace('Counter(s[index:index+size]','Counter(\"\".join(sorted(s[index:index+size]))')],['Uses k as the block length rather than the number of blocks.','Sorts characters inside each block even though internal block order must remain unchanged.'],chunk_oracle,random_chunk,lesson('Only block order may change, so the multiset of exact block strings is invariant.','Slice both strings with block length len(s)/k and compare frequency maps.','Count every aligned block in s and t; equality of the two counters is the answer.','Equal multisets can be paired and reordered to match target order; any differing block count makes construction impossible.'),'O(n)','O(k)',5),
}
