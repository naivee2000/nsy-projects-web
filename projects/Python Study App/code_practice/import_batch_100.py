"""First half of batch 100: grids, simulation, enumeration, trees, and graphs."""
from collections import defaultdict, deque
from itertools import combinations

from .import_batch_055 import entry


MOD = 1_000_000_007


def product_oracle(args):
    grid = args[0]
    products = []
    def walk(row, column, value):
        value *= grid[row][column]
        if row == len(grid) - 1 and column == len(grid[0]) - 1:
            products.append(value)
            return
        if row + 1 < len(grid): walk(row + 1, column, value)
        if column + 1 < len(grid[0]): walk(row, column + 1, value)
    walk(0, 0, 1)
    answer = max(products)
    return answer % MOD if answer >= 0 else -1


def crawler_oracle(args):
    path = []
    for operation in args[0]:
        if operation == '../':
            if path: path.pop()
        elif operation != './':
            path.append(operation)
    return len(path)


def wheel_oracle(args):
    customers, boarding_cost, running_cost = args
    waiting = profit = best_profit = 0
    best_rotation = -1
    rotation = 0
    while rotation < len(customers) or waiting:
        if rotation < len(customers): waiting += customers[rotation]
        boarded = min(4, waiting)
        waiting -= boarded
        rotation += 1
        profit += boarded * boarding_cost - running_cost
        if profit > best_profit:
            best_profit, best_rotation = profit, rotation
    return best_rotation


def requests_oracle(args):
    n, requests = args
    for size in range(len(requests), -1, -1):
        for selected in combinations(requests, size):
            balance = [0] * n
            for source, target in selected:
                balance[source] -= 1
                balance[target] += 1
            if not any(balance): return size
    return 0


def alerts_oracle(args):
    grouped = defaultdict(list)
    for name, clock in zip(*args):
        grouped[name].append(int(clock[:2]) * 60 + int(clock[3:]))
    answer = []
    for name, times in grouped.items():
        times.sort()
        if any(times[index + 2] - times[index] <= 60 for index in range(len(times) - 2)):
            answer.append(name)
    return sorted(answer)


def special_oracle(args):
    nums = args[0]
    return next((x for x in range(1, len(nums) + 1) if sum(value >= x for value in nums) == x), -1)


def level_values(values):
    if not values: return []
    levels = [[values[0]]]
    parents = [values[0]]
    cursor = 1
    while parents and cursor < len(values):
        children = []
        for parent in parents:
            if parent is None: continue
            for _ in range(2):
                if cursor >= len(values): break
                child = values[cursor]
                cursor += 1
                if child is not None: children.append(child)
        if children: levels.append(children)
        parents = children
    return levels


def even_odd_oracle(args):
    for depth, values in enumerate(level_values(args[0])):
        if depth % 2 == 0:
            if any(value % 2 == 0 for value in values) or any(a >= b for a, b in zip(values, values[1:])): return False
        elif any(value % 2 for value in values) or any(a <= b for a, b in zip(values, values[1:])): return False
    return True


def one_bit_oracle(args):
    start = args[0]
    queue = deque([(start, 0)])
    seen = {start}
    width = max(2, start.bit_length() + 1)
    while queue:
        value, distance = queue.popleft()
        if value == 0: return distance
        neighbors = [value ^ 1]
        for bit in range(1, width):
            if value & (1 << (bit - 1)) and value & ((1 << (bit - 1)) - 1) == 0:
                neighbors.append(value ^ (1 << bit))
        for neighbor in neighbors:
            if neighbor not in seen:
                seen.add(neighbor); queue.append((neighbor, distance + 1))


def depth_oracle(args):
    depth = best = 0
    for char in args[0]:
        depth += char == '('
        best = max(best, depth)
        depth -= char == ')'
    return best


def rank_oracle(args):
    n, roads = args
    edges = {tuple(sorted(edge)) for edge in roads}
    degrees = [0] * n
    for left, right in edges:
        degrees[left] += 1; degrees[right] += 1
    return max(degrees[a] + degrees[b] - ((a, b) in edges) for a in range(n) for b in range(a + 1, n))


def random_product(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(-4, 4) for _ in range(columns)] for _ in range(rows)]]


def random_crawler(rng):
    operations = []
    for _ in range(rng.randint(1, 30)):
        choice = rng.randrange(4)
        operations.append('../' if choice == 0 else './' if choice == 1 else f'd{rng.randint(0, 9)}/')
    return [operations]


def random_wheel(rng):
    return [[rng.randint(0, 10) for _ in range(rng.randint(1, 20))], rng.randint(1, 20), rng.randint(1, 30)]


def random_requests(rng):
    n = rng.randint(1, 6)
    return [n, [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 12))]]


def random_alerts(rng):
    names = ['amy', 'bo', 'cy', 'dan']
    count = rng.randint(1, 30)
    chosen, times = [], []
    for _ in range(count):
        chosen.append(rng.choice(names))
        minute = rng.randrange(24 * 60)
        times.append(f'{minute // 60:02d}:{minute % 60:02d}')
    return [chosen, times]


def random_special(rng): return [[rng.randint(0, 30) for _ in range(rng.randint(1, 25))]]


def random_even_odd(rng):
    values = [rng.randint(1, 30)]
    for _ in range(rng.randint(0, 20)):
        values.append(None if rng.random() < .25 else rng.randint(1, 30))
    while values and values[-1] is None: values.pop()
    return [values or [1]]


def random_one_bit(rng): return [rng.randint(0, 127)]


def random_depth(rng):
    pairs = rng.randint(0, 12)
    text = []
    opened = 0
    for _ in range(pairs * 2 + rng.randint(0, 8)):
        if pairs and (opened == 0 or rng.random() < .55):
            text.append('('); opened += 1; pairs -= 1
        elif opened:
            text.append(')'); opened -= 1
        else: text.append(rng.choice('1+ab'))
    text.extend(')' * opened)
    return [''.join(text)]


def random_rank(rng):
    n = rng.randint(2, 10)
    roads = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < .3]
    return [n, roads]


PRODUCT = '''def maximum_nonnegative_path_product(grid):
 rows,columns=len(grid),len(grid[0]);largest=[[None]*columns for _ in range(rows)];smallest=[[None]*columns for _ in range(rows)]
 largest[0][0]=smallest[0][0]=grid[0][0]
 for row in range(rows):
  for column in range(columns):
   if row==0 and column==0:continue
   previous=[]
   if row:previous.extend((largest[row-1][column],smallest[row-1][column]))
   if column:previous.extend((largest[row][column-1],smallest[row][column-1]))
   products=[value*grid[row][column] for value in previous]
   largest[row][column],smallest[row][column]=max(products),min(products)
 answer=largest[-1][-1]
 return answer%1000000007 if answer>=0 else -1
'''
CRAWLER = '''def minimum_crawler_operations(logs):
 depth=0
 for operation in logs:
  if operation=='../':depth=max(0,depth-1)
  elif operation!='./':depth+=1
 return depth
'''
WHEEL = '''def best_wheel_rotation(customers, boarding_cost, running_cost):
 waiting=profit=best=0;answer=-1;rotation=0
 while rotation<len(customers) or waiting:
  if rotation<len(customers):waiting+=customers[rotation]
  boarded=min(4,waiting);waiting-=boarded;rotation+=1;profit+=boarded*boarding_cost-running_cost
  if profit>best:best=profit;answer=rotation
 return answer
'''
REQUESTS = '''def maximum_balanced_transfer_requests(n, requests):
 balance=[0]*n;best=0
 def search(index,taken):
  nonlocal best
  if taken+len(requests)-index<=best:return
  if index==len(requests):
   if not any(balance):best=max(best,taken)
   return
  source,target=requests[index];balance[source]-=1;balance[target]+=1
  search(index+1,taken+1);balance[source]+=1;balance[target]-=1;search(index+1,taken)
 search(0,0);return best
'''
ALERTS = '''def keycard_alert_names(key_name, key_time):
 visits=defaultdict(list)
 for name,clock in zip(key_name,key_time):visits[name].append(int(clock[:2])*60+int(clock[3:]))
 answer=[]
 for name,times in visits.items():
  times.sort()
  if any(times[i+2]-times[i]<=60 for i in range(len(times)-2)):answer.append(name)
 return sorted(answer)
'''
SPECIAL = '''def special_array_value(nums):
 nums=sorted(nums);n=len(nums)
 for x in range(1,n+1):
  count=sum(value>=x for value in nums)
  if count==x:return x
 return -1
'''
EVEN_ODD = '''def is_even_odd_tree(root):
 queue=deque([root]);even=True
 while queue:
  previous=-10**20 if even else 10**20
  for _ in range(len(queue)):
   node=queue.popleft();value=node.val
   if value%2==(0 if even else 1) or (even and value<=previous) or (not even and value>=previous):return False
   previous=value
   if node.left:queue.append(node.left)
   if node.right:queue.append(node.right)
  even=not even
 return True
'''
ONE_BIT = '''def minimum_one_bit_operations(n):
 answer=0
 while n:
  answer^=n;n>>=1
 return answer
'''
DEPTH = '''def maximum_parentheses_depth(s):
 depth=answer=0
 for char in s:
  if char=='(':depth+=1;answer=max(answer,depth)
  elif char==')':depth-=1
 return answer
'''
RANK = '''def maximal_network_rank(n, roads):
 neighbors=[set() for _ in range(n)]
 for left,right in roads:neighbors[left].add(right);neighbors[right].add(left)
 return max(len(neighbors[a])+len(neighbors[b])-(b in neighbors[a]) for a in range(n) for b in range(a+1,n))
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]
def E(name, params, returns, topics, constraints, examples, cases, reference, wrong, reasons, oracle, generator, hints, time, space, difficulty):
    return entry(name, params, returns, topics, constraints, examples, cases, reference, wrong, reasons, oracle, generator, hints, time, space, difficulty)


BATCH = {
1594:E('maximum_nonnegative_path_product',[('grid','list[list[int]]')],'int',['dynamic-programming','matrices'],['1–15 rows and columns; each value is from -4 through 4.','Move only right or down. Return -1 when every path product is negative; otherwise return the maximum modulo 1,000,000,007.'],[([[[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]]],'Every top-left to bottom-right product is negative, so return -1.'),([[[1,-2,1],[1,-2,1],[3,-4,1]]],'The best nonnegative path has product eight.')],[[g] for g in [[[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]],[[1,-2,1],[1,-2,1],[3,-4,1]],[[1]],[[-1]],[[0,-1]],[[1,2],[3,4]],[[-1,-2],[-3,-4]],[[-1,0],[-2,3]],[[2,-3,4]],[[2],[-3],[4]],[[1,-1,-1],[1,-1,1]],[[4,4],[4,4]],[[1,-4,1],[-2,-3,-1]],[[0]]]],PRODUCT,[PRODUCT.replace("previous.extend((largest[row-1][column],smallest[row-1][column]))","previous.append(largest[row-1][column])").replace("previous.extend((largest[row][column-1],smallest[row][column-1]))","previous.append(largest[row][column-1])"),PRODUCT.replace("value*grid[row][column]","value*(grid[row][column]%1000000007)")],['Tracks only the largest prefix product, losing a negative prefix that can become the maximum after another negative.','Applies the modulus before sign-sensitive comparisons.'],product_oracle,random_product,lesson('A negative cell swaps the roles of best and worst prefix products.','Store both the maximum and minimum product reaching every cell.','Combine both extrema from the upper and left cells, multiply by the current value, and retain the new extrema.','Every path enters from above or left; two extrema suffice because multiplication is monotone or reverses order based on sign.'),'O(rows*columns)','O(rows*columns)',5),
1598:E('minimum_crawler_operations',[('logs','list[str]')],'int',['stacks','simulation'],['1–1,000 operations; each is ../, ./, or a child-folder name ending in /.','The crawler begins at the main folder and cannot move above it. Return the remaining depth.'],[([['d1/','d2/','../','d21/','./']],'The two child moves left after processing the parent and stay operations require two returns.'),([['d1/','../','../','./']],'Returning at the main folder keeps the depth at zero.')],[[x] for x in [[],['d1/'],['../'],['./'],['d1/','d2/','../','d21/','./'],['d1/','../','../','./'],['a/','b/','c/'],['a/','./','b/'],['a/','../','b/'],['../','x/'],['x/','../'],['./','./'],['a/','b/','../','../'],['a/','../','b/','c/']]],CRAWLER,[CRAWLER.replace('max(0,depth-1)','depth-1'),CRAWLER.replace("operation!='./'","operation=='./'")],['Moves above the main folder when ../ appears at depth zero.','Treats staying in place as entering a child folder.'],crawler_oracle,random_crawler,lesson('Only the current depth matters; folder names do not.','Increment for a child, decrement a positive depth for parent, and ignore stay.','Scan the log while clamping every parent move at zero.','These three transitions exactly reproduce the stack size without storing folder names.'),'O(n)','O(1)',3),
1599:E('best_wheel_rotation',[('customers','list[int]'),('boarding_cost','int'),('running_cost','int')],'int',['simulation','greedy'],['1–100,000 arrival batches with 0–10 customers each; costs are positive.','At most four customers board per rotation. Return the earliest rotation with maximum positive profit, or -1.'],[([[8,3],5,6],'After serving the waiting customers, profit reaches its maximum at rotation three.'),([[3,4,0,5,1],1,92],'Every possible stopping point loses money, so return -1.')],[[*x] for x in [([8,3],5,6),([3,4,0,5,1],1,92),([10,9,6],6,4),([3],10,5),([0],10,5),([4],1,4),([5],2,3),([8],3,10),([0,0,8],5,6),([1,1,1,1],5,4),([10,0,0],2,7),([2,2,2],3,5),([9,9],4,15),([4,4,4],2,8)]],WHEEL,[WHEEL.replace('if profit>best','if profit>=best'),WHEEL.replace('while rotation<len(customers) or waiting','while rotation<len(customers)')],['Chooses the latest rotation when several rotations share the maximum profit.','Stops after the arrivals and fails to serve customers still waiting.'],wheel_oracle,random_wheel,lesson('Profit changes only after a rotation, so evaluate every actual rotation once.','Track waiting customers, board four, and update cumulative profit.','Continue after arrivals while anyone waits; update the answer only on a strict new positive maximum.','Simulation preserves arrival order and strict comparison keeps the earliest maximum rotation.'),'O(n+waiting/4)','O(1)',5),
1601:E('maximum_balanced_transfer_requests',[('n','int'),('requests','list[list[int]]')],'int',['backtracking','bitmasks'],['1–20 buildings and at most 16 requests.','Choose the largest subset whose incoming and outgoing counts balance at every building.'],[([3,[[0,0],[1,2],[2,1]]],'All three requests balance: the self-transfer changes nothing and the other two cancel.'),([3,[[0,1],[1,2],[2,0],[0,2]]],'The three-request cycle is balanced; including the extra request would unbalance buildings zero and two.')],[[*x] for x in [(1,[]),(1,[[0,0]]),(2,[[0,1]]),(2,[[0,1],[1,0]]),(3,[[0,0],[1,2],[2,1]]),(3,[[0,1],[1,2],[2,0],[0,2]]),(3,[[0,1],[0,1],[1,0]]),(4,[[0,1],[1,2],[2,3],[3,0]]),(4,[[0,1],[2,3]]),(2,[[0,0],[1,1]]),(3,[[0,2],[2,0],[1,1]]),(5,[[0,1],[1,0],[2,3],[3,4],[4,2]]),(3,[[0,1],[1,0],[0,2],[2,0]]),(2,[[0,1],[1,0],[0,1],[1,0]])]],REQUESTS,[REQUESTS.replace('if not any(balance)','if sum(abs(value) for value in balance)<=2'),REQUESTS.replace('search(index+1,taken+1)','search(index+1,taken)')],['Accepts subsets with one unmatched transfer because their total imbalance is only two.','Fails to count selected requests.'],requests_oracle,random_requests,lesson('A chosen transfer adds one at its destination and removes one at its source.','Backtrack over include/exclude decisions while maintaining net balances.','At the leaf, accept the chosen count only when every balance is zero; prune branches unable to beat best.','Every subset corresponds to one branch path, and zero balances are exactly the feasibility condition.'),'O(2^m*m)','O(n+m)',8),
1604:E('keycard_alert_names',[('key_name','list[str]'),('key_time','list[str]')],'list[str]',['hash-maps','sliding-windows'],['Names and times have equal length from 1 through 100,000; times use HH:MM on one day.','Alert a name for at least three uses within an inclusive 60-minute span; return unique names alphabetically.'],[([['daniel','daniel','daniel','luis','luis','luis','luis'],['10:00','10:40','11:00','09:00','11:00','13:00','15:00']],'Daniel has three uses from 10:00 through 11:00 inclusive; Luis does not.'),([['alice','alice','alice','bob','bob','bob'],['12:01','12:00','18:00','21:00','20:00','19:00']],'Neither person has three uses inside one hour.')],[[*x] for x in [(['daniel','daniel','daniel','luis','luis','luis','luis'],['10:00','10:40','11:00','09:00','11:00','13:00','15:00']),(['alice','alice','alice','bob','bob','bob'],['12:01','12:00','18:00','21:00','20:00','19:00']),(['a'],['00:00']),(['a','a','a'],['00:00','00:30','01:00']),(['a','a','a'],['00:00','00:30','01:01']),(['b','a','a','a','b','b'],['10:00','09:00','09:20','09:40','10:20','10:40']),(['x','x','x'],['23:00','23:30','23:59']),(['x','x','x'],['22:59','23:30','23:59']),(['a','b','a','b','a','b'],['01:00','02:00','01:10','02:10','01:20','02:20']),(['z','z','z','a','a','a'],['12:00','12:30','13:00','00:00','00:30','01:00']),(['m','m'],['10:00','10:00']),(['m','m','m'],['10:00','10:00','10:00']),(['q','q','q','q'],['01:00','02:01','02:30','03:00']),(['a','a','a'],['11:00','10:00','10:30'])]],ALERTS,[ALERTS.replace('<=60','<60'),ALERTS.replace('return sorted(answer)','return answer')],['Excludes a span of exactly one hour.','Returns names in dictionary encounter order instead of alphabetical order.'],alerts_oracle,random_alerts,lesson('After sorting one person’s times, any qualifying triple appears in three consecutive positions.','Group converted minutes by name and compare each time with the time two places later.','Alert when that inclusive difference is at most sixty, then sort the unique names.','If any window contains at least three events, its first three consecutive sorted events also fit in the same window.'),'O(n log n)','O(n)',5),
1608:E('special_array_value',[('nums','list[int]')],'int',['binary-search','sorting'],['1–100 nonnegative integers, each at most 1,000.','Return the unique x such that exactly x entries are at least x, or -1.'],[([[3,5]],'Both entries are at least two, so x=2.'),([[0,0]],'No positive x has exactly x qualifying entries.')],[[x] for x in [[3,5],[0,0],[0,4,3,0,4],[3,6,7,7,0],[1],[0],[1,1],[2,2],[0,1,2,3],[100,100,100],[1,2,3,4],[0,0,3],[5,0,0,0,0],[2,3,4,5,6]]],SPECIAL,[SPECIAL.replace('value>=x','value>x'),SPECIAL.replace('range(1,n+1)','range(1,n)')],['Counts only values strictly greater than x.','Never considers x equal to the full array length.'],special_oracle,random_special,lesson('Only values from one through n can equal their own qualifying count.','Test each candidate against the count of entries at least that candidate.','Return the first equality, otherwise -1.','The qualifying count never increases as x grows, so at most one crossing can satisfy count=x.'),'O(n²)','O(n)',3),
1609:E('is_even_odd_tree',[('root','TreeNode')],'bool',['trees','breadth-first-search'],['1–100,000 nodes with positive integer values.','Even-indexed levels require strictly increasing odd values; odd-indexed levels require strictly decreasing even values.'],[([[1,10,4,3,None,7,9,12,8,6,None,None,2]],'Every level satisfies its required parity and strict direction.'),([[5,4,2,3,3,7]],'Level two repeats three, violating strict increase.')],[[x] for x in [[1],[2],[1,10,4,3,None,7,9,12,8,6,None,None,2],[5,4,2,3,3,7],[1,2,4],[1,4,2],[3,8,6,1,3,5,7],[3,8,6,1,5,3,7],[1,10,4,3,None,7,9],[1,10,4,2,None,7,9],[9,8,6,1,3,5,7],[1,2,None,3],[7,12,10,3,5],[1,10,4,None,None,7,9],[5,6,4,1,3]]],EVEN_ODD,[EVEN_ODD.replace('value<=previous','value<previous').replace('value>=previous','value>previous'),EVEN_ODD.replace("value%2==(0 if even else 1)","value%2==(1 if even else 0)")],['Allows equal adjacent values on a level.','Reverses the required parity at every level.'],even_odd_oracle,random_even_odd,lesson('Each level has independent parity and ordering rules.','Traverse breadth first while remembering the previous value in the current level.','Choose a parity-specific sentinel, reject parity or strict-order violations, and toggle the level rule.','Breadth-first order is left-to-right level order, so every required adjacent comparison is checked exactly once.'),'O(n)','O(width)',5),
1611:E('minimum_one_bit_operations',[('n','int')],'int',['bit-manipulation','recursion'],['0 <= n <= 1,000,000,000.','Use only the stated constrained bit flips and return the minimum operations needed to reach zero.'],[([3],'The sequence 3 to 1 to 0 uses two valid operations.'),([6],'The minimum valid sequence requires four operations.')],[[n] for n in [0,1,2,3,4,5,6,7,8,9,10,15,16,31]],ONE_BIT,[ONE_BIT.replace('answer^=n','answer+=n'),ONE_BIT.replace('n>>=1','n>>=2')],['Adds shifted values instead of applying the inverse-Gray-code XOR recurrence.','Skips every other Gray-code prefix bit.'],one_bit_oracle,random_one_bit,lesson('The allowed moves follow reflected Gray-code order.','Invert a Gray-coded value by XORing all of its right-shifted prefixes.','Repeatedly XOR n into the answer and shift n right until zero.','Each XOR prefix reconstructs one binary bit of the operation index, yielding the unique shortest position of n in the Gray path to zero.'),'O(log n)','O(1)',8),
1614:E('maximum_parentheses_depth',[('s','str')],'int',['strings','stacks'],['The expression is valid and has length at most 100.','Return the maximum number of simultaneously open parentheses.'],[(['(1+(2*3)+((8)/4))+1'],'The deepest section, ((8)/4), has three parentheses open.'),(['1+2'],'No parentheses occur, so the maximum depth is zero.')],[[s] for s in ['(1+(2*3)+((8)/4))+1','1+2','()','(())','()()','((()))','(a+(b))','(1)+((2))+(((3)))','abc','(()())','((a)+(b))','(a(b(c)d)e)','(())()','a+(b*c)']],DEPTH,[DEPTH.replace('answer=max(answer,depth)','answer=max(answer,depth-1)'),DEPTH.replace("elif char==')':depth-=1","elif char==')':depth=0")],['Records one less than the current number of open parentheses.','Resets depth at every close instead of removing only one open parenthesis.'],depth_oracle,random_depth,lesson('Nesting depth equals the number of unmatched opening parentheses at that position.','Maintain a running balance and maximize it immediately after each opening parenthesis.','Increment on (, update the maximum, and decrement on ).','Validity guarantees the balance represents currently open pairs throughout the scan.'),'O(n)','O(1)',3),
1615:E('maximal_network_rank',[('n','int'),('roads','list[list[int]]')],'int',['graphs','counting'],['2–100 cities; roads are unique undirected pairs.','For every pair of cities, count all incident roads once, including their direct road only once.'],[([4,[[0,1],[0,3],[1,2],[1,3]]],'Cities zero and one have combined rank four after counting their shared road once.'),([5,[[0,1],[0,3],[1,2],[1,3],[2,3],[2,4]]],'Cities one and two provide the maximum combined network rank five.')],[[*x] for x in [(2,[]),(2,[[0,1]]),(4,[[0,1],[0,3],[1,2],[1,3]]),(5,[[0,1],[0,3],[1,2],[1,3],[2,3],[2,4]]),(3,[[0,1],[1,2]]),(3,[[0,1],[0,2],[1,2]]),(4,[]),(4,[[0,1]]),(4,[[0,1],[2,3]]),(5,[[0,1],[0,2],[0,3],[0,4]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(6,[[0,1],[0,2],[3,4],[3,5]]),(3,[[0,2],[1,2]]),(4,[[0,2],[0,3],[1,2],[1,3]])]],RANK,[RANK.replace('-(b in neighbors[a])',''),RANK.replace('-(b in neighbors[a])','-1')],['Counts the direct road between the selected cities twice.','Subtracts one even when the selected cities are not directly connected.'],rank_oracle,random_rank,lesson('A pair’s rank is the sum of its degrees minus one when the cities are directly linked.','Build neighbor sets, then evaluate every unordered city pair.','For a<b, add both set sizes and subtract membership of b in a’s set.','Every road incident to either city appears once in a degree sum, except their shared road appears in both and needs one subtraction.'),'O(n²+roads)','O(n+roads)',5),
}

BATCH[1609]['params'] = [('root','TreeNode','treenode')]
