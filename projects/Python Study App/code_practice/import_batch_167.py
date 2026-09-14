"""Matrix formatting, prefix scores, cousin sums, row counts, and divisibility batch 167."""

from collections import deque

from .import_batch_055 import entry


def widths_oracle(args):
    grid=args[0]
    return [max(len(str(grid[row][column])) for row in range(len(grid))) for column in range(len(grid[0]))]


def random_widths(rng):
    rows,columns=rng.randint(1,10),rng.randint(1,8)
    return [[[rng.randint(-10**8,10**8) for _ in range(columns)] for _ in range(rows)]]


def scores_oracle(args):
    nums=args[0];answer=[]
    for end in range(len(nums)):
        answer.append(sum(nums[index]+max(nums[:index+1]) for index in range(end+1)))
    return answer


def random_scores(rng):
    return [[rng.randint(1,100) for _ in range(rng.randint(1,30))]]


def cousins_oracle(args):
    values=args[0]
    if not values:return []
    nodes=[[values[0],None,None]];root=nodes[0];queue=deque([root]);index=1
    while queue and index<len(values):
        node=queue.popleft()
        for side in (1,2):
            if index<len(values) and values[index] is not None:
                child=[values[index],None,None];node[side]=child;queue.append(child);nodes.append(child)
            index+=1
    level=[(root,None)]
    while level:
        total=sum(node[0] for node,_ in level)
        family={}
        for node,parent in level:family[id(parent)]=family.get(id(parent),0)+node[0]
        for node,parent in level:node[0]=0 if parent is None else total-family[id(parent)]
        level=[(child,node) for node,_ in level for child in node[1:] if child]
    output=[];queue=deque([root])
    while queue:
        node=queue.popleft()
        if node is None:output.append(None);continue
        output.append(node[0]);queue.extend(node[1:])
    while output and output[-1] is None:output.pop()
    return output


def random_cousins(rng):
    size=rng.randint(1,25);values=[rng.randint(0,30)]
    for _ in range(1,size):values.append(None if rng.random()<.25 else rng.randint(0,30))
    if all(value is None for value in values[1:]):values=values[:1]
    return [values]


def row_oracle(args):
    mat=args[0];counts=[sum(row) for row in mat];best=max(counts)
    return [counts.index(best),best]


def random_row(rng):
    rows,columns=rng.randint(1,15),rng.randint(1,15)
    return [[[rng.randint(0,1) for _ in range(columns)] for _ in range(rows)]]


def divisibility_oracle(args):
    nums,divisors=args
    return min(divisors,key=lambda divisor:(-sum(value%divisor==0 for value in nums),divisor))


def random_divisibility(rng):
    return [[rng.randint(1,100) for _ in range(rng.randint(1,20))],rng.sample(range(1,31),rng.randint(1,10))]


WIDTHS="""\
def integer_column_widths(grid):
    columns=len(grid[0]);answer=[0]*columns
    for row in grid:
        for column,value in enumerate(row):answer[column]=max(answer[column],len(str(value)))
    return answer
"""

SCORES="""\
def prefix_conversion_scores(nums):
    maximum=total=0;answer=[]
    for value in nums:
        maximum=max(maximum,value);total+=value+maximum;answer.append(total)
    return answer
"""

COUSINS="""\
def replace_tree_values_with_cousins(root):
    from collections import deque
    root.val=0;queue=deque([root])
    while queue:
        parents=list(queue);queue.clear();level_sum=0
        for parent in parents:
            for child in (parent.left,parent.right):
                if child:level_sum+=child.val;queue.append(child)
        for parent in parents:
            sibling_sum=(parent.left.val if parent.left else 0)+(parent.right.val if parent.right else 0)
            if parent.left:parent.left.val=level_sum-sibling_sum
            if parent.right:parent.right.val=level_sum-sibling_sum
    return root
"""

ROWS="""\
def row_with_most_ones(mat):
    best_index=best_count=0
    for index,row in enumerate(mat):
        count=sum(row)
        if count>best_count:best_index,best_count=index,count
    return [best_index,best_count]
"""

DIVISIBILITY="""\
def maximum_divisibility_score(nums,divisors):
    best_divisor=min(divisors);best_score=-1
    for divisor in divisors:
        score=sum(value%divisor==0 for value in nums)
        if score>best_score or score==best_score and divisor<best_divisor:
            best_divisor,best_score=divisor,score
    return best_divisor
"""


BATCH={
2639:entry('integer_column_widths',[('grid','list[list[int]]')],'list[int]',['matrices','strings'],
    ['grid is a nonempty rectangular integer matrix.','A column width is the greatest printed character length in that column; a minus sign counts.','Return widths from leftmost column to rightmost.'],
    [([[[1],[22],[333]]],'The printed lengths one, two, and three make the sole column width three.'),([[[ -15,1],[7,2000]]],'The first column needs three characters for -15 and the second needs four for 2000.')],
    [[g] for g in [[[0]],[[1]],[[-1]],[[10]],[[-10]],[[1,2]],[[1],[2]],[[1,-20],[300,4]],[[999,-1],[-1000,22]],[[0,0],[0,0]],[[5,-55,555]],[[1,20,300],[4000,50,6]],[[-99999999,1],[2,-3]],[[7,8],[90,1],[2,3456]]]],
    WIDTHS,[WIDTHS.replace('len(str(value))','len(str(abs(value)))'),WIDTHS.replace('answer[column]','answer[0]')],
    ['Ignores the minus sign of negative values.','Writes every width into the first column slot.'],widths_oracle,random_widths,
    ['Convert each integer to its ordinary string representation.','Maintain one maximum character length per column.','Visit every matrix cell and update only its column maximum.','Every candidate printed width is examined exactly once, and string conversion naturally includes a negative sign.'],'O(rows*columns)','O(columns)',3),
2640:entry('prefix_conversion_scores',[('nums','list[int]')],'list[int]',['arrays','prefix sums'],
    ['For index i, conversion[i] equals nums[i] plus the maximum value from nums[0:i+1].','The score of a prefix is the sum of its conversion values.','Return the score for every nonempty prefix in order.'],
    [([[2,3,7,5,10]],'Conversion values are 4, 6, 14, 12, and 20, giving cumulative scores 4, 10, 24, 36, and 56.'),([[1,1,2,4,8,16]],'Tracking the running maximum gives scores 2, 4, 8, 16, 32, and 64.')],
    [[a] for a in [[1],[5,1],[1,5],[3,3,3],[1,2,3],[3,2,1],[2,3,7,5,10],[10,1,10,1],[1,100,1],[4,2,8,3,9],[9,8,7,6,5],[2,2,3,2,4],[1000000000,1],[1,2,4,8,16]]],
    SCORES,[SCORES.replace('maximum=max(maximum,value)','maximum=value'),SCORES.replace('total+=value+maximum','total+=maximum')],
    ['Uses only the current value rather than the prefix maximum.','Omits nums[i] from each conversion value.'],scores_oracle,random_scores,
    ['Track the maximum encountered while scanning left to right.','Add current value plus that maximum to a cumulative score.','Append the cumulative score after each position.','The maintained maximum is exactly max(nums[0:i+1]), and the running total inductively equals the score of that prefix.'],'O(n)','O(n)',5),
2641:entry('replace_tree_values_with_cousins',[('root','TreeNode | None')],'TreeNode | None',['trees','breadth-first search'],
    ['The input is a nonempty binary tree.','Replace each node value with the sum of values at the same depth whose parents differ.','Mutate and return the original root.'],
    [([[5,4,9,1,10,None,7]],'The root and its children have no cousins; the last level becomes 7, 7, and 11.'),([[3,1,2]],'Neither child has a different-parent node at its depth, so every result value is zero.')],
    [[a] for a in [[1],[1,2],[1,None,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[1,2,3,None,4,None,5],[0,0,0,1,2,3,4],[10,5,15,2,7,12,20],[1,1,1,1,1,1,1],[8,4,12,None,6,10,None],[5,3,8,1,None,7,9],[2,4,6,8,10,None,12],[9,2,3,None,4,5,6]]],
    COUSINS,[COUSINS.replace('level_sum-sibling_sum','level_sum'),COUSINS.replace('root.val=0','root.val=root.val')],
    ['Includes siblings in each node value instead of excluding its parent family.','Leaves the root unchanged even though it has no cousins.'],cousins_oracle,random_cousins,
    ['Process the tree one depth at a time.','Before changing children, compute the sum of all original child values on the next level.','For each parent, subtract the combined original values of its own children from that level sum and assign the result to both children.','All next-level values are read before mutation, and level sum minus one sibling family is exactly the cousin definition.'],'O(nodes)','O(width)',6),
2643:entry('row_with_most_ones',[('mat','list[list[int]]')],'list[int]',['matrices','counting'],
    ['mat is a nonempty binary matrix.','Find the row containing the most ones.','Return [row_index,ones_count], choosing the smallest index on a tie.'],
    [([[[0,1],[1,0]]],'Both rows contain one one, so the smaller index zero wins.'),([[[0,0],[1,1]]],'Row one contains two ones and is uniquely best.')],
    [[m] for m in [[[0]],[[1]],[[0],[1]],[[1],[0]],[[0,0],[0,0]],[[1,1],[1,1]],[[1,0,1],[0,1,0]],[[0,0,1],[1,1,0],[1,1,1]],[[1,0],[1,1],[1,1]],[[0,1,0,1]],[[0],[0],[0]],[[1],[1],[1]],[[1,0,0],[0,1,1]],[[0,0,0],[0,0,1],[1,1,0]]]],
    ROWS,[ROWS.replace('count>best_count','count>=best_count'),ROWS.replace('count=sum(row)','count=len(row)')],
    ['Replaces the winner on ties and returns the largest tied index.','Counts columns rather than one-valued cells.'],row_oracle,random_row,
    ['Count ones in each row.','Keep the best index and count seen so far.','Update only for a strictly larger count so an earlier tied row remains selected.','Each row is evaluated once, and the invariant retains the required maximum with smallest-index tie-breaking.'],'O(rows*columns)','O(1)',3),
2644:entry('maximum_divisibility_score',[('nums','list[int]'),('divisors','list[int]')],'int',['arrays','counting'],
    ['The score of a divisor is how many values in nums it divides exactly.','Return the divisor having the greatest score.','Break score ties by returning the numerically smallest divisor.'],
    [([[2,9,15,50],[5,3,7,2]],'Divisors two, three, and five each score two, so the smallest tied divisor two wins.'),([[4,7,9,3,9],[5,2,3]],'Divisor three divides three values and has the highest score.')],
    [[a,b] for a,b in [([1],[1]),([1],[2]),([2,4,6],[2,3]),([3,6,9],[2,3]),([5,7,11],[2,3,4]),([10,20,30],[5,10]),([12,18,24],[2,3,6]),([7,14,21],[7,1]),([8,9,10],[2,5]),([100],[3,4,5]),([2,3,5,7],[2,3,5,7]),([6,10,15,30],[2,3,5]),([1,1,1],[2,3]),([24,36,48],[8,6,12])]],
    DIVISIBILITY,[DIVISIBILITY.replace('divisor<best_divisor','divisor>best_divisor'),DIVISIBILITY.replace('value%divisor==0','value%divisor!=0')],
    ['Chooses the largest divisor when scores tie.','Counts values not divisible by the divisor.'],divisibility_oracle,random_divisibility,
    ['Evaluate each candidate divisor independently.','Count values whose remainder modulo that divisor is zero.','Replace the winner for a larger score, or for an equal score with a smaller divisor.','The scan directly evaluates the definition for every allowed choice, and the paired comparison implements both ranking rules.'],'O(nums*divisors)','O(1)',3),
}

BATCH[2641]['params'][0]=('root','TreeNode | None','treenode')
BATCH[2641]['adapter']='treenode'
