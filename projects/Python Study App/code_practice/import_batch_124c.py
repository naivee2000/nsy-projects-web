"""Third slice of workbook batch 124."""

from itertools import permutations

from .import_batch_055 import entry


def root_oracle(args):
    values = args[0]
    return values[0] == values[1] + values[2]


def random_root(rng):
    return [[rng.randint(0, 100) for _ in range(3)]]


def brightness_oracle(args):
    n, lights, requirement = args
    brightness = [0] * n
    for position, radius in lights:
        for index in range(max(0, position - radius), min(n, position + radius + 1)):
            brightness[index] += 1
    return sum(value >= needed for value, needed in zip(brightness, requirement))


def random_brightness(rng):
    n = rng.randint(1, 20)
    lights = [[rng.randrange(n), rng.randint(0, n)] for _ in range(rng.randint(0, 15))]
    return [n, lights, [rng.randint(0, 8) for _ in range(n)]]


def closest_oracle(args):
    return min(args[0], key=lambda value: (abs(value), -value))


def random_closest(rng):
    return [[rng.randint(-100, 100) for _ in range(rng.randint(1, 25))]]


def supplies_oracle(args):
    total, first, second = args
    return sum(1 for a in range(total // first + 1) for b in range(total // second + 1)
               if a * first + b * second <= total)


def random_supplies(rng):
    return [rng.randint(0, 80), rng.randint(1, 20), rng.randint(1, 20)]


def sequence_oracle(args):
    scores, edges = args
    adjacency = {tuple(sorted(edge)) for edge in edges}
    best = -1
    for nodes in permutations(range(len(scores)), 4):
        if all(tuple(sorted((nodes[index], nodes[index + 1]))) in adjacency for index in range(3)):
            best = max(best, sum(scores[node] for node in nodes))
    return best


def random_sequence(rng):
    n = rng.randint(4, 8)
    edges = [[left, right] for left in range(n) for right in range(left + 1, n) if rng.randrange(3) == 0]
    return [[rng.randint(1, 30) for _ in range(n)], edges]


ROOT = '''\
def root_equals_children_sum(root):
    return root.val==root.left.val+root.right.val
'''

BRIGHTNESS = '''\
def count_required_brightness(n,lights,requirement):
    changes=[0]*(n+1)
    for position,radius in lights:
        left=max(0,position-radius);right=min(n-1,position+radius)
        changes[left]+=1;changes[right+1]-=1
    current=answer=0
    for index in range(n):
        current+=changes[index]
        answer+=current>=requirement[index]
    return answer
'''

CLOSEST = '''\
def closest_number_to_zero(nums):
    return min(nums,key=lambda value:(abs(value),-value))
'''

SUPPLIES = '''\
def count_pen_pencil_combinations(total,cost1,cost2):
    answer=0
    for first in range(total//cost1+1):
        answer+=(total-first*cost1)//cost2+1
    return answer
'''

SEQUENCE = '''\
def maximum_four_node_sequence_score(scores,edges):
    neighbors=[[] for _ in scores]
    for left,right in edges:
        neighbors[left].append(right);neighbors[right].append(left)
    for node in range(len(scores)):
        neighbors[node]=sorted(neighbors[node],key=lambda other:scores[other],reverse=True)[:3]
    answer=-1
    for middle_left,middle_right in edges:
        for outer_left in neighbors[middle_left]:
            for outer_right in neighbors[middle_right]:
                if len({outer_left,middle_left,middle_right,outer_right})==4:
                    answer=max(answer,scores[outer_left]+scores[middle_left]+scores[middle_right]+scores[outer_right])
    return answer
'''


BATCH = {
    2236: entry('root_equals_children_sum',[('root','TreeNode')],'bool',['trees','binary trees'],['The input tree has exactly one root and its two non-null children.','Compare node values, not node identities.','Return whether root.val equals left.val plus right.val.'],[([[10,4,6]],'Four plus six equals the root value ten.'),([[5,3,1]],'The child sum is four, which does not equal five.')],[[x] for x in [[0,0,0],[1,0,1],[2,1,1],[3,1,1],[5,3,1],[10,4,6],[100,40,60],[7,7,0],[9,0,9],[12,5,8],[20,11,9],[4,2,3],[50,25,25],[6,1,5]]],ROOT,[ROOT.replace('+','-'),ROOT.replace('==','!=')],['Subtracts the right child instead of adding both children.','Returns the negation of the required equality.'],root_oracle,random_root,['Only the three stored node values matter.','Read both child values and add them before comparing with the root.','Return root.val == root.left.val + root.right.val.','The expression directly evaluates the single equality in the problem definition.'],'O(1)','O(1)',3),
    2237: entry('count_required_brightness',[('n','int'),('lights','list[list[int]]'),('requirement','list[int]')],'int',['arrays','prefix sums'],['Street positions are the integers zero through n-1.','A light [position,radius] illuminates the inclusive clipped interval position-radius through position+radius.','Brightness is the number of covering lights; count positions meeting or exceeding their individual requirement.'],[([5,[[0,1],[2,1],[3,2]],[0,2,1,4,1]],'The computed brightness meets the requirement at four of the five positions.'),([3,[],[0,1,0]],'With no lights, only the two positions requiring zero brightness qualify.')],[[n,l,r] for n,l,r in [(1,[],[0]),(1,[[0,0]],[1]),(5,[[0,1],[2,1],[3,2]],[0,2,1,4,1]),(3,[],[0,1,0]),(4,[[1,0]],[0,1,1,0]),(5,[[2,10]],[1,1,1,1,1]),(6,[[0,2],[5,2]],[1,1,1,1,1,1]),(5,[[2,1],[2,1]],[0,2,2,2,0]),(2,[[0,0],[1,0]],[1,1]),(7,[[3,0]],[0,0,0,1,0,0,0]),(4,[[0,3]],[2,1,1,1]),(5,[[1,1],[3,1]],[1,1,2,1,1]),(8,[[2,2],[6,1]],[1,1,1,1,1,1,1,1]),(3,[[0,5],[2,5]],[2,2,2])]],BRIGHTNESS,[BRIGHTNESS.replace('right+1','right'),BRIGHTNESS.replace('current>=requirement[index]','current>requirement[index]')],['Ends each illumination interval one position too early.','Requires brightness to be strictly greater instead of allowing equality.'],brightness_oracle,random_brightness,['Range additions can encode every lamp interval with two endpoint changes.','Add one at the clipped left endpoint and subtract one just after the clipped right endpoint.','Prefix-sum the change array and compare each brightness with its requirement.','Each lamp contributes one exactly throughout its interval; prefix accumulation combines all lamps, so each comparison uses the true brightness.'],'O(n+lights)','O(n)',6),
    2239: entry('closest_number_to_zero',[('nums','list[int]')],'int',['arrays'],['Return an element with minimum absolute value.','If positive x and negative x tie, return positive x.','The input contains at least one integer.'],[([[-4,-2,1,4,8]],'One has the smallest distance to zero.'),([[-2,2]],'Both values are equally distant, so the larger value two wins the tie.')],[[x] for x in [[0],[1],[-1],[-4,-2,1,4,8],[-2,2],[-5,-3], [3,5],[-1,1,2],[-10,4,6],[-7,-2,-9],[8,2,5],[-100,100,0],[-3,3,-2,2],[9,-8,7],[-6,-4,5],[12,-1,-2]]],CLOSEST,[CLOSEST.replace('-value','value'),CLOSEST.replace('abs(value)','value')],['Breaks equal-distance ties toward the negative value.','Minimizes the signed value instead of distance from zero.'],closest_oracle,random_closest,['Compare numbers first by distance from zero and then by the preferred tie direction.','The key (abs(value), -value) makes a smaller distance primary and a larger value secondary.','Return min(nums, key=lambda value: (abs(value), -value)).','Tuple ordering exactly models the required two-level ranking, so its minimum is the required array element.'],'O(n)','O(1)',3),
    2240: entry('count_pen_pencil_combinations',[('total','int'),('cost1','int'),('cost2','int')],'int',['math','enumeration'],['Choose nonnegative integer quantities of both item types.','A combination is valid when its total cost is at most the budget, so money may remain.','Different quantity pairs count separately, including buying zero of either or both.'],[([20,10,5],'For zero, one, or two pens there are five, three, or one pencil choices, totaling nine.'),([5,10,10],'Only buying zero of both items fits, so the answer is one.')],[[t,a,b] for t,a,b in [(0,1,1),(1,1,1),(20,10,5),(5,10,10),(10,10,10),(9,2,3),(100,1,1),(15,4,6),(7,7,2),(30,8,9),(25,5,7),(3,2,2),(50,13,17),(12,20,3)]],SUPPLIES,[SUPPLIES.replace('+1\n','\n'),SUPPLIES.replace('total//cost1+1','total//cost1')],['Omits the zero-pencil choice for each fixed pen count.','Omits the maximum affordable number of pens from enumeration.'],supplies_oracle,random_supplies,['Fix the number of the first item, then count all affordable quantities of the second.','For first from zero through total//cost1, the second quantity has floor(remaining/cost2)+1 choices.','Sum (total-first*cost1)//cost2+1 across every feasible first quantity.','Every valid quantity pair has one unique first quantity and is counted once among that iteration’s complete range of second quantities.'],'O(total/cost1)','O(1)',5),
    2242: entry('maximum_four_node_sequence_score',[('scores','list[int]'),('edges','list[list[int]]')],'int',['graphs','sorting','enumeration'],['Choose four distinct nodes a,b,c,d with edges a-b, b-c, and c-d.','The sequence score is the sum of all four node scores.','Return the maximum score, or -1 when no valid four-node sequence exists.'],[([[5,2,9,8,4],[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]],'The sequence 0-1-2-3 has score 5+2+9+8=24.'),([[9,20,6,4,11,12],[[0,3],[5,3],[2,4],[1,3]]],'No chain can contain four distinct nodes, so return negative one.')],[[s,e] for s,e in [([1,2,3,4],[[0,1],[1,2],[2,3]]),([1,2,3,4],[]),([5,2,9,8,4],[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]),([9,20,6,4,11,12],[[0,3],[5,3],[2,4],[1,3]]),([1,1,1,1],[[0,1],[1,2],[2,3],[3,0]]),([10,1,1,10],[[0,1],[1,2],[2,3]]),([8,7,6,5,4],[[0,1],[0,2],[0,3],[0,4]]),([3,9,8,7,6],[[0,1],[1,2],[2,3],[3,4]]),([5,10,20,1,2],[[0,1],[1,2],[2,3],[2,4]]),([4,3,2,1],[[0,1],[0,2],[1,3],[2,3]]),([100,1,2,3,4],[[0,1],[1,2],[2,3],[3,4],[0,4]]),([2,8,4,9,5,7],[[0,1],[1,2],[2,3],[3,4],[4,5],[1,4]]),([6,5,4,3,2],[[0,1],[1,2]]),([7,1,9,2,8],[[0,1],[1,2],[2,3],[3,4],[0,2]])]],SEQUENCE,[SEQUENCE.replace('[:3]','[:2]'),SEQUENCE.replace('==4','>=3')],['Keeps only two neighbors per middle node and may discard the best non-conflicting outer choice.','Allows an outer node to repeat and counts sequences with only three distinct nodes.'],sequence_oracle,random_sequence,['Treat every edge b-c as the middle of a possible four-node sequence.','Only the three highest-score neighbors of each middle endpoint are needed because at most two nodes are forbidden by distinctness.','For each edge, try pairs from its endpoints’ top-three neighbor lists and keep sums whose four nodes are distinct.','Any optimal outer choice below third place would have three better neighbors, and at most two conflict, so some equally feasible better choice must exist.'],'O(edges*constant + edges log degree)','O(nodes+edges)',8),
}

BATCH[2236]['params'][0] = ('root','TreeNode','treenode')
BATCH[2242]['boundaries'].append([[100,100,90,80,70],[[0,1],[0,2],[0,3],[1,2],[1,4]]])
