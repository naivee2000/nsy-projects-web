"""Monotonic-stack, functional-graph, route-DP, greedy split, and digit-DP imports."""
from functools import lru_cache

from .import_batch_055 import entry


def books_oracle(args):
    books=args[0];best=0
    for right in range(len(books)):
        taken=books[right];total=taken;best=max(best,total)
        for left in range(right-1,-1,-1):
            taken=min(books[left],taken-1)
            if taken<=0:break
            total+=taken;best=max(best,total)
    return best


def random_books(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,20))]]


def cycle_oracle(args):
    edges=args[0];best=-1
    for start in range(len(edges)):
        order={};node=start;step=0
        while node!=-1 and node not in order:
            order[node]=step;step+=1;node=edges[node]
        if node in order:best=max(best,step-order[node])
    return best


def random_cycle(rng):
    size=rng.randint(2,20)
    return [[rng.randint(-1,size-1) for _ in range(size)]]


def train_oracle(args):
    regular,express,fee=args;states={(0,False):0};answer=[]
    for index in range(len(regular)):
        following={}
        for (_,on_express),cost in states.items():
            following[(index+1,False)]=min(following.get((index+1,False),10**30),cost+regular[index])
            following[(index+1,True)]=min(following.get((index+1,True),10**30),cost+express[index]+(0 if on_express else fee))
        states=following;answer.append(min(states.values()))
    return answer


def random_train(rng):
    size=rng.randint(1,12)
    return [[rng.randint(1,20) for _ in range(size)],[rng.randint(1,20) for _ in range(size)],rng.randint(1,20)]


def replacement_oracle(args):
    nums=args[0]
    @lru_cache(None)
    def visit(index,maximum):
        if index<0:return 0
        value=nums[index];best=10**9
        for parts in range(1,value+1):
            if (value+parts-1)//parts<=maximum:
                best=min(best,parts-1+visit(index-1,value//parts))
        return best
    return visit(len(nums)-2,nums[-1])


def random_replacement(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,8))]]


def special_oracle(args):
    return sum(len(set(str(value)))==len(str(value)) for value in range(1,args[0]+1))


def random_special(rng):return [rng.randint(1,5000)]


BOOKS='''def maximum_books_taken(books):
    stack=[];dp=[0]*len(books);answer=0
    for index,value in enumerate(books):
        while stack and books[stack[-1]]-stack[-1]>=value-index:stack.pop()
        previous=stack[-1] if stack else -1;length=min(value,index-previous);first=value-length+1
        total=(first+value)*length//2
        if previous>=0 and index-previous<=value:total+=dp[previous]
        dp[index]=total;answer=max(answer,total);stack.append(index)
    return answer
'''

BOOKS_ONE='''def maximum_books_taken(books):
    return max(books)
'''

BOOKS_ALL='''def maximum_books_taken(books):
    return sum(books)
'''

CYCLE='''def longest_directed_cycle(edges):
    visited=[False]*len(edges);answer=-1
    for start in range(len(edges)):
        if visited[start]:continue
        step={};node=start
        while node!=-1 and not visited[node]:
            visited[node]=True;step[node]=len(step);node=edges[node]
        if node in step:answer=max(answer,len(step)-step[node])
    return answer
'''

CYCLE_TAIL='''def longest_directed_cycle(edges):
    answer=-1
    for start in range(len(edges)):
        seen=set();node=start
        while node!=-1 and node not in seen:
            seen.add(node);node=edges[node]
        if node!=-1:answer=max(answer,len(seen))
    return answer
'''

CYCLE_PAIRS='''def longest_directed_cycle(edges):
    return 2 if any(target!=-1 and edges[target]==index for index,target in enumerate(edges)) else -1
'''

TRAIN='''def minimum_train_costs(regular,express,express_cost):
    regular_state=0;express_state=express_cost;answer=[]
    for ordinary,fast in zip(regular,express):
        next_regular=min(regular_state,express_state)+ordinary
        next_express=min(express_state+fast,regular_state+express_cost+fast)
        regular_state,express_state=next_regular,next_express;answer.append(min(regular_state,express_state))
    return answer
'''

REPLACE='''def minimum_sorting_replacements(nums):
    operations=0;maximum=nums[-1]
    for value in reversed(nums[:-1]):
        parts=(value+maximum-1)//maximum;operations+=parts-1;maximum=value//parts
    return operations
'''

REPLACE_FIXED_BOUND='''def minimum_sorting_replacements(nums):
    operations=0;maximum=nums[-1]
    for value in reversed(nums[:-1]):
        parts=(value+maximum-1)//maximum;operations+=parts-1
    return operations
'''

REPLACE_FLOOR='''def minimum_sorting_replacements(nums):
    operations=0;maximum=nums[-1]
    for value in reversed(nums[:-1]):
        parts=max(1,value//maximum);operations+=parts-1;maximum=value//parts
    return operations
'''

SPECIAL='''def count_distinct_digit_integers(n):
    from functools import lru_cache
    digits=list(map(int,str(n)))
    @lru_cache(None)
    def visit(index,mask,tight,started):
        if index==len(digits):return int(started)
        answer=0;limit=digits[index] if tight else 9
        for digit in range(limit+1):
            following_tight=tight and digit==limit
            if not started and digit==0:answer+=visit(index+1,mask,following_tight,False)
            elif not mask>>digit&1:answer+=visit(index+1,mask|1<<digit,following_tight,True)
        return answer
    return visit(0,0,True,False)
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2355:entry('maximum_books_taken',[('books','list[int]')],'int',['arrays','monotonic stacks','dynamic programming'],['books has 1 through 100000 positive shelf counts.','Choose a contiguous shelf segment and positive take counts that strictly increase from left to right without exceeding each shelf.','Return the maximum total books taken.'],[([[8,5,2,7,9]],'Taking one, two, seven, and nine from shelves one through four gives nineteen.'),([[7,1,3,4,5]],'The final four shelves permit taking one, three, four, and five for thirteen.')],[[x] for x in [[1],[5],[1,1],[1,2],[2,1],[1,2,3],[3,2,1],[5,1,5],[2,4,6,8],[8,6,4,2],[3,1,4,1,5],[10,2,3,4],[1,10,10,10],[4,7,2,9,10]]],BOOKS,[BOOKS_ONE,BOOKS_ALL],['Chooses only one shelf and misses profitable increasing multi-shelf segments.','Takes every book without enforcing strictly increasing take counts.'],books_oracle,random_books,lesson('If a segment ends at shelf i taking books[i], optimal earlier takes decrease by one until capped by a shelf or by one.','Compare transformed values books[i]-i with a monotonic stack to find the preceding constraining shelf.','Sum the arithmetic tail ending at books[i], and add the best compatible prefix when that preceding shelf remains connected.','The nearest smaller transformed value is exactly the first shelf whose capacity beats the backward arithmetic requirement; DP joins the independent prefix and forced tail.'),'O(n)','O(n)',8),
2360:entry('longest_directed_cycle',[('edges','list[int]')],'int',['graphs','depth-first search','functional graphs'],['edges has 2 through 100000 entries; edges[i] is -1 or one outgoing neighbor distinct from i.','Return the number of vertices in the longest directed cycle.','Return -1 when the graph has no cycle.'],[([[3,3,4,2,3]],'Vertices two, four, and three form a directed cycle of length three.'),([[2,-1,3,1]],'Every path eventually reaches node one and stops, so there is no cycle.')],[[e] for e in [[-1,-1],[1,-1],[1,0],[1,2,0],[2,0,1],[3,3,4,2,3],[2,-1,3,1],[1,2,3,0],[1,2,-1,2],[2,3,1,-1],[4,0,1,2,3],[1,0,3,2],[2,3,4,2,-1],[5,2,3,4,1,0]]],CYCLE,[CYCLE_TAIL,CYCLE_PAIRS],['Counts the noncyclic tail leading into a cycle as part of its length.','Recognizes only mutual two-node cycles and misses cycles of every other length.'],cycle_oracle,random_cycle,lesson('A cycle counts only when the current walk revisits one of its own nodes.','Keep both global visited state and a map from current-walk nodes to their step index.','Walk outgoing edges until -1 or a visited node; if that endpoint is in the current map, subtract its first step.','Outdegree at most one makes each start a single path, and global marking ensures every vertex is processed once.'),'O(n)','O(n)',8),
2361:entry('minimum_train_costs',[('regular','list[int]'),('express','list[int]'),('express_cost','int')],'list[int]',['dynamic programming','arrays'],['regular and express have equal length n and give segment costs from stop i-1 to i.','Start on regular at stop zero; entering express costs express_cost, while returning to regular is free.','Return the minimum cost to reach each stop one through n on either route.'],[([[1,6,9,5],[5,2,3,10],8],'Tracking both route states yields minimum prefix costs one, seven, fourteen, and nineteen.'),([[1,1,1],[2,2,2],1],'Regular travel remains cheapest at every stop, giving one, two, and three.')],[[r,e,c] for r,e,c in [([1],[1],1),([5],[1],2),([1],[5],2),([1,1],[1,1],1),([10,10],[1,1],5),([1,10],[10,1],2),([5,1,5],[1,5,1],3),([2,2,2],[3,1,3],1),([9,1,9,1],[1,9,1,9],4),([1,2,3,4],[4,3,2,1],2),([100,1],[1,100],10),([3,3,3],[2,2,2],100),([8,6,4,2],[1,3,5,7],5),([1,20,1,20],[20,1,20,1],3)]],TRAIN,[TRAIN.replace('regular_state+express_cost+fast','regular_state+fast'),TRAIN.replace('min(regular_state,express_state)+ordinary','regular_state+ordinary')],['Enters the express route from regular without paying the transfer fee.','Forbids the free transfer from express back to regular before a segment.'],train_oracle,random_train,lesson('At each stop retain the cheapest cost ending on each route.','Regular can be entered freely; express can be continued or entered by paying its fee.','Compute next_regular=min(states)+regular[i] and next_express=min(express+fast,regular+fee+fast).','These two states cover every route history by its current line, and keeping only the cheaper history for a line is safe because future costs depend only on that line.'),'O(n)','O(1) excluding output',5),
2366:entry('minimum_sorting_replacements',[('nums','list[int]')],'int',['arrays','greedy','math'],['nums has 1 through 100000 positive integers.','One operation splits one value into two positive values with the same sum; repeat as needed.','Minimize operations so the resulting sequence is nondecreasing.'],[([[3,9,3]],'Split nine into three equal parts using two operations, yielding all threes.'),([[1,2,3,4,5]],'The input is already nondecreasing, so no split is needed.')],[[x] for x in [[1],[2,1],[1,2],[3,9,3],[10,1],[5,2],[7,3],[8,3,2],[4,4,4],[1,10,5],[9,8,7,6],[100,10,1],[2,100,99],[20,15,10,5]]],REPLACE,[REPLACE_FLOOR,REPLACE_FIXED_BOUND],['Uses floor division and may leave a generated part above the right-side limit.','Never lowers the right-side bound after splitting, so earlier values may remain too large.'],replacement_oracle,random_replacement,lesson('Work right-to-left with the maximum value the current element’s parts may have.','Use the fewest parts whose ceiling size is at most that maximum.','parts=ceil(value/maximum); add parts-1 operations; the smallest resulting part value//parts becomes the new bound.','Balanced parts maximize the smallest part for a fixed count, preserving the loosest possible bound for earlier elements, so the greedy choice cannot hurt the prefix.'),'O(n)','O(1)',8),
2376:entry('count_distinct_digit_integers',[('n','int')],'int',['digit dynamic programming','bitmasks','counting'],['1 <= n <= 2*10^9.','A positive integer is special when none of its decimal digits repeat.','Return the count of special integers from one through n inclusive.'],[([20],'Every positive integer through twenty except eleven has distinct digits, giving nineteen.'),([135],'Digit counting finds 110 special positive integers no greater than 135.')],[[n] for n in [1,5,9,10,11,20,99,100,101,110,135,999,1000,5432]],SPECIAL,[SPECIAL.replace('elif not mask>>digit&1','elif True'),SPECIAL.replace('return int(started)','return 1')],['Never checks the used-digit mask and counts numbers with repeated digits.','Counts the all-leading-zero construction as the positive integer zero.'],special_oracle,random_special,lesson('Process decimal positions while remembering used digits, whether the number has started, and whether the prefix equals n.','A ten-bit mask rejects repeated non-leading digits.','Digit DP tries 0 through the tight limit; leading zeros do not enter the mask; the terminal state counts only started numbers.','Every integer at most n has one padded digit path, tightness enforces the upper bound, and the mask accepts exactly distinct-digit paths.'),'O(digits*2^10*20)','O(digits*2^10)',8),
}
