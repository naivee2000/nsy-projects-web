"""Fourth slice of workbook batch 122."""

from collections import Counter, deque
from itertools import combinations, permutations
from math import gcd

from .import_batch_055 import entry


def tree_oracle(args):
    descriptions = args[0]
    children = {}
    child_values = set()
    for parent, child, is_left in descriptions:
        children.setdefault(parent, [None, None])[0 if is_left else 1] = child
        child_values.add(child)
    root = next(parent for parent, _, _ in descriptions if parent not in child_values)
    queue = deque([root])
    answer = []
    while queue:
        value = queue.popleft()
        answer.append(value)
        if value is None:
            continue
        left, right = children.get(value, [None, None])
        queue.extend([left, right])
    while answer and answer[-1] is None:
        answer.pop()
    return answer


def random_tree(rng):
    n = rng.randint(2, 12)
    values = rng.sample(range(1, 200), n)
    available = [values[0]]
    slots = {values[0]: [0, 1]}
    descriptions = []
    for child in values[1:]:
        parent = rng.choice(available)
        side = rng.choice(slots[parent])
        slots[parent].remove(side)
        if not slots[parent]:
            available.remove(parent)
        descriptions.append([parent, child, 1 if side == 0 else 0])
        slots[child] = [0, 1]
        available.append(child)
    rng.shuffle(descriptions)
    return [descriptions]


def replace_oracle(args):
    values = list(args[0])
    changed = True
    while changed:
        changed = False
        for index in range(len(values) - 1):
            divisor = gcd(values[index], values[index + 1])
            if divisor > 1:
                values[index : index + 2] = [values[index] // divisor * values[index + 1]]
                changed = True
                break
    return values


def random_replace(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 18))]]


def divisor_oracle(args):
    nums = args[0]
    answer = 0
    for order in permutations(range(len(nums)), 3):
        total = sum(nums[index] for index in order)
        if sum(total % nums[index] == 0 for index in order) == 1:
            answer += 1
    return answer


def random_divisor(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(3, 10))]]


def distant_oracle(args):
    nums, key, k = args
    positions = [index for index, value in enumerate(nums) if value == key]
    return [index for index in range(len(nums)) if any(abs(index - position) <= k for position in positions)]


def random_distant(rng):
    n = rng.randint(1, 30)
    key = rng.randint(1, 6)
    nums = [rng.randint(1, 6) for _ in range(n)]
    nums[rng.randrange(n)] = key
    return [nums, key, rng.randint(0, n)]


def artifacts_oracle(args):
    _, artifacts, dig = args
    excavated = {tuple(cell) for cell in dig}
    return sum(
        all((row, column) in excavated for row in range(top, bottom + 1) for column in range(left, right + 1))
        for top, left, bottom, right in artifacts
    )


def random_artifacts(rng):
    n = rng.randint(1, 5)
    cells = [(row, column) for row in range(n) for column in range(n)]
    rng.shuffle(cells)
    artifacts = [[row, column, row, column] for row, column in cells[: rng.randint(1, len(cells))]]
    dig = [list(cell) for cell in cells if rng.randrange(2)]
    return [n, artifacts, dig]


TREE = '''\
def create_tree_from_descriptions(descriptions):
    nodes={};children=set()
    for parent,child,is_left in descriptions:
        nodes.setdefault(parent,TreeNode(parent));nodes.setdefault(child,TreeNode(child))
        if is_left:nodes[parent].left=nodes[child]
        else:nodes[parent].right=nodes[child]
        children.add(child)
    root=next(value for value in nodes if value not in children)
    return nodes[root]
'''

REPLACE = '''\
def replace_adjacent_non_coprimes(nums):
    from math import gcd
    stack=[]
    for value in nums:
        stack.append(value)
        while len(stack)>1:
            divisor=gcd(stack[-2],stack[-1])
            if divisor==1:break
            right=stack.pop();left=stack.pop();stack.append(left//divisor*right)
    return stack
'''

DIVISOR = '''\
def count_single_divisor_triplets(nums):
    from collections import Counter
    from itertools import combinations_with_replacement
    from math import comb
    counts=Counter(nums);answer=0
    for first,second,third in combinations_with_replacement(sorted(counts),3):
        values=(first,second,third);needed=Counter(values)
        if any(counts[value]<amount for value,amount in needed.items()):continue
        total=sum(values)
        if sum(total%value==0 for value in values)!=1:continue
        ways=1
        for value,amount in needed.items():ways*=comb(counts[value],amount)
        answer+=6*ways
    return answer
'''

DISTANT = '''\
def k_distant_indices(nums,key,k):
    difference=[0]*(len(nums)+1)
    for index,value in enumerate(nums):
        if value==key:
            left=max(0,index-k);right=min(len(nums),index+k+1)
            difference[left]+=1;difference[right]-=1
    active=0;answer=[]
    for index in range(len(nums)):
        active+=difference[index]
        if active:answer.append(index)
    return answer
'''

ARTIFACTS = '''\
def count_extractable_artifacts(n,artifacts,dig):
    excavated={tuple(cell) for cell in dig};answer=0
    for top,left,bottom,right in artifacts:
        if all((row,column) in excavated for row in range(top,bottom+1) for column in range(left,right+1)):
            answer+=1
    return answer
'''


BATCH = {
    2196: entry('create_tree_from_descriptions',[('descriptions','list[list[int]]')],'TreeNode | None',['trees','hash maps','construction'],['Each description is [parent,child,is_left], where one means left and zero means right.','All values are unique and the descriptions form exactly one valid binary tree.','Return the root node; child positions and sparse shape must be preserved.'],[([[[20,15,1],[20,17,0],[50,20,1],[50,80,0],[80,19,1]]],'Only fifty never appears as a child; its level-order tree is [50,20,80,15,17,19].'),([[[1,2,1],[2,3,0]]],'One is the root, with left child two whose right child is three.')],[[d] for d in [[[1,2,1]],[[1,2,0]],[[1,2,1],[1,3,0]],[[2,1,1],[2,3,0]],[[1,2,1],[2,3,1]],[[1,2,0],[2,3,0]],[[20,15,1],[20,17,0],[50,20,1],[50,80,0],[80,19,1]],[[3,1,1],[3,5,0],[1,0,1],[1,2,0]],[[10,5,1],[5,2,0],[10,15,0]],[[8,4,1],[4,2,1],[2,1,1]],[[7,3,1],[7,9,0],[9,8,1]],[[100,50,1],[100,150,0],[50,25,0]],[[4,2,1],[4,6,0],[2,1,1],[2,3,0]],[[9,5,0],[5,4,1]]]],TREE,[TREE.replace('if is_left:nodes[parent].left','if not is_left:nodes[parent].left'),TREE.replace('value not in children','value in children')],['Reverses left and right child placement.','Chooses a value that appears as a child instead of the unique root.'],tree_oracle,random_tree,['Create one reusable node object per value and identify the only value never used as a child.','Attach child nodes while recording all child values in a set.','After processing descriptions, return the node whose value is absent from children.','Every non-root node has exactly one parent and therefore appears in the child set; the valid tree’s root is the unique exception.'],'O(descriptions)','O(nodes)',6),
    2197: entry('replace_adjacent_non_coprimes',[('nums','list[int]')],'list[int]',['arrays','stacks','greatest common divisors'],['Adjacent values with gcd greater than one must be replaced by their least common multiple.','A replacement may create a new non-coprime pair with the value immediately to its left.','Continue until every adjacent pair is coprime and return the unique final list.'],[([[6,4,3,2,7,6,2]],'Cascading replacements combine the first four values to 12 and the final pair to 6, giving [12,7,6].'),([[2,2,1,1,3,3,3]],'The two values and the trailing threes merge within their regions, producing [2,1,1,3].')],[[x] for x in [[1],[2,3],[2,4],[6,4,3,2,7,6,2],[2,2,1,1,3,3,3],[4,6,8],[6,10,15],[5,7,11],[12,18,5,10],[2,3,6],[8,9,12],[7,14,21,5],[3,6,2,4],[16,24,36,5]]],REPLACE,[REPLACE.replace('if divisor==1:break','if divisor!=1:break'),REPLACE.replace('left//divisor*right','left*right')],['Stops on non-coprime pairs and tries to merge coprime pairs.','Uses the product instead of dividing by gcd to form the least common multiple.'],replace_oracle,random_replace,['A stack exposes exactly the newest adjacency that a replacement can affect.','Push each value, then repeatedly merge the top two while their gcd exceeds one.','Replace top pair by left/gcd*right and keep checking backward.','Earlier settled adjacencies remain unchanged except the one touching the merged value, which is precisely the new stack top pair.'],'O(n log values)','O(n)',8),
    2198: entry('count_single_divisor_triplets',[('nums','list[int]')],'int',['arrays','counting','enumeration'],['Triplets use three distinct indices, and their order counts: each qualifying index set contributes six permutations.','Let total be the sum of the three selected values.','Exactly one of the three selected values, counting repeated occurrences, must divide total.'],[([[4,6,7,3,2]],'Two unordered index triples meet the rule, and their twelve ordered permutations are counted.'),([[1,2,3]],'Their sum six is divisible by all three selected values, not exactly one, so return zero.')],[[x] for x in [[1,2,3],[4,6,7,3,2],[2,2,3],[2,3,4],[3,3,4],[1,1,2],[5,7,9],[2,4,8,16],[6,10,15],[1,4,6,7],[3,5,7,9],[2,2,2,3],[4,4,6,7],[10,11,12,13]]],DIVISOR,[DIVISOR.replace('answer+=6*ways','answer+=ways'),DIVISOR.replace('!=1','==0')],['Counts unordered index sets but omits their six orderings.','Accepts only sums divisible by none of the selected values.'],divisor_oracle,random_divisor,['Values are small, so aggregate identical choices before enumerating value triples.','Enumerate nondecreasing value triples, verify available multiplicities, and compute how many index sets realize them.','When exactly one value occurrence divides the sum, multiply the combination count by six ordered permutations.','Every distinct-index ordered triplet belongs to one nondecreasing value multiset and one of its six index orders, so the aggregation is exact.'],'O(V^3)','O(V)',6),
    2200: entry('k_distant_indices',[('nums','list[int]'),('key','int'),('k','int')],'list[int]',['arrays','difference arrays','two pointers'],['An index qualifies if some key occurrence lies within absolute distance k.','Return each qualifying index exactly once in increasing order.','k may be zero, in which case only key positions qualify.'],[([[3,4,9,1,3,9,5],9,1],'The two key positions cover index intervals [1,3] and [4,6], whose union is 1 through 6.'),([[2,2,2,2,2],2,2],'Every position is itself or is near a key, so all indices are returned once.')],[[a,key,k] for a,key,k in [([1],1,0),([1],1,2),([1,2,3],2,0),([1,2,3],2,1),([3,4,9,1,3,9,5],9,1),([2,2,2,2,2],2,2),([1,0,0,0,1],1,1),([5,1,5,1,5],5,0),([5,1,5,1,5],5,2),([1,2,1,2,1],2,1),([9,8,7,6],9,3),([0,0,1,0],1,5),([4,3,2,1,4],4,1),([6,1,2,3,6,4],6,2)]],DISTANT,[DISTANT.replace('index+k+1','index+k'),DISTANT.replace('if active:answer.append(index)','if active>1:answer.append(index)')],['Treats the distance-k right endpoint as exclusive.','Returns only indices covered by at least two key neighborhoods.'],distant_oracle,random_distant,['Each key occurrence contributes an inclusive interval of qualifying indices.','Use a difference array to add all intervals, then scan their union once.','Increment at max(0,j-k), decrement after min(n-1,j+k), prefix-sum, and emit positions with positive coverage.','Difference updates represent every neighborhood exactly, and positive prefix coverage is equivalent to existence of at least one qualifying key index.'],'O(n)','O(n)',3),
    2201: entry('count_extractable_artifacts',[('n','int'),('artifacts','list[list[int]]'),('dig','list[list[int]]')],'int',['matrices','hash sets','simulation'],['Each artifact rectangle is [top,left,bottom,right] with inclusive coordinates.','An artifact counts only when every cell in its rectangle appears in dig.','Artifacts do not overlap, dig cells are unique, and n defines the square grid size.'],[([2,[[0,0,0,0],[0,1,1,1]],[[0,0],[0,1]]],'The one-cell artifact is fully dug, but the vertical artifact still has cell [1,1] buried, so return one.'),([3,[[0,0,1,1],[2,2,2,2]],[[0,0],[0,1],[1,0],[1,1],[2,2]]],'Both the 2-by-2 rectangle and single cell are fully excavated.')],[[n,a,d] for n,a,d in [(1,[[0,0,0,0]],[]),(1,[[0,0,0,0]],[[0,0]]),(2,[[0,0,0,0],[0,1,1,1]],[[0,0],[0,1]]),(2,[[0,0,1,0]],[[0,0],[1,0]]),(2,[[0,0,1,1]],[[0,0],[0,1],[1,0]]),(3,[[0,0,1,1],[2,2,2,2]],[[0,0],[0,1],[1,0],[1,1],[2,2]]),(3,[[0,0,0,2]],[[0,0],[0,1],[0,2]]),(3,[[0,0,2,0]],[[0,0],[1,0],[2,0]]),(4,[[1,1,2,2]],[[1,1],[1,2],[2,1],[2,2]]),(4,[[0,0,0,0],[3,3,3,3]],[[0,0]]),(3,[[0,1,1,1]],[[0,1]]),(5,[[2,2,3,3]],[[2,2],[2,3],[3,2],[3,3]]),(2,[[0,0,0,1]],[[0,1]]),(3,[[1,0,1,2]],[[1,0],[1,1],[1,2]])]],ARTIFACTS,[ARTIFACTS.replace('if all(','if any('),ARTIFACTS.replace('range(top,bottom+1)','range(top,bottom)')],['Counts a partially excavated artifact when any one cell is dug.','Omits the artifact’s bottom row from the completeness check.'],artifacts_oracle,random_artifacts,['Dig membership is queried repeatedly, so store coordinates in a set.','For each rectangle, require every row-column coordinate in its inclusive bounds to be excavated.','Build excavated tuples; use all(...) over both inclusive ranges; count successful artifacts.','The Cartesian-product scan visits exactly the cells occupied by an artifact, so all membership tests succeeding is necessary and sufficient.'],'O(dig+artifact cells)','O(dig)',5),
}

BATCH[2196]['adapter'] = 'treenode'
