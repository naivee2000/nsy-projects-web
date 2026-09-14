"""Fourth slice of workbook batch 126."""

from collections import deque
from decimal import Decimal

from .import_batch_055 import entry


def discount_oracle(args):
    sentence, discount = args; multiplier = Decimal(100 - discount) / 100
    result = []
    for word in sentence.split(' '):
        if len(word) > 1 and word[0] == '$' and word[1:].isdigit():
            word = '$' + format(Decimal(word[1:]) * multiplier, '.2f')
        result.append(word)
    return ' '.join(result)


def random_discount(rng):
    words = []
    for _ in range(rng.randint(1, 15)):
        kind = rng.randrange(4)
        if kind == 0: words.append('$' + str(rng.randint(0, 10000)))
        elif kind == 1: words.append(str(rng.randint(0, 99)) + '$')
        else: words.append(''.join(rng.choice('abc') for _ in range(rng.randint(1, 6))))
    return [' '.join(words), rng.randint(0, 100)]


def steps_oracle(args):
    values = list(args[0]); steps = 0
    while any(values[index - 1] > values[index] for index in range(1, len(values))):
        remove = {index for index in range(1, len(values)) if values[index - 1] > values[index]}
        values = [value for index, value in enumerate(values) if index not in remove]; steps += 1
    return steps


def random_steps(rng):
    return [[rng.randint(0, 30) for _ in range(rng.randint(1, 25))]]


def obstacles_oracle(args):
    grid = args[0]; rows, columns = len(grid), len(grid[0]); infinity = 10**9
    distance = [[infinity] * columns for _ in range(rows)]; distance[0][0] = 0
    for _ in range(rows * columns):
        changed = False
        for row in range(rows):
            for column in range(columns):
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=row+dr,column+dc
                    if 0<=nr<rows and 0<=nc<columns and distance[nr][nc] > distance[row][column] + grid[nr][nc]:
                        distance[nr][nc] = distance[row][column] + grid[nr][nc]; changed = True
        if not changed: break
    return distance[-1][-1]


def random_obstacles(rng):
    rows, columns = rng.randint(2, 7), rng.randint(2, 7)
    grid = [[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]; grid[0][0] = grid[-1][-1] = 0
    return [grid]


def stocks_oracle(args):
    present, future, budget = args; best = 0
    for mask in range(1 << len(present)):
        cost = sum(present[index] for index in range(len(present)) if mask >> index & 1)
        if cost <= budget:
            best = max(best, sum(max(0, future[index] - present[index]) for index in range(len(present)) if mask >> index & 1))
    return best


def random_stocks(rng):
    n = rng.randint(1, 11); present = [rng.randint(1, 20) for _ in range(n)]
    return [present, [rng.randint(1, 30) for _ in range(n)], rng.randint(0, 40)]


def game_oracle(args):
    values = list(args[0])
    while len(values) > 1:
        values = [min(values[2*i],values[2*i+1]) if i%2==0 else max(values[2*i],values[2*i+1]) for i in range(len(values)//2)]
    return values[0]


def random_game(rng):
    size = 2 ** rng.randint(0, 5)
    return [[rng.randint(0, 100) for _ in range(size)]]


DISCOUNT = '''\
def apply_sentence_price_discount(sentence,discount):
    result=[]
    for word in sentence.split(' '):
        if len(word)>1 and word[0]=='$' and word[1:].isdigit():
            cents=int(word[1:])*(100-discount)
            word=f'${cents//100}.{cents%100:02d}'
        result.append(word)
    return ' '.join(result)
'''

STEPS = '''\
def steps_until_non_decreasing(nums):
    stack=[];answer=0
    for value in nums:
        steps=0
        while stack and value>=stack[-1][0]:steps=max(steps,stack.pop()[1])
        steps=steps+1 if stack else 0
        answer=max(answer,steps);stack.append((value,steps))
    return answer
'''

OBSTACLES = '''\
def minimum_removed_obstacles(grid):
    from collections import deque
    rows,columns=len(grid),len(grid[0]);distance=[[10**9]*columns for _ in range(rows)];distance[0][0]=0;queue=deque([(0,0)])
    while queue:
        row,column=queue.popleft()
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns:
                candidate=distance[row][column]+grid[nr][nc]
                if candidate<distance[nr][nc]:
                    distance[nr][nc]=candidate
                    if grid[nr][nc]:queue.append((nr,nc))
                    else:queue.appendleft((nr,nc))
    return distance[-1][-1]
'''

STOCKS = '''\
def maximum_stock_budget_profit(present,future,budget):
    dp=[0]*(budget+1)
    for cost,sale in zip(present,future):
        profit=sale-cost
        if profit<=0:continue
        for money in range(budget,cost-1,-1):dp[money]=max(dp[money],dp[money-cost]+profit)
    return dp[budget]
'''

GAME = '''\
def min_max_reduction_game(nums):
    values=list(nums)
    while len(values)>1:
        values=[min(values[2*index],values[2*index+1]) if index%2==0 else max(values[2*index],values[2*index+1]) for index in range(len(values)//2)]
    return values[0]
'''


BATCH = {
    2288: entry('apply_sentence_price_discount',[('sentence','str'),('discount','int')],'str',['strings','parsing'],['Words are separated by one space.','A price word is exactly a dollar sign followed by one or more digits; tokens like 5$ or $1a are unchanged.','Apply the integer percent discount and format every recognized result with exactly two decimal places.'],[(['there are $1 $2 and 5$ candies in the shop',50],'Only $1 and $2 are price words, becoming $0.50 and $1.00.'),(['$100 $0 $7x',25],'The valid prices become $75.00 and $0.00, while $7x is unchanged.')],[[s,d] for s,d in [('there are $1 $2 and 5$ candies in the shop',50),('$100 $0 $7x',25),('$1',0),('$1',100),('hello world',30),('5$ $5',20),('$10 $20',33),('$001',50),('$9999',1),('$1a a$1',10),('$0',75),('buy $25 now',12),('$3 and $3',67),('$123456',99)]],DISCOUNT,[DISCOUNT.replace("word[1:].isdigit()","word[1:].isalnum()"),DISCOUNT.replace("cents%100:02d","cents%100")],['Treats alphanumeric suffixes as numeric prices and attempts invalid conversion.','Fails to pad the fractional cents field to exactly two digits.'],discount_oracle,random_discount,['Parse the sentence token by token so punctuation remains part of a non-price word.','For a valid price, discounted cents equal integer_price*(100-discount), avoiding floating error.','Format cents//100 as dollars and cents%100 with two digits, then rejoin by spaces.','The recognition predicate matches the contract exactly and integer arithmetic represents the exact two-decimal result.'],'O(sentence length)','O(sentence length)',5),
    2289: entry('steps_until_non_decreasing',[('nums','list[int]')],'int',['arrays','monotonic stacks','dynamic programming'],['In one step, simultaneously remove every element smaller than its immediate left neighbor at the start of that step.','Repeat until the remaining array is non-decreasing.','Return the number of simultaneous removal rounds.'],[([[5,3,4,4,7,3,6,11,8,5,11]],'Successive simultaneous deletions stabilize after three rounds.'),([[4,5,7,7,13]],'The array is already non-decreasing, so zero rounds are needed.')],[[x] for x in [[1],[1,2],[2,1],[5,3,4,4,7,3,6,11,8,5,11],[4,5,7,7,13],[5,4,3,2,1],[1,3,2,4],[10,1,2,3,4],[3,3,2],[1,2,3,0],[7,6,8,5,9],[2,1,1,1],[9,1,8,2,7,3],[1,5,2,3,4]]],STEPS,[STEPS.replace('steps+1 if stack else 0','steps if stack else 0'),STEPS.replace('value>=stack[-1][0]','value>stack[-1][0]')],['Does not add the current removal round after surviving blockers.','Fails to pop equal values even though they do not remove one another and should merge their state.'],steps_oracle,random_steps,['The stack stores surviving blockers with the round when each dependent value disappears.','Pop values no greater than current while taking their maximum delay; if a larger blocker remains, current disappears one round later.','Push (value,steps) and track the maximum steps over all values.','Popped elements cannot block current after their own removal; the nearest surviving greater element determines exactly one later deletion round.'],'O(n)','O(n)',7),
    2290: entry('minimum_removed_obstacles',[('grid','list[list[int]]')],'int',['matrices','graphs','0-1 BFS'],['Zero cells are free and one cells are removable obstacles; start and destination are zero.','Move in four cardinal directions and pay one when entering an obstacle cell.','Return the minimum number of obstacles removed along any route.'],[([[[0,1,1],[1,1,0],[1,1,0]]],'A least-cost route enters two obstacle cells before reaching the corner.'),([[[0,1,0],[0,1,0],[0,0,0]]],'A path of zero cells reaches the destination without removing an obstacle.')],[[g] for g in [[[0,0],[0,0]],[[0,1],[1,0]],[[0,1,1],[1,1,0],[1,1,0]],[[0,1,0],[0,1,0],[0,0,0]],[[0,1,1,1,0]],[[0],[1],[1],[0]],[[0,1,0],[1,1,1],[0,1,0]],[[0,0,1],[1,0,1],[1,0,0]],[[0,1,1],[0,1,1],[0,0,0]],[[0,0,0],[1,1,0],[0,0,0]],[[0,1],[0,0],[1,0]],[[0,1,0,1],[1,1,0,1],[0,0,0,0]],[[0,0,1,1],[1,0,1,0],[1,0,0,0]],[[0,1,1,0],[0,1,0,0]]]],OBSTACLES,[OBSTACLES.replace('distance[row][column]+grid[nr][nc]','distance[row][column]+grid[row][column]'),OBSTACLES.replace('queue.appendleft','queue.append')],['Charges the cell being left instead of the obstacle cell being entered.','Uses an ordinary queue for all edges and can finalize expensive routes before free ones.'],obstacles_oracle,random_obstacles,['This is shortest path with edge weights zero or one based on the entered cell.','A deque processes zero-cost relaxations at the front and one-cost relaxations at the back.','Relax four neighbors; appendleft for zero and append for one until no distance improves.','0-1 BFS maintains nondecreasing tentative cost like Dijkstra specialized to binary weights, so the destination distance is minimal.'],'O(rows*columns)','O(rows*columns)',8),
    2291: entry('maximum_stock_budget_profit',[('present','list[int]'),('future','list[int]'),('budget','int')],'int',['arrays','0/1 knapsack','dynamic programming'],['Each stock may be bought at most once at its present price, and any number of distinct stocks may be selected.','Total purchase cost cannot exceed budget; unspent money is allowed.','Profit for a selected stock is future[i]-present[i], and loss-making stocks may be skipped.'],[([[5,4,6,2,3],[8,5,4,3,5],10],'Buying stocks costing five, two, and three uses the budget and earns 3+1+2=6.'),([[4,2,6],[3,5,8],3],'Only the cost-two stock is affordable and profitable, earning three.')],[[p,f,b] for p,f,b in [([5,4,6,2,3],[8,5,4,3,5],10),([4,2,6],[3,5,8],3),([1],[2],0),([1],[2],1),([5],[1],10),([2,3],[5,7],5),([2,2],[4,4],2),([10,1,1],[20,3,3],2),([3,4,5],[3,4,5],12),([1,2,3],[10,2,9],4),([6,5,4],[7,20,5],5),([2,7,3],[5,10,8],7),([8,1,9,2],[20,2,30,6],10),([4,4,4],[8,9,10],8)]],STOCKS,[STOCKS.replace('range(budget,cost-1,-1)','range(cost,budget+1)'),STOCKS.replace('profit<=0','profit>=0')],['Updates budget from low to high and can buy the same stock repeatedly.','Skips profitable stocks and considers only nonpositive gains.'],stocks_oracle,random_stocks,['This is 0/1 knapsack with present price as weight and positive future-minus-present as value.','Process each stock once and update budgets in descending order to prevent reusing it.','For money from budget down to cost, maximize dp[money] with dp[money-cost]+profit.','Descending updates preserve the previous-stock layer, so every feasible subset is represented once and the maximum profit is retained.'],'O(stocks*budget)','O(budget)',6),
    2293: entry('min_max_reduction_game',[('nums','list[int]')],'int',['arrays','simulation'],['The nonempty array length is a power of two.','In each round, output index i uses min of input positions 2i and 2i+1 when i is even, otherwise max.','Repeat on the new half-length array until one value remains.'],[([[1,3,5,2,4,8,2,2]],'The rounds produce [1,5,4,2], then [1,4], then 1.'),([[3]],'A one-element array is already the final game result.')],[[x] for x in [[3],[1,2],[2,1],[1,3,5,2,4,8,2,2],[0,1,2,3],[3,2,1,0],[5,5,5,5],[9,1,8,2,7,3,6,4],[1,9,2,8],[10,20,30,40,50,60,70,80],[0,0],[100,1],[4,7,2,9,1,8,3,6],[8,7,6,5]]],GAME,[GAME.replace('index%2==0','index%2==1'),GAME.replace('len(values)//2','len(values)//2-1')],['Reverses which result indices take minimum and maximum.','Produces one too few values per round and may discard the final pair.'],game_oracle,random_game,['Simulate each round because every output depends only on one disjoint input pair.','Build a half-length list, alternating min and max according to the new index parity.','Replace values with that list until its length is one.','Each round exactly matches the defined pair transformation, and power-of-two length guarantees repeated halving reaches one.'],'O(n)','O(n)',3),
}

BATCH[2291]['statement'] = 'Choose any subset of distinct stocks to buy now within the budget and sell later; return the maximum total profit.'
BATCH[2288]['wrong'][0] = '''\
def apply_sentence_price_discount(sentence,discount):
    result=[]
    for word in sentence.split(' '):
        if len(word)>1 and word[-1]=='$' and word[:-1].isdigit():
            cents=int(word[:-1])*(100-discount);word=f'${cents//100}.{cents%100:02d}'
        result.append(word)
    return ' '.join(result)
'''
BATCH[2288]['wrong_reasons'][0] = 'Looks for a trailing dollar sign instead of the required leading dollar sign.'
BATCH[2290]['wrong'][1] = '''\
def minimum_removed_obstacles(grid):
    return sum(grid[0][1:])+sum(row[-1] for row in grid[1:])
'''
BATCH[2290]['wrong_reasons'][1] = 'Checks only the fixed top-row then right-column route rather than finding the least-cost path.'
BATCH[2290]['wrong'][0] = OBSTACLES.replace('distance[row][column]+grid[nr][nc]', 'distance[row][column]+2*grid[nr][nc]')
BATCH[2290]['wrong_reasons'][0] = 'Charges two removals for every obstacle cell instead of one.'
BATCH[2293]['wrong'][1] = '''\
def min_max_reduction_game(nums):
    return min(nums)
'''
BATCH[2293]['wrong_reasons'][1] = 'Assumes the global minimum always survives, ignoring maximum rounds that can discard it.'
BATCH[2293]['boundaries'].append([[5,6,1,9]])
