"""Set quotas, monochrome subtrees, string matches, and binary price search."""
from itertools import combinations

from .import_batch_055 import entry


def set_oracle(args):
    first, second = args; keep = len(first) // 2; answer = 0
    for left in combinations(range(len(first)), keep):
        left_values = {first[index] for index in left}
        for right in combinations(range(len(second)), keep):
            answer = max(answer, len(left_values | {second[index] for index in right}))
    return answer


def random_set(rng):
    size = 2 * rng.randint(1, 4)
    return [[rng.randint(1, 8) for _ in range(size)], [rng.randint(1, 8) for _ in range(size)]]


def subtree_oracle(args):
    edges, colors = args; size = len(colors); children = [[] for _ in range(size)]
    graph = [[] for _ in range(size)]
    for left, right in edges:
        graph[left].append(right); graph[right].append(left)
    parent = [-1] * size; order = [0]
    for node in order:
        for following in graph[node]:
            if following != parent[node]:
                parent[following] = node; children[node].append(following); order.append(following)
    answer = 1
    for root in range(size):
        stack = [root]; descendants = []
        while stack:
            node = stack.pop(); descendants.append(node); stack.extend(children[node])
        if all(colors[node] == colors[root] for node in descendants):
            answer = max(answer, len(descendants))
    return answer


def random_subtree(rng):
    size = rng.randint(1, 20)
    edges = [[node, rng.randrange(node)] for node in range(1, size)]
    rng.shuffle(edges)
    return [edges, [rng.randint(1, 4) for _ in range(size)]]


def beautiful_oracle(args):
    text, first, second, distance = args
    first_starts = [index for index in range(len(text) - len(first) + 1) if text.startswith(first, index)]
    second_starts = [index for index in range(len(text) - len(second) + 1) if text.startswith(second, index)]
    return [index for index in first_starts if any(abs(index - other) <= distance for other in second_starts)]


def random_beautiful(rng):
    text = ''.join(rng.choice('abcd') for _ in range(rng.randint(1, 28)))
    first = ''.join(rng.choice('abcd') for _ in range(rng.randint(1, min(6, len(text)))))
    second = ''.join(rng.choice('abcd') for _ in range(rng.randint(1, min(6, len(text)))))
    return [text, first, second, rng.randint(1, len(text))]


def price_oracle(args):
    budget, interval = args; total = number = 0
    while True:
        candidate = number + 1
        price = sum((candidate >> (position - 1)) & 1
                    for position in range(interval, candidate.bit_length() + 1, interval))
        if total + price > budget:
            return number
        total += price; number = candidate


def random_price(rng):
    return [rng.randint(1, 350), rng.randint(1, 8)]


MAX_SET = '''def maximum_set_after_half_removals(nums1,nums2):
    first=set(nums1);second=set(nums2);capacity=len(nums1)//2
    unique_first=min(len(first-second),capacity)
    unique_second=min(len(second-first),capacity)
    return min(len(nums1),unique_first+unique_second+len(first&second))
'''


SUBTREE = '''def largest_same_color_subtree(edges,colors):
    graph=[[] for _ in colors]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    answer=1
    def visit(node,parent):
        nonlocal answer
        size=1;same=True
        for child in graph[node]:
            if child==parent:continue
            child_size,valid=visit(child,node);size+=child_size
            same=same and valid and colors[child]==colors[node]
        if same:answer=max(answer,size)
        return size,same
    visit(0,-1)
    return answer
'''


BEAUTIFUL_SIMPLE = '''def beautiful_indices_small(s,a,b,k):
    first=[index for index in range(len(s)-len(a)+1) if s.startswith(a,index)]
    second=[index for index in range(len(s)-len(b)+1) if s.startswith(b,index)]
    return [index for index in first if any(abs(index-other)<=k for other in second)]
'''


BEAUTIFUL_FAST = '''def beautiful_indices_large(s,a,b,k):
    def matches(pattern):
        combined=pattern+'#'+s;prefix=[0]*len(combined);answer=[]
        for index in range(1,len(combined)):
            length=prefix[index-1]
            while length and combined[index]!=combined[length]:length=prefix[length-1]
            if combined[index]==combined[length]:length+=1
            prefix[index]=length
            if length==len(pattern):answer.append(index-2*len(pattern))
        return answer
    first=matches(a);second=matches(b);answer=[];pointer=0
    for index in first:
        while pointer<len(second) and second[pointer]<index-k:pointer+=1
        if pointer<len(second) and second[pointer]<=index+k:answer.append(index)
    return answer
'''


PRICE = '''def maximum_cheap_number(k,x):
    def accumulated(number):
        total=0;position=x
        while 1<<(position-1)<=number:
            half=1<<(position-1);cycle=half*2
            total+=(number+1)//cycle*half+max(0,(number+1)%cycle-half)
            position+=x
        return total
    high=1
    while accumulated(high)<=k:high*=2
    low=0
    while low<high:
        middle=(low+high+1)//2
        if accumulated(middle)<=k:low=middle
        else:high=middle-1
    return low
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BEAUTIFUL_CASES = [[s,a,b,k] for s,a,b,k in [
    ('a','a','a',1),('abcd','a','a',4),('abcd','a','d',2),('abcd','a','d',3),
    ('aaaaa','aa','aaa',1),('ababab','ab','ba',1),('ababab','ab','ba',0),
    ('abcabc','abc','cab',2),('mississippi','issi','ss',3),('zzxyzz','zz','xy',2),
    ('leetcode','code','leet',4),('abcdeabcde','abc','cde',3),
    ('aabaacaabaa','aabaa','aca',4),('xyzxyzxyz','xyz','yzx',1)]]


BATCH = {
3002: entry('maximum_set_after_half_removals',[('nums1','list[int]'),('nums2','list[int]')],'int',['sets','greedy','arrays'],['Both arrays have the same positive even length n.','Keep exactly n/2 entries from each array and insert all kept values into one set.','Return the largest possible number of distinct values.'],[([[1,2,1,2],[1,1,1,1]],'Keep value two from the first array and value one from the second, producing two distinct values.'),([[1,2,3,4,5,6],[2,3,2,3,2,3]],'Three first-only values plus shared values two and three produce the maximum size five.')],[[a,b] for a,b in [([1,1],[1,1]),([1,2],[3,4]),([1,2],[1,2]),([1,1,2,2],[2,2,3,3]),([1,2,3,4],[1,2,3,4]),([1,1,1,2],[2,3,3,3]),([1,2,3,4],[5,6,7,8]),([1,1,2,3,4,4],[3,3,5,5,6,6]),([1,2,3,4,5,6],[7,8,9,10,11,12]),([1,1,2,2,3,3],[4,4,5,5,6,6]),([9,9,9,9],[8,8,7,7]),([1,2,2,3,3,4],[3,4,4,5,5,6]),([10,20,10,30],[20,40,20,50]),([1,2,3,1,2,3,4,5],[3,4,5,6,7,3,4,5])]],MAX_SET,[MAX_SET.replace('first-second','first'),MAX_SET.replace('min(len(nums1),','') .replace('))\n',')\n',1)],['Counts shared values as first-array-only choices and may exceed that array’s quota.','Does not cap the combined distinct count by the total number of retained entries.'],set_oracle,random_set,lesson('Values unique to one array should consume that array’s quota before shared values do.','Take as many exclusive distinct values as each half-capacity permits, then fill remaining global slots with shared values.','a=min(|S1-S2|,n/2), b=min(|S2-S1|,n/2); answer=min(n,a+b+|S1∩S2|).','Exclusive choices cannot be supplied by the other array and never conflict; shared values fill only leftover capacity, with n as the unavoidable total-entry bound.'),'O(n)','O(n)',5),
3004: entry('largest_same_color_subtree',[('edges','list[list[int]]'),('colors','list[int]')],'int',['trees','recursion','depth-first search'],['edges form an undirected tree rooted at node zero and colors has one positive integer per node.','A node’s subtree contains that node and all descendants under the root-zero orientation.','Return the maximum size of a subtree whose every node has one color.'],[([[[0,1],[0,2],[0,3]],[1,1,2,3]],'The root subtree mixes colors, while each leaf alone is monochrome, so the maximum is one.'),([[[0,1],[0,2],[2,3],[2,4]],[1,2,3,3,3]],'The subtree rooted at node two contains three nodes, all color three.')],[[e,c] for e,c in [([], [1]),([[0,1]],[1,1]),([[0,1]],[1,2]),([[0,1],[1,2]],[2,2,2]),([[0,1],[1,2]],[2,2,3]),([[0,1],[0,2]],[1,1,1]),([[0,1],[0,2]],[1,2,1]),([[0,1],[1,2],[1,3]],[4,4,4,4]),([[0,1],[1,2],[1,3]],[4,4,5,4]),([[0,1],[0,2],[2,3],[2,4]],[1,1,2,2,2]),([[0,1],[0,2],[1,3],[1,4]],[7,7,8,7,7]),([[0,1],[1,2],[2,3],[3,4]],[3,3,3,3,3]),([[0,1],[1,2],[2,3],[3,4]],[3,3,2,3,3]),([[0,1],[0,2],[0,3],[3,4],[3,5]],[1,2,2,3,3,3])]],SUBTREE,[SUBTREE.replace('same and valid and colors[child]==colors[node]','same and colors[child]==colors[node]'),SUBTREE.replace('size+=child_size','size+=1')],['Checks only each child root color and ignores a different-colored deeper descendant.','Counts immediate children rather than the full recursive subtree size.'],subtree_oracle,random_subtree,lesson('A subtree is monochrome only if every child subtree is monochrome and each child root matches its parent.','Use postorder recursion returning both subtree size and a validity flag.','Combine child sizes; AND their flags and color comparisons; update the maximum only when valid.','Postorder has complete information for every descendant, and the recursive condition is exactly necessary and sufficient for the rooted subtree to share one color.'),'O(n)','O(n)',5),
3006: entry('beautiful_indices_small',[('s','str'),('a','str'),('b','str'),('k','int')],'list[int]',['strings','enumeration','two pointers'],['s, a, and b are lowercase strings; a and b have length at most ten; k is nonnegative.','Index i must start an occurrence of a and lie within k positions of some start of b.','Return all qualifying a-start indices in ascending order.'],[(['isawsquirrelnearmysquirrelhouseohmy','my','squirrel',15],'The my occurrences at sixteen and thirty-three are within fifteen start positions of squirrel occurrences at four and eighteen.'),(['abcd','a','a',4],'The shared occurrence at index zero witnesses its own distance zero, so zero is beautiful.')],BEAUTIFUL_CASES,BEAUTIFUL_SIMPLE,[BEAUTIFUL_SIMPLE.replace('<=k','<k'),BEAUTIFUL_SIMPLE.replace('abs(index-other)','abs(index+len(a)-other)')],['Treats the allowed distance k as strict and loses boundary matches.','Measures from the end of a instead of comparing substring start indices.'],beautiful_oracle,random_beautiful,lesson('Occurrence starts can be enumerated directly because the short patterns bound each comparison.','Collect every start of a and b, then retain a starts having any b start within k.','Use startswith at each legal start; for each a index test abs(i-j)<=k over b starts.','The occurrence lists contain exactly all possible witnesses, and the direct distance test matches the definition.'),'O(n*(|a|+|b|)+occurrences product)','O(n)',5),
3007: entry('maximum_cheap_number',[('k','int'),('x','int')],'int',['binary search','bit counting','math'],['k is positive and x is between one and eight.','Bit positions are one-indexed from the least significant bit; a number’s price counts set bits at positions x,2x,3x,...','Return the largest n whose total price over all integers from one through n is at most k.'],[([9,1],'Prices through six sum to nine, while adding seven raises the accumulated price to twelve.'),([7,2],'The accumulated price through nine is six, but through ten is eight, so nine is greatest.')],[[k,x] for k,x in [(1,1),(2,1),(3,1),(10,1),(20,1),(1,2),(2,2),(5,2),(10,2),(25,3),(50,4),(100,5),(250,7),(1000,8)]],PRICE,[PRICE.replace('position=x','position=x+1'),PRICE.replace('(number+1)//cycle','number//cycle').replace('(number+1)%cycle','number%cycle')],['Starts the priced bit sequence one position too high.','Counts complete and partial bit cycles only through number-1, creating an off-by-one accumulated price.'],price_oracle,random_price,lesson('Set bits at one fixed position follow periodic blocks of zeros then ones.','Count each priced position over 0..n in O(log n), then binary-search the monotone accumulated total.','For each position p=x,2x,... add full one-block cycles plus the partial tail; find an exponential upper bound and binary-search it.','The cycle formula counts every contributing bit exactly once, and monotonicity makes the final feasible binary-search boundary the greatest cheap number.'),'O(log^2 answer)','O(1)',5),
3008: entry('beautiful_indices_large',[('s','str'),('a','str'),('b','str'),('k','int')],'list[int]',['KMP','strings','two pointers'],['s, a, and b are lowercase strings and may each contain up to 500,000 characters; k is nonnegative.','Index i must start an occurrence of a and lie within k positions of some start of b.','Return all qualifying a-start indices in ascending order using near-linear matching.'],[(['isawsquirrelnearmysquirrelhouseohmy','my','squirrel',15],'KMP finds my at sixteen and thirty-three and squirrel at four and eighteen; both my starts have a nearby witness.'),(['abcd','a','a',4],'The occurrence at zero matches both patterns and qualifies at distance zero.')],BEAUTIFUL_CASES,BEAUTIFUL_FAST,[BEAUTIFUL_FAST.replace('second[pointer]<index-k','second[pointer]<=index-k'),BEAUTIFUL_FAST.replace("pattern+'#'+s","s+'#'+pattern")],['Discards a b occurrence exactly k positions before i.','Builds the KMP combined string in the wrong order, so reported offsets are not starts in s.'],beautiful_oracle,random_beautiful,lesson('KMP finds overlapping occurrences in linear time, and sorted occurrence starts admit a one-way proximity pointer.','Build prefix arrays for pattern#text for both patterns; scan b starts forward as a starts increase.','For each a start, discard b starts below i-k and accept when the next is at most i+k.','KMP reports every occurrence once; after discarding too-small witnesses none can help a later index, proving the pointer scan complete and linear.'),'O(n+|a|+|b|)','O(n+|a|+|b|)',8),
}
