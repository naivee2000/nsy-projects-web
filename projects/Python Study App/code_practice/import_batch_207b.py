"""Bitmask and string dynamic-programming imports."""
from collections import Counter, deque
from itertools import combinations

from .import_batch_055 import entry

MOD = 1_000_000_007


def connect_oracle(args):
    cost = args[0]; rows, cols = len(cost), len(cost[0]); best = float('inf')
    choices = range(1, 1 << cols)
    def visit(row, covered, total):
        nonlocal best
        if total >= best:return
        if row == rows:
            if covered == (1 << cols) - 1:best = total
            return
        for mask in choices:
            visit(row + 1, covered | mask, total + sum(cost[row][col] for col in range(cols) if mask >> col & 1))
    visit(0, 0, 0)
    return best


def random_connect(rng):
    rows, cols = rng.randint(1, 4), rng.randint(1, 4)
    return [[[rng.randint(1, 20) for _ in range(cols)] for _ in range(rows)]]


def diameter_oracle(args):
    size, edges = args; graph = [[] for _ in range(size)]
    for left, right in edges:
        graph[left - 1].append(right - 1);graph[right - 1].append(left - 1)
    answer = [0] * (size - 1)
    for count in range(2, size + 1):
        for vertices in combinations(range(size), count):
            allowed = set(vertices); distances = {vertices[0]: 0}; queue = deque([vertices[0]])
            while queue:
                node = queue.popleft()
                for neighbor in graph[node]:
                    if neighbor in allowed and neighbor not in distances:
                        distances[neighbor] = distances[node] + 1;queue.append(neighbor)
            if len(distances) != count:continue
            diameter = 0
            for start in vertices:
                distance = {start: 0}; queue = deque([start])
                while queue:
                    node = queue.popleft()
                    for neighbor in graph[node]:
                        if neighbor in allowed and neighbor not in distance:
                            distance[neighbor] = distance[node] + 1;queue.append(neighbor)
                diameter = max(diameter, max(distance.values()))
            answer[diameter - 1] += 1
    return answer


def random_diameter(rng):
    size = rng.randint(2, 9)
    return [size, [[node, rng.randint(1, node - 1)] for node in range(2, size + 1)]]


def substring_oracle(args):
    left, right = args; answer = 0
    for i in range(len(left)):
        for j in range(len(right)):
            differences = 0
            for length in range(1, min(len(left) - i, len(right) - j) + 1):
                differences += left[i + length - 1] != right[j + length - 1]
                answer += differences == 1
    return answer


def random_substrings(rng):
    return [''.join(rng.choice('abc') for _ in range(rng.randint(1, 8))),
            ''.join(rng.choice('abc') for _ in range(rng.randint(1, 8)))]


def formation_oracle(args):
    words, target = args; width = len(words[0]); answer = 0
    for columns in combinations(range(width), len(target)):
        ways = 1
        for char, column in zip(target, columns):
            ways *= sum(word[column] == char for word in words)
        answer = (answer + ways) % MOD
    return answer


def random_formation(rng):
    count, width = rng.randint(1, 6), rng.randint(1, 7)
    words = [''.join(rng.choice('abc') for _ in range(width)) for _ in range(count)]
    return [words, ''.join(rng.choice('abc') for _ in range(rng.randint(1, width)))]


def distribute_oracle(args):
    capacities = sorted(Counter(args[0]).values(), reverse=True)
    demands = sorted(args[1], reverse=True)
    def assign(index):
        if index == len(demands):return True
        tried = set()
        for bucket in range(len(capacities)):
            if capacities[bucket] >= demands[index] and capacities[bucket] not in tried:
                tried.add(capacities[bucket]);capacities[bucket] -= demands[index]
                if assign(index + 1):return True
                capacities[bucket] += demands[index]
        return False
    return assign(0)


def random_distribute(rng):
    kinds = rng.randint(1, 6); nums = []
    for value in range(kinds):nums.extend([value] * rng.randint(1, 7))
    rng.shuffle(nums)
    return [nums, [rng.randint(1, 6) for _ in range(rng.randint(1, 6))]]


CONNECT = '''def minimum_connection_cost(cost):
    rows,cols=len(cost),len(cost[0]);size=1<<cols
    dp=[float('inf')]*size;dp[0]=0
    for row in range(rows):
        following=[float('inf')]*size
        for mask in range(size):
            for col in range(cols):
                following[mask|1<<col]=min(following[mask|1<<col],dp[mask]+cost[row][col])
        dp=following
    cheapest=[min(cost[row][col] for row in range(rows)) for col in range(cols)]
    answer=float('inf')
    for mask,value in enumerate(dp):
        answer=min(answer,value+sum(cheapest[col] for col in range(cols) if not mask>>col&1))
    return answer
'''

CONNECT_FIRST_COLUMN = '''def minimum_connection_cost(cost):
    total=sum(row[0] for row in cost)
    for column in range(1,len(cost[0])):
        total+=min(row[column] for row in cost)
    return total
'''

CONNECT_ROW_MINIMUM = '''def minimum_connection_cost(cost):
    return sum(min(row) for row in cost)
'''

DIAMETER = '''def subtree_diameter_counts(n,edges):
    distance=[[n+1]*n for _ in range(n)]
    for node in range(n):distance[node][node]=0
    normalized=[]
    for left,right in edges:
        left-=1;right-=1;normalized.append((left,right));distance[left][right]=distance[right][left]=1
    for middle in range(n):
        for left in range(n):
            for right in range(n):distance[left][right]=min(distance[left][right],distance[left][middle]+distance[middle][right])
    answer=[0]*(n-1)
    for mask in range(1,1<<n):
        nodes=[node for node in range(n) if mask>>node&1]
        if len(nodes)<2:continue
        if sum((mask>>left&1) and (mask>>right&1) for left,right in normalized)!=len(nodes)-1:continue
        diameter=max(distance[left][right] for left in nodes for right in nodes)
        answer[diameter-1]+=1
    return answer
'''

SUBSTRINGS = '''def count_one_difference_substrings(s,t):
    answer=0
    for offset in range(-len(t)+1,len(s)):
        left=max(0,offset);right=left-offset
        previous=left-1;before_previous=left-1
        while left<len(s) and right<len(t):
            if s[left]!=t[right]:before_previous,previous=previous,left
            answer+=previous-before_previous
            left+=1;right+=1
    return answer
'''

SUBSTRINGS_SINGLE = '''def count_one_difference_substrings(s,t):
    return sum(left!=right for left in s for right in t)
'''

SUBSTRINGS_AT_MOST = '''def count_one_difference_substrings(s,t):
    answer=0
    for i in range(len(s)):
        for j in range(len(t)):
            differences=0
            for length in range(1,min(len(s)-i,len(t)-j)+1):
                differences+=s[i+length-1]!=t[j+length-1]
                answer+=differences<=1
    return answer
'''

FORMATION = '''def count_target_formations(words,target):
    mod=1000000007;width=len(words[0]);ways=[0]*(len(target)+1);ways[0]=1
    for column in range(width):
        counts={}
        for word in words:counts[word[column]]=counts.get(word[column],0)+1
        for index in range(min(column+1,len(target)),0,-1):
            ways[index]=(ways[index]+ways[index-1]*counts.get(target[index-1],0))%mod
    return ways[-1]
'''

DISTRIBUTE = '''def can_distribute_repeats(nums,quantity):
    from collections import Counter
    counts=list(Counter(nums).values());customers=len(quantity);size=1<<customers
    totals=[0]*size
    for mask in range(1,size):
        bit=mask&-mask;totals[mask]=totals[mask^bit]+quantity[bit.bit_length()-1]
    possible={0}
    for count in counts:
        following=set(possible)
        for assigned in possible:
            remaining=(size-1)^assigned;subset=remaining
            while subset:
                if totals[subset]<=count:following.add(assigned|subset)
                subset=(subset-1)&remaining
        possible=following
    return size-1 in possible
'''

DISTRIBUTE_TOTAL = '''def can_distribute_repeats(nums,quantity):
    return len(nums)>=sum(quantity)
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH = {
1595: entry('minimum_connection_cost',[('cost','list[list[int]]')],'int',['dynamic programming','bitmasks','graphs'],['cost is a 1-through-12 by 1-through-12 positive matrix.','Choose connections so every vertex in both groups has at least one incident connection.','Return the minimum sum of selected connection costs.'],[([[[15,96],[36,2]]],'Connect the first left point to the first right point for fifteen and the second pair for two, totaling seventeen.'),([[[1,3,5],[4,1,1]]],'The first row connects to column zero, and the second row can cover columns one and two for a total of three.')],[[c] for c in [[[5]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[9,1],[1,9]],[[2,2],[2,2]],[[1,10,10],[10,1,10],[10,10,1]],[[3,1,4],[1,5,9]],[[8,6],[4,2],[7,3]],[[1,100,100],[100,1,1]],[[5,4,3,2]],[[5],[4],[3],[2]],[[2,9,3],[8,1,7],[6,5,4]],[[7,2],[3,8],[5,1]]]],CONNECT,[CONNECT_FIRST_COLUMN,CONNECT_ROW_MINIMUM],['Forces every left point to use the first column before separately covering other columns.','Connects each left point cheaply but never ensures every right point is covered.'],connect_oracle,random_connect,lesson('Track which right-group vertices are covered after processing each left vertex.','Connect each left vertex once in the main DP, then cheaply attach any still-uncovered right vertices.','Transition mask to mask|1<<column; afterward add each missing column’s cheapest incident edge.','An optimum can designate one selected edge per left vertex; any additional selected edge is needed only to cover a missing right vertex and can be replaced by its cheapest incident edge.'),'O(rows*cols*2^cols)','O(2^cols)',8),
1617: entry('subtree_diameter_counts',[('n','int'),('edges','list[list[int]]')],'list[int]',['trees','bitmasks','graph distances'],['The edges form a tree on vertices 1 through n, where 2 <= n <= 15.','For every nonempty connected vertex subset with at least two vertices, compute its induced-subtree diameter in edges.','Return counts for diameters 1 through n-1.'],[([4,[[1,2],[2,3],[2,4]]],'Three two-vertex subtrees have diameter one, and four larger connected subsets have diameter two.'),([2,[[1,2]]],'The only subset containing both vertices has diameter one.')],[[n,e] for n,e in [(3,[[1,2],[2,3]]),(3,[[1,2],[1,3]]),(4,[[1,2],[2,3],[3,4]]),(4,[[1,2],[1,3],[1,4]]),(5,[[1,2],[2,3],[3,4],[4,5]]),(5,[[1,2],[1,3],[1,4],[1,5]]),(5,[[1,2],[2,3],[2,4],[4,5]]),(6,[[1,2],[2,3],[3,4],[4,5],[5,6]]),(6,[[1,2],[1,3],[2,4],[2,5],[3,6]]),(7,[[1,2],[2,3],[2,4],[4,5],[4,6],[6,7]]),(3,[[2,1],[3,1]]),(4,[[2,1],[3,2],[4,2]]),(5,[[5,4],[4,3],[3,2],[2,1]]),(8,[[1,2],[1,3],[2,4],[2,5],[3,6],[6,7],[6,8]])]],DIAMETER,[DIAMETER.replace("!=len(nodes)-1","==len(nodes)-1"),DIAMETER.replace('answer[diameter-1]+=1','answer[max(0,diameter-2)]+=1')],['Skips connected subsets and counts disconnected ones by reversing the tree-edge test.','Shifts every diameter into the preceding output bucket.'],diameter_oracle,random_diameter,lesson('Because the full graph is a tree, an induced subset is connected exactly when it contains vertex_count-1 tree edges.','Precompute all tree distances, then enumerate vertex masks.','For connected masks, take the maximum pair distance and increment its diameter bucket.','Distances inside a connected induced subtree equal their unique full-tree path lengths because every path vertex must also be in the connected subset.'),'O(2^n*n²+n³)','O(n²)',8),
1638: entry('count_one_difference_substrings',[('s','str'),('t','str')],'int',['strings','dynamic programming','sliding windows'],['s and t contain 1 through 100 lowercase letters.','Count pairs of equal-length nonempty substrings that differ at exactly one aligned position.','Occurrences at different starting positions count separately.'],[(['aba','baba'],'Across all aligned diagonals, six substring pairs have exactly one mismatched character.'),(['ab','bb'],'The pairs a/b, ab/bb, and a/b from the second position give three valid occurrences.')],[[a,b] for a,b in [('a','a'),('a','b'),('ab','ab'),('ab','ba'),('abc','abc'),('abc','abd'),('aaa','bbb'),('aaa','aba'),('abcd','bc'),('x','xyz'),('xyz','x'),('abab','baba'),('aaaa','aaab'),('abcde','edcba')]],SUBSTRINGS,[SUBSTRINGS_SINGLE,SUBSTRINGS_AT_MOST],['Counts only length-one substring pairs and misses longer pairs with one difference.','Counts matching substring pairs as well as pairs with exactly one difference.'],substring_oracle,random_substrings,lesson('Each pair of substring starts lies on one alignment diagonal.','On a diagonal, remember the latest and second-latest mismatch positions.','Every ending position has latest-second_latest starts that include exactly the latest mismatch.','Starts after the second-latest mismatch exclude all earlier differences, while starts at or before the latest mismatch include the required one.'),'O(len(s)*len(t))','O(1)',5),
1639: entry('count_target_formations',[('words','list[str]'),('target','str')],'int',['strings','dynamic programming','counting'],['There are 1 through 1000 equal-length lowercase words, each up to 1000 characters; target is no longer than that width.','Build target left-to-right by choosing strictly increasing column indices and any word at each chosen column.','Return the number of choices modulo 1000000007.'],[([['acca','bbbb','caca'],'aba'],'Choose increasing columns whose character frequencies multiply; all valid choices total six.'),([['abba','baab'],'bab'],'The valid column choices, including their word multiplicities, total four.')],[[w,t] for w,t in [(['a'],'a'),(['a'],'b'),(['a','a'],'a'),(['ab'],'ab'),(['ab'],'ba'),(['abc','abc'],'abc'),(['abc','bbc'],'abc'),(['aaa','aaa'],'aa'),(['abca','bbcb','cbcc'],'abc'),(['abcd','efgh'],'ae'),(['zzzz','zzzz','zzzz'],'zzz'),(['abab','baba'],'aba'),(['abcde','bbcde','cbcde'],'bcd'),(['aaaaa','bbbbb'],'ab')]],FORMATION,[FORMATION.replace('range(min(column+1,len(target)),0,-1)','range(1,min(column+1,len(target))+1)'),FORMATION.replace('for word in words:','for word in words[:1]:')],['Updates target positions left-to-right and reuses the same source column more than once.','Counts characters from only the first word and loses choices supplied by other words.'],formation_oracle,random_formation,lesson('Only column character frequencies matter, not which word supplied earlier characters.','Process columns left-to-right and update target-prefix counts right-to-left.','ways[j] += ways[j-1] * frequency[column][target[j-1]].','Descending updates prevent one column from supplying two target positions, and every increasing column choice has one final chosen column counted exactly once.'),'O(word_count*width+width*target_length)','O(target_length+alphabet)',8),
1655: entry('can_distribute_repeats',[('nums','list[int]'),('quantity','list[int]')],'bool',['backtracking','bitmasks','counting'],['nums has at most 100000 values but at most 50 distinct values; quantity has 1 through 10 positive demands.','Each customer must receive its requested count of one identical integer value.','Different customers may share a value only when its available frequency covers their combined demand.'],[([[1,2,3,4],[2]],'Every value occurs once, so no customer can receive two identical integers.'),([[1,1,2,2],[2,2]],'Give both ones to one customer and both twos to the other.')],[[n,q] for n,q in [([1],[1]),([1],[2]),([1,1],[1,1]),([1,1],[2]),([1,1,2],[2,1]),([1,1,2],[2,2]),([1,1,2,2,3,3],[2,2,2]),([1,1,1,1],[2,2]),([1,1,1],[1,1,1]),([1,2,3],[1,1,1]),([1,1,2,2],[3]),([1,1,1,2,2],[3,2]),([1,1,1,2,2,2],[2,2,2]),([1,1,1,1,2,2,3],[3,2,2])]],DISTRIBUTE,[DISTRIBUTE.replace('totals[subset]<=count','totals[subset]<count'),DISTRIBUTE_TOTAL],['Requires unused capacity after an assignment and rejects an exact fit.','Checks only the total number of items and ignores the identical-value requirement.'],distribute_oracle,random_distribute,lesson('Compress equal input values into independent capacity buckets.','Represent a set of already satisfied customers by a bitmask.','For each capacity, enumerate subsets of remaining customers whose total demand fits and add them to reachable masks.','Every customer assigned to one value appears in exactly one chosen subset; carrying old masks permits unused values.'),'O(distinct*3^customers)','O(2^customers)',8),
}
