"""Third slice of workbook batch 122."""

from collections import Counter, defaultdict, deque
from itertools import permutations

from .import_batch_055 import entry


def mapped_value(value, mapping):
    if value == 0:
        return mapping[0]
    return int("".join(str(mapping[int(digit)]) for digit in str(value)))


def jumbled_oracle(args):
    mapping, nums = args
    decorated = [(mapped_value(value, mapping), index, value) for index, value in enumerate(nums)]
    return [value for _, _, value in sorted(decorated)]


def random_jumbled(rng):
    mapping = list(range(10))
    rng.shuffle(mapping)
    return [mapping, [rng.randint(0, 9999) for _ in range(rng.randint(1, 20))]]


def ancestors_oracle(args):
    n, edges = args
    reverse = [[] for _ in range(n)]
    for parent, child in edges:
        reverse[child].append(parent)
    answer = []
    for node in range(n):
        seen = set()
        stack = list(reverse[node])
        while stack:
            parent = stack.pop()
            if parent not in seen:
                seen.add(parent)
                stack.extend(reverse[parent])
        answer.append(sorted(seen))
    return answer


def random_ancestors(rng):
    n = rng.randint(1, 9)
    edges = [[left, right] for left in range(n) for right in range(left + 1, n) if rng.randrange(4) == 0]
    return [n, edges]


def adjacent_distance(source, target):
    positions = defaultdict(deque)
    for index, char in enumerate(target):
        positions[char].append(index)
    order = [positions[char].popleft() for char in source]
    return sum(order[i] > order[j] for i in range(len(order)) for j in range(i + 1, len(order)))


def palindrome_oracle(args):
    s = args[0]
    counts = Counter(s)
    half = "".join(char * (count // 2) for char, count in sorted(counts.items()))
    middle = next((char for char, count in counts.items() if count % 2), "")
    targets = {"".join(order) + middle + "".join(reversed(order)) for order in permutations(half)}
    return min(adjacent_distance(s, target) for target in targets)


def random_palindrome(rng):
    half = [rng.choice("abcde") for _ in range(rng.randint(1, 4))]
    values = half + list(reversed(half))
    if rng.randrange(2):
        values.append(rng.choice("abcde"))
    rng.shuffle(values)
    return ["".join(values)]


def cells_oracle(args):
    start, end = args[0].split(":")
    return [f"{chr(column)}{row}" for column in range(ord(start[0]), ord(end[0]) + 1) for row in range(int(start[1]), int(end[1]) + 1)]


def random_cells(rng):
    left = rng.randint(ord("A"), ord("Y"))
    right = rng.randint(left, min(ord("Z"), left + 4))
    top = rng.randint(1, 7)
    bottom = rng.randint(top, 9)
    return [f"{chr(left)}{top}:{chr(right)}{bottom}"]


def append_oracle(args):
    nums, k = args
    used = set(nums)
    value = 1
    answer = 0
    while k:
        if value not in used:
            answer += value
            k -= 1
        value += 1
    return answer


def random_append(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 20))], rng.randint(1, 25)]


JUMBLED = '''\
def sort_jumbled_numbers(mapping,nums):
    def mapped(value):
        if value==0:return mapping[0]
        return int(''.join(str(mapping[int(digit)]) for digit in str(value)))
    return sorted(nums,key=mapped)
'''

ANCESTORS = '''\
def all_dag_ancestors(n,edges):
    graph=[[] for _ in range(n)];degree=[0]*n
    for parent,child in edges:graph[parent].append(child);degree[child]+=1
    ancestors=[set() for _ in range(n)];queue=[node for node in range(n) if degree[node]==0]
    for parent in queue:
        for child in graph[parent]:
            ancestors[child].add(parent);ancestors[child].update(ancestors[parent])
            degree[child]-=1
            if degree[child]==0:queue.append(child)
    return [sorted(values) for values in ancestors]
'''

PALINDROME = '''\
def minimum_adjacent_palindrome_moves(s):
    chars=list(s);left=0;right=len(chars)-1;moves=0
    while left<right:
        match=right
        while match>left and chars[match]!=chars[left]:match-=1
        if match==left:
            chars[left],chars[left+1]=chars[left+1],chars[left];moves+=1
        else:
            while match<right:
                chars[match],chars[match+1]=chars[match+1],chars[match];match+=1;moves+=1
            left+=1;right-=1
    return moves
'''

CELLS = '''\
def spreadsheet_cells_in_range(s):
    start,end=s.split(':');answer=[]
    for column in range(ord(start[0]),ord(end[0])+1):
        for row in range(int(start[1]),int(end[1])+1):answer.append(f'{chr(column)}{row}')
    return answer
'''

APPEND = '''\
def minimum_missing_positive_sum(nums,k):
    answer=0;current=1
    for value in sorted(set(nums)):
        if value<current:continue
        take=min(k,value-current)
        answer+=(current+current+take-1)*take//2;k-=take;current=value+1
        if k==0:return answer
    return answer+(current+current+k-1)*k//2
'''


BATCH = {
    2191: entry('sort_jumbled_numbers',[('mapping','list[int]'),('nums','list[int]')],'list[int]',['arrays','sorting','digit mapping'],['mapping[d] replaces every decimal digit d before comparing a number.','Sort by mapped numeric value, but return the original numbers.','Equal mapped values must retain their original relative order, and zero maps as one digit.'],[([[8,9,4,0,2,1,3,5,7,6],[991,338,38]],'Mapped values are 669, 7, and 7; stable sorting returns [338,38,991].'),([[0,1,2,3,4,5,6,7,8,9],[789,456,123]],'Identity mapping makes ordinary numeric order, giving [123,456,789].')],[[m,n] for m,n in [([0,1,2,3,4,5,6,7,8,9],[0]),([9,8,7,6,5,4,3,2,1,0],[0,1,9]),([8,9,4,0,2,1,3,5,7,6],[991,338,38]),([0,1,2,3,4,5,6,7,8,9],[789,456,123]),([1,0,2,3,4,5,6,7,8,9],[10,1,100]),([0,0,2,3,4,5,6,7,8,9],[1,10,100]),([2,1,0,3,4,5,6,7,8,9],[20,2,200]),([9,1,2,3,4,5,6,7,8,0],[9,90,99]),([1,2,3,4,5,6,7,8,9,0],[0,9,10]),([5,6,7,8,9,0,1,2,3,4],[123,321,12]),([0,1,2,3,4,5,6,7,8,9],[5,5,3]),([1,1,2,3,4,5,6,7,8,9],[0,1,10]),([3,2,1,0,4,5,6,7,8,9],[30,3,300]),([9,0,1,2,3,4,5,6,7,8],[101,11,1])]],JUMBLED,[JUMBLED.replace('return sorted(nums,key=mapped)','return sorted(nums)'),JUMBLED.replace("if value==0:return mapping[0]","if value==0:return 0")],['Sorts by original values rather than mapped values.','Treats zero as having no digits instead of applying mapping[0].'],jumbled_oracle,random_jumbled,['Separate the sort key from the value returned.','Map each decimal digit, convert the mapped digit sequence to an integer, and rely on Python’s stable sort.','Handle zero explicitly; define mapped(value); return sorted(nums,key=mapped).','The key is exactly the transformed numeric value, and stable sorting preserves source order for equal keys.'],'O(n*d+n log n)','O(n)',5),
    2192: entry('all_dag_ancestors',[('n','int'),('edge_list','list[list[int]]')],'list[list[int]]',['graphs','topological sort','sets'],['Nodes are 0 through n-1 and the directed graph is acyclic.','An ancestor has a directed path of one or more edges to the node.','Return each node’s ancestors in increasing numeric order.'],[([8,[[0,3],[0,4],[1,3],[2,4],[2,7],[3,5],[3,6],[3,7],[4,6]]],'Propagating ancestor sets through topological order yields the eight requested sorted lists.'),([5,[[0,1],[0,2],[1,3],[2,3],[3,4]]],'Node three has ancestors 0,1,2 and node four additionally includes three.')],[[n,e] for n,e in [(1,[]),(2,[]),(2,[[0,1]]),(3,[[0,1],[1,2]]),(3,[[0,2],[1,2]]),(4,[[0,1],[0,2],[1,3],[2,3]]),(5,[[0,1],[0,2],[1,3],[2,3],[3,4]]),(4,[[0,3],[1,3],[2,3]]),(5,[[0,4],[1,4],[2,4],[3,4]]),(6,[[0,1],[1,2],[0,3],[3,4],[4,5]]),(6,[]),(7,[[0,2],[1,2],[2,5],[3,5],[5,6]]),(4,[[0,1],[1,2],[2,3],[0,3]]),(8,[[0,3],[0,4],[1,3],[2,4],[3,5],[4,6]])]],ANCESTORS,[ANCESTORS.replace('ancestors[child].update(ancestors[parent])','pass'),ANCESTORS.replace('sorted(values)','sorted(values,reverse=True)')],['Records only direct parents and omits transitive ancestors.','Returns ancestor lists in decreasing rather than increasing order.'],ancestors_oracle,random_ancestors,['A child inherits every ancestor of each parent, plus the parent itself.','Process parents before children with topological indegrees and propagate sets along outgoing edges.','Initialize zero-indegree nodes; for each edge update child set, decrement degree, and enqueue when ready.','DAG topological order guarantees every parent set is complete before its child is processed, so propagation finds every and only reachable predecessor.'],'O(n+edges+propagated ancestors)','O(n^2)',6),
    2193: entry('minimum_adjacent_palindrome_moves',[('s','str')],'int',['strings','two pointers','greedy'],['The lowercase string is guaranteed to be rearrangeable into a palindrome.','One move swaps two adjacent characters.','Return the minimum number of moves, not the resulting palindrome.'],[(['aabb'],'Bubble the matching a and b characters into mirrored positions using two adjacent swaps.'),(['letelt'],'Greedily matching the outer letters requires two adjacent swaps in total.')],[[x] for x in ['aa','aba','aabb','mamad','aabbcc','aabbc','ntiin','letelt','abcba','aabcb','aaaabbbb','racecar','ccbbbaa','xxyyzz','aabbccd']],PALINDROME,[PALINDROME.replace('match+=1;moves+=1','match+=1;moves+=0'),PALINDROME.replace('chars[left],chars[left+1]=chars[left+1],chars[left]','left+=1')],['Performs bubble swaps but forgets to count them toward the answer.','Skips an unmatched center candidate without paying or performing its adjacent swap.'],palindrome_oracle,random_palindrome,['Fix mirrored positions from the outside inward.','Find the rightmost match for the left character and bubble it to the right boundary; if none exists, move the odd singleton one step toward the center.','Repeat until pointers meet, counting each adjacent swap.','Using the nearest right-side match minimizes swaps for the fixed outer position; an unmatched character must be the unique odd-frequency center and every step toward center is necessary.'],'O(n^2)','O(n)',8),
    2194: entry('spreadsheet_cells_in_range',[('s','str')],'list[str]',['strings','enumeration'],['s has form C1:C2 with uppercase columns A through Z and single-digit rows 1 through 9.','The first cell is no later than the second in both column and row.','Return cells ordered by column first, then row within each column.'],[(['K1:L2'],'Columns K then L each contribute rows 1 then 2, giving [K1,K2,L1,L2].'),(['A1:A3'],'One column across rows one through three gives [A1,A2,A3].')],[[x] for x in ['A1:A1','A1:A2','A1:B1','A1:B2','K1:L2','A1:A3','B2:D4','Z9:Z9','X7:Z9','C3:F3','M2:N8','D5:H7','A9:C9','Y1:Z5']],CELLS,[CELLS.replace('for column in range(ord(start[0]),ord(end[0])+1)','for column in range(ord(start[0]),ord(end[0]))'),CELLS.replace('for row in range(int(start[1]),int(end[1])+1)','for row in range(int(start[1]),int(end[1]))')],['Omits the final column from the inclusive range.','Omits the final row from each inclusive column range.'],cells_oracle,random_cells,['The required order is a nested column-major enumeration.','Convert column letters to character codes and row digits to integers, using inclusive endpoints.','Loop columns from start through end; inside, loop rows from start through end and format each cell.','The nested loop order matches the specified sort and visits every Cartesian-product cell exactly once.'],'O(number of cells)','O(number of cells)',3),
    2195: entry('minimum_missing_positive_sum',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','sorting','arithmetic'],['Choose k distinct positive integers absent from nums.','Duplicate values in nums forbid that value only once and do not change k.','Return the smallest possible sum of chosen values.'],[([[1,4,25,10,25],2],'The two smallest missing positives are 2 and 3, whose sum is 5.'),([[5,6],6],'Choose 1,2,3,4,7,8 for the minimum total 25.')],[[a,k] for a,k in [([1],1),([2],1),([1,4,25,10,25],2),([5,6],6),([1,2,3],3),([2,2,2],2),([10],5),([1,3,5,7],4),([100,200],3),([1,1,4,4],4),([2,3,4],1),([1,10,20],10),([5,4,3,2,1],2),([7,7,8,9],5)]],APPEND,[APPEND.replace('if value<current:continue','if value<current:break'),APPEND.replace('current=value+1','current=value')],['Stops at a duplicate or previously passed forbidden value and treats later forbidden values as available.','Fails to advance past a forbidden value after processing its gap.'],append_oracle,random_append,['Always choose the smallest currently available positive integers.','Sort unique forbidden values and consume each missing arithmetic interval in order.','For every gap take up to k values and add its arithmetic-series sum; after all gaps take the next k consecutive values.','Any solution using a larger available value while a smaller one remains can exchange them to reduce the sum, proving the greedy order.'],'O(n log n)','O(n)',6),
}
