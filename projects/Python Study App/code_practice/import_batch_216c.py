"""Stair paths, server upgrades, tree levels, occurrence queries, and ball colors."""
import math

from .import_batch_055 import entry


def stairs_oracle(args):
    target = args[0]; total = 0
    for jumps in range(32):
        downs = (1 << jumps) - target
        if 0 <= downs <= jumps + 1:total += math.comb(jumps + 1, downs)
    return total


def random_stairs(rng):
    return [rng.randint(0, 1000)]


def upgrades_oracle(args):
    count, upgrade, sell, money = args; answer = []
    for index, size in enumerate(count):
        best = 0
        for chosen in range(size + 1):
            if chosen * upgrade[index] <= money[index] + (size-chosen) * sell[index]:best = chosen
        answer.append(best)
    return answer


def random_upgrades(rng):
    size = rng.randint(1, 8)
    return [[rng.randint(0, 20) for _ in range(size)],[rng.randint(1, 15) for _ in range(size)],
            [rng.randint(1, 15) for _ in range(size)],[rng.randint(0, 100) for _ in range(size)]]


def tree_levels(values):
    if not values:return []
    levels = []; queue = [(values[0], 1)]; cursor = 1
    while queue:
        value, level = queue.pop(0)
        while len(levels) < level:levels.append(0)
        levels[level-1] += value
        for _ in range(2):
            if cursor < len(values):
                child = values[cursor]; cursor += 1
                if child is not None:queue.append((child,level+1))
    return levels


def level_oracle(args):
    sums = tree_levels(args[0]); return min(range(len(sums)), key=lambda index: (sums[index],index)) + 1


def random_level(rng):
    size = rng.randint(1, 31); values = [rng.randint(-20, 30)]
    for index in range(1, size):values.append(rng.randint(-20,30) if values[(index-1)//2] is not None and rng.random()<.8 else None)
    while values and values[-1] is None:values.pop()
    return [values]


def occurrences_oracle(args):
    nums, queries, value = args; positions = [index for index,item in enumerate(nums) if item == value]
    return [positions[rank-1] if 0 < rank <= len(positions) else -1 for rank in queries]


def random_occurrences(rng):
    nums = [rng.randint(0, 6) for _ in range(rng.randint(1, 20))]
    return [nums,[rng.randint(1, 12) for _ in range(rng.randint(1, 10))],rng.randint(0,6)]


def colors_oracle(args):
    _, queries = args; balls = {}; answer = []
    for ball, color in queries:
        balls[ball] = color; answer.append(len(set(balls.values())))
    return answer


def random_colors(rng):
    limit = rng.randint(1, 15)
    return [limit,[[rng.randint(0,limit),rng.randint(1,8)] for _ in range(rng.randint(1,20))]]


STAIRS = '''def ways_to_reach_stair(k):
    import math
    answer=0
    for jumps in range(32):
        downs=(1<<jumps)-k
        if 0<=downs<=jumps+1:answer+=math.comb(jumps+1,downs)
    return answer
'''


UPGRADES = '''def maximum_upgradable_servers(count,upgrade,sell,money):
    return [min(size,(cash+size*sale)//(cost+sale)) for size,cost,sale,cash in zip(count,upgrade,sell,money)]
'''


LEVEL = '''def minimum_sum_tree_level(root):
    queue=[root];level=1;best_level=1;best_sum=10**30
    while queue:
        total=sum(node.val for node in queue)
        if total<best_sum:best_sum=total;best_level=level
        queue=[child for node in queue for child in (node.left,node.right) if child]
        level+=1
    return best_level
'''


OCCURRENCES = '''def occurrence_query_indices(nums,queries,x):
    positions=[index for index,value in enumerate(nums) if value==x]
    return [positions[rank-1] if rank<=len(positions) else -1 for rank in queries]
'''


COLORS = '''def distinct_ball_colors(limit,queries):
    ball_color={};frequencies={};answer=[]
    for ball,color in queries:
        if ball in ball_color:
            old=ball_color[ball];frequencies[old]-=1
            if frequencies[old]==0:del frequencies[old]
        ball_color[ball]=color;frequencies[color]=frequencies.get(color,0)+1
        answer.append(len(frequencies))
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):return [concept,strategy,pseudocode,proof]


BATCH = {
3154:entry('ways_to_reach_stair',[('k','int')],'int',['combinatorics','dynamic programming','bit manipulation'],['k is a nonnegative integer.','Start at stair one with jump exponent zero; an up move adds 2^exponent and then increments the exponent.','A down move subtracts one, cannot be used at stair zero, and cannot follow another down move; count every operation sequence that visits k.'],[([0],'Use one down immediately, or jump up once and then use two separated down moves; there are two ways.'),([1],'The empty sequence, one up followed by one down, one down followed by one up, and a longer valid route give four ways.')],[[k] for k in [0,1,2,3,4,5,6,7,8,9,10,15,16,31]],STAIRS,[STAIRS.replace('(1<<jumps)-k','(1<<jumps)-k-1'),STAIRS.replace('math.comb(jumps+1,downs)','math.comb(jumps,downs)')],['Uses the wrong baseline for the position after all upward jumps.','Provides only jumps slots for downward moves and misses the slot after the last up move.'],stairs_oracle,random_stairs,lesson('After j upward moves, their sum plus the initial stair equals 2^j; reaching k therefore requires exactly 2^j-k downward moves.','Nonconsecutive downs occupy a subset of the j+1 gaps before, between, and after upward moves.','For each j, let d=2^j-k; when 0≤d≤j+1 add C(j+1,d).','Choosing gaps produces every valid ordering exactly once; the bounds also prevent descending below zero for any counted route.'),'O(log k)','O(1)',8),
3155:entry('maximum_upgradable_servers',[('count','list[int]'),('upgrade','list[int]'),('sell','list[int]'),('money','list[int]')],'list[int]',['math','binary search','arrays'],['All four arrays have the same nonzero length; costs and sale prices are positive and counts and money are nonnegative.','Within each data center, sell any non-upgraded servers and use its starting money to upgrade the rest.','Return the maximum number upgraded independently for every center.'],[([[4,3],[3,5],[4,2],[8,9]],'The centers can afford three and two upgrades respectively after selling the unused servers.'),([[2],[10],[1],[0]],'Selling one server yields only one unit, so no server can be upgraded.')],[[c,u,s,m] for c,u,s,m in [([4,3],[3,5],[4,2],[8,9]),([2],[10],[1],[0]),([1],[5],[2],[5]),([0],[3],[4],[10]),([5],[2],[1],[0]),([5],[10],[10],[0]),([3],[5],[2],[9]),([10],[4],[3],[1]),([2,8],[7,2],[3,5],[20,0]),([1,1],[1,100],[1,1],[0,99]),([20],[9],[2],[50]),([6,4,2],[3,8,5],[2,1,10],[0,20,0]),([100],[5],[7],[13]),([7,9],[6,4],[1,3],[12,8])]],UPGRADES,[UPGRADES.replace('cash+size*sale','cash+(size-1)*sale'),'''def maximum_upgradable_servers(count,upgrade,sell,money):
    return [(cash+size*sale)//(cost+sale) for size,cost,sale,cash in zip(count,upgrade,sell,money)]
'''],['Assumes one server is unavailable for sale even when upgrading fewer, underestimating funds.','Fails to cap the formula by the number of existing servers.'],upgrades_oracle,random_upgrades,lesson('If x servers are upgraded, the other count-x may be sold, so affordability is x*upgrade≤money+(count-x)*sell.','Rearrange the inequality to isolate x and cap the quotient by count.','x=min(count,floor((money+count*sell)/(upgrade+sell))).','The affordability inequality is monotone in x; its largest integral solution is exactly the capped quotient.'),'O(centers)','O(1) excluding output',5),
3157:entry('minimum_sum_tree_level',[('root','TreeNode')],'int',['trees','breadth-first search'],['root is a nonempty binary tree and node values may be negative.','The root is level one; a level sum includes every node at that depth.','Return the smallest level number having the minimum sum.'],[([[50,6,2,30,80,7]],'Level sums are 50, 8, and 117, so level two is the unique minimum.'),([[1,-2,-3,4,5]],'The second level sums to -5, smaller than the other level sums.')],[[t] for t in [[50,6,2,30,80,7],[1],[1,2,3],[1,-2,-3,4,5],[5,1,2,10,10,-20,-20],[0,0,0],[10,-5,None,-10],[3,1,1,1,1],[8,4,12,2,6,10,14],[-1,-2,-3,-4,-5,-6,-7],[5,None,1,None,2],[100,1,1,1,1,1,1],[2,3,4,-20,None,None,-20],[7,-1,9,-2,-3,4,5]]],LEVEL,[LEVEL.replace('if total<best_sum','if total<=best_sum'),LEVEL.replace('best_sum=10**30','best_sum=0')],['Replaces an earlier tied level with a later one instead of returning the smallest level.','Initializes the best sum to zero and can leave level one selected when all level sums are positive.'],level_oracle,random_level,lesson('Breadth-first traversal naturally groups exactly the nodes sharing one level.','Compute each frontier sum, update only on a strict improvement, then build the child frontier.','Initialize best to infinity; for level=1.., sum queue, record if smaller, enqueue children.','Every node appears in exactly one frontier, and strict comparison preserves the earliest level on equal sums.'),'O(nodes)','O(width)',5),
3159:entry('occurrence_query_indices',[('nums','list[int]'),('queries','list[int]'),('x','int')],'list[int]',['arrays','hash tables'],['nums and queries are nonempty; every query is a positive occurrence rank.','Occurrences are numbered from one in left-to-right order, while returned array indices are zero-based.','Return -1 when the requested occurrence of x does not exist.'],[([[1,3,1,7],[1,3,2,4],1],'The first and second ones occur at indices zero and two; the third and fourth do not exist.'),([[2,2,2],[3,1],2],'The third two is at index two and the first is at index zero.')],[[n,q,x] for n,q,x in [([1,3,1,7],[1,3,2,4],1),([2,2,2],[3,1],2),([1],[1],1),([1],[2],1),([1,2,3],[1],4),([0,1,0],[2,1],0),([5,4,5,5],[1,2,3,4],5),([9,8,7],[1,2],8),([1,1,2,1],[3],1),([3,3,3,3],[4,1],3),([1,2,1,2,1],[2,3],2),([-1,0,-1],[1,2],-1),([7,6,7,6,7,6],[3,1],7),([4,4,5,4],[2,4],4)]],OCCURRENCES,[OCCURRENCES.replace('positions[rank-1]','positions[rank]'),OCCURRENCES.replace('enumerate(nums)','enumerate(nums,1)')],['Treats the one-based occurrence rank as a zero-based list index.','Returns one-based array positions instead of required zero-based indices.'],occurrences_oracle,random_occurrences,lesson('All queries ask about the same value, so scan nums once and store its occurrence positions.','Translate each one-based requested rank to positions[rank-1] after a bounds check.','positions=[i for i if nums[i]==x]; map q to positions[q-1] or -1.','The positions list is in occurrence order, making its rank-to-index correspondence exact.'),'O(len(nums)+len(queries))','O(occurrences)',5),
3160:entry('distinct_ball_colors',[('limit','int'),('queries','list[list[int]]')],'list[int]',['hash tables','simulation'],['Ball labels range from zero through limit; queries is nonempty and every color is positive.','Each query [ball,color] replaces that ball’s previous color, if any.','After every update, return the number of different colors currently assigned to at least one ball.'],[([4,[[1,4],[2,5],[1,3],[3,4]]],'The distinct-color counts after replacement are one, two, two, and three.'),([1,[[0,1],[1,1],[0,2]]],'The two balls first share color one; recoloring ball zero produces two distinct colors.')],[[l,q] for l,q in [(4,[[1,4],[2,5],[1,3],[3,4]]),(1,[[0,1],[1,1],[0,2]]),(0,[[0,5]]),(0,[[0,1],[0,2]]),(2,[[0,1],[1,2],[2,3]]),(2,[[0,1],[1,1],[2,1]]),(3,[[1,2],[1,2]]),(3,[[1,2],[2,3],[1,3]]),(5,[[0,9],[5,9],[3,8]]),(2,[[0,1],[1,2],[0,2],[1,1]]),(4,[[4,1],[3,2],[2,1],[1,2]]),(10,[[1,5],[2,6],[3,7],[2,5]]),(1,[[0,3],[1,4],[0,4],[1,3]]),(6,[[1,1],[2,2],[3,3],[1,3],[2,3]])]],COLORS,[COLORS.replace('if frequencies[old]==0:del frequencies[old]',''),COLORS.replace('ball_color[ball]=color;frequencies[color]','frequencies[color]')],['Keeps zero-frequency colors in the map and continues counting them.','Never records a ball’s new color, so later recoloring cannot decrement the old color.'],colors_oracle,random_colors,lesson('Track both directions needed by updates: each ball’s current color and each color’s number of balls.','On replacement decrement and possibly delete the old color, then increment the new color.','Update ball_color and color_count; append len(color_count).','A color is present exactly when its maintained frequency is positive, so the map size is the desired distinct count.'),'O(queries)','O(colored balls+colors)',5),
}

BATCH[3157]['params'][0]=('root','TreeNode','treenode')
