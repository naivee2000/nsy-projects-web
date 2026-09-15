"""Manhattan extrema, closed substrings, cyclic edits, medians, and graph AND."""
from collections import deque

from .import_batch_055 import entry


def manhattan_oracle(args):
    points = args[0]; answer = 10**30
    for removed in range(len(points)):
        kept = [point for index, point in enumerate(points) if index != removed]
        maximum = 0
        for left in range(len(kept)):
            for right in range(left + 1, len(kept)):
                maximum = max(maximum, abs(kept[left][0] - kept[right][0]) +
                              abs(kept[left][1] - kept[right][1]))
        answer = min(answer, maximum)
    return answer


def random_manhattan(rng):
    return [[[rng.randint(-20, 20), rng.randint(-20, 20)]
             for _ in range(rng.randint(3, 10))]]


def closed_oracle(args):
    text = args[0]; answer = -1
    for left in range(len(text)):
        for right in range(left + 1, len(text) + 1):
            if right - left == len(text):
                continue
            inside = set(text[left:right])
            if all(char not in inside for char in text[:left] + text[right:]):
                answer = max(answer, right - left)
    return answer


def random_closed(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 14)))]


def cyclic_oracle(args):
    text, budget = args; output = []
    for char in text:
        chosen = char
        for candidate_code in range(ord('a'), ord(char) + 1):
            direct = ord(char) - candidate_code
            wrap = 26 - direct
            cost = min(direct, wrap)
            if cost <= budget:
                chosen = chr(candidate_code); budget -= cost; break
        output.append(chosen)
    return ''.join(output)


def random_cyclic(rng):
    return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1, 15))),
            rng.randint(0, 40)]


def median_oracle(args):
    nums, target = args; values = sorted(nums); middle = len(values) // 2; answer = 0
    for index, value in enumerate(values):
        if index <= middle and value > target:
            answer += value - target
        elif index >= middle and value < target:
            answer += target - value
    return answer


def random_median(rng):
    return [[rng.randint(-20, 20) for _ in range(rng.randint(1, 15))], rng.randint(-20, 20)]


def graph_oracle(args):
    size, edges, queries = args; graph = [[] for _ in range(size)]
    for left, right, weight in edges:
        graph[left].append((right, weight)); graph[right].append((left, weight))
    component = [-1] * size; costs = []
    for start in range(size):
        if component[start] != -1:
            continue
        identifier = len(costs); queue = deque([start]); component[start] = identifier; nodes = []
        while queue:
            node = queue.popleft(); nodes.append(node)
            for neighbor, _ in graph[node]:
                if component[neighbor] == -1:
                    component[neighbor] = identifier; queue.append(neighbor)
        cost = -1
        for node in nodes:
            for _, weight in graph[node]:
                cost &= weight
        costs.append(cost)
    return [0 if left == right else costs[component[left]] if component[left] == component[right] else -1
            for left, right in queries]


def random_graph(rng):
    size = rng.randint(1, 9); edges = []
    for left in range(size):
        for right in range(left + 1, size):
            if rng.random() < .25:
                edges.append([left, right, rng.randint(0, 31)])
    queries = [[rng.randrange(size), rng.randrange(size)] for _ in range(rng.randint(1, 10))]
    return [size, edges, queries]


MANHATTAN = '''def minimum_max_manhattan_after_removal(points):
    size=len(points);plus=sorted((x+y,index) for index,(x,y) in enumerate(points));minus=sorted((x-y,index) for index,(x,y) in enumerate(points))
    answer=10**30
    for removed in range(size):
        plus_low=plus[1][0] if plus[0][1]==removed else plus[0][0]
        plus_high=plus[-2][0] if plus[-1][1]==removed else plus[-1][0]
        minus_low=minus[1][0] if minus[0][1]==removed else minus[0][0]
        minus_high=minus[-2][0] if minus[-1][1]==removed else minus[-1][0]
        answer=min(answer,max(plus_high-plus_low,minus_high-minus_low))
    return answer
'''


CLOSED = '''def longest_self_contained_substring(s):
    first={};last={}
    for index,char in enumerate(s):first.setdefault(char,index);last[char]=index
    answer=-1;size=len(s)
    for char,left in first.items():
        farthest=last[char]
        for right in range(left,size):
            current=s[right]
            if first[current]<left:break
            farthest=max(farthest,last[current])
            if right==farthest and right-left+1<size:answer=max(answer,right-left+1)
    return answer
'''


CYCLIC = '''def smallest_cyclic_edit_string(s,k):
    output=[]
    for char in s:
        chosen=char
        for code in range(ord('a'),ord(char)+1):
            distance=min(ord(char)-code,26-ord(char)+code)
            if distance<=k:chosen=chr(code);k-=distance;break
        output.append(chosen)
    return ''.join(output)
'''


MEDIAN = '''def minimum_operations_for_median(nums,k):
    values=sorted(nums);middle=len(values)//2;answer=abs(values[middle]-k)
    if values[middle]>k:
        for index in range(middle-1,-1,-1):
            if values[index]<=k:break
            answer+=values[index]-k
    else:
        for index in range(middle+1,len(values)):
            if values[index]>=k:break
            answer+=k-values[index]
    return answer
'''


GRAPH = '''def minimum_and_walk_costs(n,edges,query):
    parent=list(range(n));sizes=[1]*n
    def find(node):
        while parent[node]!=node:
            parent[node]=parent[parent[node]];node=parent[node]
        return node
    def union(left,right):
        left=find(left);right=find(right)
        if left==right:return
        if sizes[left]<sizes[right]:left,right=right,left
        parent[right]=left;sizes[left]+=sizes[right]
    for left,right,_ in edges:union(left,right)
    costs={}
    for left,_,weight in edges:
        root=find(left);costs[root]=costs.get(root,-1)&weight
    answer=[]
    for left,right in query:
        if left==right:answer.append(0)
        elif find(left)!=find(right):answer.append(-1)
        else:answer.append(costs[find(left)])
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3102: entry('minimum_max_manhattan_after_removal',[('points','list[list[int]]')],'int',['geometry','sorting','extrema'],['points contains at least three integer coordinate pairs.','Remove exactly one point, then measure the maximum Manhattan distance among every remaining pair.','Return the minimum possible maximum distance.'],[([[[3,10],[5,15],[10,2],[4,4]]],'Removing [5,15] leaves a maximum Manhattan distance of twelve, which is optimal.'),([[[0,0],[1,1],[100,100]]],'Removing the distant point leaves distance two between the remaining pair.')],[[p] for p in [[[0,0],[1,1],[2,2]],[[0,0],[1,1],[100,100]],[[3,10],[5,15],[10,2],[4,4]],[[0,0],[0,0],[1,1]],[[0,5],[5,0],[3,3]],[[1,2],[3,4],[5,6],[7,8]],[[0,0],[10,0],[0,10],[10,10]],[[-5,-5],[5,5],[0,0]],[[-10,2],[3,-7],[8,4],[1,1]],[[2,9],[9,2],[5,5],[100,0]],[[1,10],[2,9],[3,8],[4,7]],[[0,0],[2,3],[4,1],[6,5],[8,2]],[[7,7],[7,-7],[-7,7],[-7,-7]],[[1,1],[1,2],[2,1],[50,50]]]],MANHATTAN,[MANHATTAN.replace('max(plus_high-plus_low,minus_high-minus_low)','plus_high-plus_low'),MANHATTAN.replace('answer=10**30','answer=0').replace('answer=min(answer','answer=max(answer')],['Considers only the x+y projection and misses distances witnessed by x-y.','Chooses the removal leaving the largest diameter instead of the smallest.'],manhattan_oracle,random_manhattan,lesson('Manhattan distance equals the maximum difference in the transformed coordinates x+y and x-y.','Sort both projections with point indices; after each removal select the first/last entry not carrying that index.','For every removed index compute both remaining projection ranges and minimize their maximum.','The projection identity gives the exact diameter, and only an endpoint can change when one indexed point is removed.'),'O(n log n)','O(n)',8),
3104: entry('longest_self_contained_substring',[('s','str')],'int',['strings','intervals','hash maps'],['s is a nonempty lowercase string.','A self-contained substring is proper (not the whole string) and contains every occurrence in s of each character it includes.','Return the greatest possible length, or -1 if no proper self-contained substring exists.'],[(['abba'],'Substring bb contains every b and excludes all a occurrences, so the answer is two.'),(['abab'],'Every occurrence-closed substring is the whole string, which is forbidden, so the result is -1.')],[[s] for s in ['a','ab','aa','abba','abab','abc','abac','eccbbbbdec','adefaddaccc','aaaaab','baaaa','abcabc','abccba','cabbaac']],CLOSED,[CLOSED.replace('and right-left+1<size',''),CLOSED.replace('if first[current]<left:break','if first[current]<left:continue')],['Allows the entire string even though the substring must be proper.','Continues through a character whose earlier occurrence lies outside, accepting a non-contained interval.'],closed_oracle,random_closed,lesson('A valid interval must begin at a character’s first occurrence and expand through the last occurrence of every character encountered.','Try each distinct first occurrence; reject if an encountered character begins earlier, otherwise extend the required right boundary.','Scan from left, update farthest=max(last[char]); whenever index=farthest record the proper interval length.','Expansion includes all later occurrences, the earlier-occurrence check includes all prior ones, and each possible valid left boundary is tested.'),'O(alphabet*n)','O(alphabet)',8),
3106: entry('smallest_cyclic_edit_string',[('s','str'),('k','int')],'str',['strings','greedy'],['s contains lowercase letters and k is nonnegative.','Changing one character costs its shortest circular alphabet distance, where a and z are adjacent.','Spend total cost at most k and return the lexicographically smallest obtainable string.'],[(['zbbz',3],'Change z to a for one and both b characters to a for one each, leaving the final z and producing aaaz.'),(['xax',2],'Changing the first x to a costs three, so the best use is changing it backward by two to v, producing vax.')],[[s,k] for s,k in [('a',0),('z',1),('b',1),('zbbz',3),('xax',2),('abc',3),('zzz',2),('mnop',10),('azaz',2),('leetcode',5),('qwerty',0),('cba',2),('yx',4),('abcdefghijklmnopqrstuvwxyz',25)]],CYCLIC,[CYCLIC.replace('min(ord(char)-code,26-ord(char)+code)','ord(char)-code'),CYCLIC.replace('for char in s','for char in reversed(s)')],['Ignores the wraparound route between letters near z and a.','Spends the budget from the right end, sacrificing lexicographically more important earlier positions.'],cyclic_oracle,random_cyclic,lesson('Lexicographic order makes the earliest improvable position more important than every later character combined.','Scan left to right and choose the smallest letter reachable within the remaining circular-distance budget.','For candidate letters a through the current character, take the first with min(backward,wrap)≤k, subtract its cost, and continue.','The first differing position dominates lexicographic comparison, so the locally smallest affordable choice cannot be improved by saving budget for later.'),'O(26*n)','O(n)',5),
3107: entry('minimum_operations_for_median',[('nums','list[int]'),('k','int')],'int',['sorting','greedy','medians'],['nums is a nonempty integer array and k is an integer.','The median is sorted index floor(n/2), so an even-length array uses the larger middle value.','One operation changes one value by one; return the fewest operations making the median exactly k.'],[([[2,5,6,8,5],4],'After sorting, lower the two middle-or-higher values five and five to four, requiring two operations.'),([[1,2,3,4],5],'The upper median and every value after it must reach at least five, costing three plus one = four.')],[[a,k] for a,k in [([1],1),([1],5),([1,2],1),([1,2],2),([1,2],3),([2,5,6,8,5],4),([1,2,3,4],5),([5,5,5],5),([10,10,1,1],5),([-3,-1,2],0),([7,1,9,3,5],6),([1,100,101,102],50),([4,2,8,6,0],3),([9,8,7,6,5,4],7)]],MEDIAN,[MEDIAN.replace('middle=len(values)//2','middle=(len(values)-1)//2'),"""def minimum_operations_for_median(nums,k):
    values=sorted(nums);return abs(values[len(values)//2]-k)
"""],['Uses the lower middle element for even-length arrays.','Changes only the current median and ignores other values that would cross the target median position.'],median_oracle,random_median,lesson('After sorting, values on the median’s low side must not exceed k and values on its high side must not fall below k.','Move the median to k, then clamp only violating values on the necessary side.','If median>k, sum value-k for indices through the median where value>k; otherwise sum k-value from the median onward where value<k.','Every counted unit is necessary to keep at least the required number of values on each side of k, and these changes are sufficient.'),'O(n log n)','O(n)',5),
3108: entry('minimum_and_walk_costs',[('n','int'),('edges','list[list[int]]'),('query','list[list[int]]')],'list[int]',['graphs','union find','bit manipulation'],['Vertices are 0 through n-1; edges are undirected and may repeat, with nonnegative weights.','A walk may repeat vertices and edges; its cost is the bitwise AND of every traversed edge weight.','For each query return zero for equal endpoints, -1 across components, or the minimum walk cost otherwise.'],[([5,[[0,1,7],[1,3,7],[1,2,1]],[[0,3],[3,4]]],'Vertices zero and three share a component whose edge-weight AND is one; vertex four is disconnected.'),([3,[[0,1,6],[1,2,5],[0,2,3]],[[0,2],[1,1]]],'A walk can include all component edges for AND zero, while an equal-endpoint query costs zero.')],[[n,e,q] for n,e,q in [(1,[],[[0,0]]),(2,[],[[0,1]]),(2,[[0,1,7]],[[0,1]]),(3,[[0,1,6],[1,2,5]],[[0,2]]),(3,[[0,1,6],[1,2,5],[0,2,3]],[[0,2],[1,1]]),(4,[[0,1,7],[2,3,3]],[[0,1],[0,2],[2,3]]),(4,[[0,1,15],[1,2,14],[2,3,12]],[[0,3]]),(3,[[0,1,7],[0,1,3],[1,2,6]],[[0,2]]),(5,[[0,1,31],[1,2,15],[2,3,7],[3,4,3]],[[0,4],[4,0]]),(5,[[0,1,7],[1,3,7],[1,2,1]],[[0,3],[3,4]]),(4,[],[[0,0],[1,2]]),(3,[[0,1,0]],[[0,1],[1,2]]),(6,[[0,1,14],[1,2,12],[3,4,7],[4,5,3]],[[0,2],[3,5],[2,3]]),(4,[[0,1,5],[1,2,3],[2,0,6],[2,3,7]],[[0,3]])]],GRAPH,[GRAPH.replace("costs[root]=costs.get(root,-1)&weight","costs[root]=max(costs.get(root,0),weight)"),GRAPH.replace('if left==right:answer.append(0)','if left==right:answer.append(costs.get(find(left),-1))')],['Uses the largest component edge instead of the AND of every edge.','Returns the component edge cost for an equal-endpoint query instead of the required zero-length cost zero.'],graph_oracle,random_graph,lesson('Within one connected component a walk can detour over every edge before reaching its destination, and extra AND operands can only reduce cost.','Union all endpoints, AND every edge weight into its final component, then answer connectivity queries.','Build DSU; componentCost[root]&=weight for all edges; answer 0 for u=v, cost for same roots, else -1.','A traversal can include all component edges, achieving their AND, and no walk can clear a bit present in every component edge.'),'O((n+edges+queries)*alpha(n))','O(n)',8),
}
