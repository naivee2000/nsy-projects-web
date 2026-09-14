"""Second slice of workbook batch 127."""

from fractions import Fraction
from itertools import product

from .import_batch_055 import entry


def replacement_oracle(args):
    text, pattern, mappings = args; choices = {}
    for char in set(pattern): choices[char] = {char}
    for old, new in mappings:
        if old in choices: choices[old].add(new)
    return any(''.join(candidate) in text for candidate in product(*(choices[char] for char in pattern)))


def random_replacement(rng):
    alphabet = 'abc123'; text = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 15)))
    pattern = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, min(5, len(text)))))
    pairs = list(product(alphabet, repeat=2)); rng.shuffle(pairs)
    return [text, pattern, [list(pair) for pair in pairs[:rng.randint(0, 8)]]]


def score_oracle(args):
    nums, limit = args
    return sum(sum(nums[left:right]) * (right - left) < limit
               for left in range(len(nums)) for right in range(left + 1, len(nums) + 1))


def random_score(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 25))], rng.randint(1, 500)]


def tax_oracle(args):
    brackets, income = args; previous = 0; result = Fraction(0)
    for upper, percent in brackets:
        taxed = max(0, min(income, upper) - previous)
        result += Fraction(taxed * percent, 100); previous = upper
        if income <= upper: break
    return float(result)


def random_tax(rng):
    bounds = sorted(rng.sample(range(1, 30), rng.randint(1, 8)))
    return [[[bound, rng.randint(0, 100)] for bound in bounds], rng.randint(0, bounds[-1])]


def path_oracle(args):
    grid, move_cost = args; rows, columns = len(grid), len(grid[0]); best = 10**18
    for route in product(range(columns), repeat=rows):
        cost = sum(grid[row][route[row]] for row in range(rows))
        cost += sum(move_cost[grid[row][route[row]]][route[row + 1]] for row in range(rows - 1))
        best = min(best, cost)
    return best


def random_path(rng):
    rows, columns = rng.randint(2, 5), rng.randint(1, 4); values = list(range(rows * columns)); rng.shuffle(values)
    grid = [values[row * columns:(row + 1) * columns] for row in range(rows)]
    return [grid, [[rng.randint(0, 20) for _ in range(columns)] for _ in values]]


def cookies_oracle(args):
    cookies, children = args; best = sum(cookies)
    for assignment in product(range(children), repeat=len(cookies)):
        totals = [0] * children
        for bag, child in zip(cookies, assignment): totals[child] += bag
        best = min(best, max(totals))
    return best


def random_cookies(rng):
    n = rng.randint(1, 7)
    return [[rng.randint(1, 20) for _ in range(n)], rng.randint(1, min(n, 3))]


REPLACEMENT = '''\
def substring_matches_replacements(s,sub,mappings):
    allowed={(old,new) for old,new in mappings}
    for start in range(len(s)-len(sub)+1):
        if all(source==target or (source,target) in allowed for source,target in zip(sub,s[start:start+len(sub)])):return True
    return False
'''

SCORE = '''\
def count_subarrays_below_score(nums,k):
    left=total=answer=0
    for right,value in enumerate(nums):
        total+=value
        while left<=right and total*(right-left+1)>=k:total-=nums[left];left+=1
        answer+=right-left+1
    return answer
'''

TAX = '''\
def progressive_tax_amount(brackets,income):
    previous=0;tax=0.0
    for upper,percent in brackets:
        taxed=max(0,min(income,upper)-previous);tax+=taxed*percent/100;previous=upper
        if income<=upper:break
    return tax
'''

PATH = '''\
def minimum_grid_move_path_cost(grid,move_cost):
    costs=list(grid[0])
    for row in range(1,len(grid)):
        updated=[]
        for column,value in enumerate(grid[row]):
            updated.append(value+min(costs[previous]+move_cost[grid[row-1][previous]][column] for previous in range(len(grid[0]))))
        costs=updated
    return min(costs)
'''

COOKIES = '''\
def minimum_cookie_unfairness(cookies,k):
    cookies=sorted(cookies,reverse=True);loads=[0]*k;answer=sum(cookies)
    def assign(index):
        nonlocal answer
        if max(loads)>=answer:return
        if index==len(cookies):answer=min(answer,max(loads));return
        seen=set()
        for child in range(k):
            if loads[child] in seen:continue
            seen.add(loads[child]);loads[child]+=cookies[index];assign(index+1);loads[child]-=cookies[index]
            if loads[child]==0:break
    assign(0)
    return answer
'''


BATCH = {
    2301: entry('substring_matches_replacements',[('s','str'),('sub','str'),('mappings','list[list[str]]')],'bool',['strings','hash sets','string matching'],['Each mapping [old,new] permits one occurrence of old in sub to become new; unchanged characters are always allowed.','Each pattern position may be replaced at most once and mappings are directional.','Return whether some transformed sub equals a contiguous substring of s.'],[(['fool3e7bar','leet',[['e','3'],['t','7'],['t','8']]],'Replacing e with 3 and t with 7 makes l3e7, which occurs in the source.'),(['fooleetbar','f00l',[['o','0']]],'Mappings allow o to become zero, not zero to become o, so the pattern cannot match.')],[[s,p,m] for s,p,m in [('a','a',[]),('a','b',[['b','a']]),('fool3e7bar','leet',[['e','3'],['t','7'],['t','8']]),('fooleetbar','f00l',[['o','0']]),('abc','abc',[]),('abc','xyz',[['x','a'],['y','b'],['z','c']]),('aaaa','bb',[['b','a']]),('123abc','a2c',[['2','b']]),('hello','jello',[['j','h']]),('abcd','bc',[['b','x']]),('x9y','xay',[['a','9']]),('abab','aa',[['a','b']]),('code123','ode',[['o','0']]),('zzz','abc',[['a','z'],['b','z'],['c','z']])]],REPLACEMENT,[REPLACEMENT.replace('(source,target) in allowed','(target,source) in allowed'),REPLACEMENT.replace('source==target or ','')],['Reverses every directional replacement pair.','Requires every position to use a mapping and disallows unchanged matching characters.'],replacement_oracle,random_replacement,['Store allowed directional character pairs in a set.','For each possible source-window start, compare corresponding characters independently.','A position matches when characters are equal or (sub_char,source_char) is allowed; accept when all positions match.','Every valid transformation acts independently at each position, so the window predicate is necessary and sufficient, and all windows are tested.'],'O((len(s)-len(sub)+1)*len(sub))','O(mappings)',8),
    2302: entry('count_subarrays_below_score',[('nums','list[int]'),('k','int')],'int',['arrays','sliding windows'],['All nums values are positive.','A nonempty contiguous subarray has score sum(subarray)*length(subarray).','Count subarrays whose score is strictly less than k.'],[([[2,1,4,3,5],10],'Six subarrays have sum times length below ten.'),([[1,1,1],5],'All three singletons and both length-two subarrays qualify, giving five.')],[[n,k] for n,k in [([1],1),([1],2),([2,1,4,3,5],10),([1,1,1],5),([5,5],20),([1,2,3],100),([10],10),([10],11),([2,2,2,2],9),([1,10,1],12),([3,1,2,1],8),([100,1],50),([4,4,1,1],15),([1,2,1,2,1],7)]],SCORE,[SCORE.replace('>=k','>k'),SCORE.replace('answer+=right-left+1','answer+=right-left')],['Treats a score equal to k as valid despite the strict inequality.','Omits one valid subarray ending at every right boundary.'],score_oracle,random_score,['Positive values make the window score decrease whenever its left endpoint advances.','For each right endpoint, shrink from the left until sum*length is below k.','Then every subarray ending at right and starting from left through right is valid, adding right-left+1.','Monotonic positivity makes the valid starts a contiguous suffix, so the window counts each qualifying subarray once.'],'O(n)','O(1)',8),
    2303: entry('progressive_tax_amount',[('brackets','list[list[int]]'),('income','int')],'float',['arrays','simulation'],['Brackets have increasing upper bounds and rates are integer percentages.','Only income above the previous upper bound and up to the current upper bound is taxed at that bracket rate.','Return the total tax as a numeric value; zero income produces zero tax.'],[([[[3,50],[7,10],[12,25]],10],'The first three dollars contribute 1.50, the next four 0.40, and the final three 0.75, totaling 2.65.'),([[[1,0],[4,25]],4],'The first dollar is untaxed and the next three contribute 0.75.')],[[b,i] for b,i in [([[3,50],[7,10],[12,25]],10),([[1,0],[4,25]],4),([[5,10]],0),([[5,10]],5),([[2,100]],1),([[2,50],[5,50]],5),([[3,0],[6,100]],4),([[1,25],[2,25],[3,25]],3),([[10,7]],9),([[2,10],[4,20],[8,30]],7),([[5,99]],1),([[1,100],[10,0]],10),([[4,12],[9,34]],6),([[2,5],[3,10],[20,15]],12)]],TAX,[TAX.replace('previous=upper','previous=0'),TAX.replace('/100','//100')],['Resets the lower bracket boundary and taxes earlier income repeatedly.','Uses integer division within each bracket and discards fractional tax.'],tax_oracle,random_tax,['Walk brackets in increasing upper-bound order while remembering the prior bound.','Tax max(0,min(income,upper)-previous) dollars at percent/100.','Accumulate each contribution and stop after the bracket containing income.','The bracket slices are disjoint and cover exactly the taxable income, so their rate-weighted sum is the required amount.'],'O(brackets)','O(1)',5),
    2304: entry('minimum_grid_move_path_cost',[('grid','list[list[int]]'),('move_cost','list[list[int]]')],'int',['matrices','dynamic programming'],['Start in any first-row cell and choose one cell in each following row.','Moving from a cell with value v to next-row column c costs move_cost[v][c].','Total cost includes every visited cell value plus every inter-row move cost.'],[([[[5,3],[4,0],[2,1]],[[9,8],[1,5],[10,12],[18,6],[2,4],[14,3]]],'The cheapest complete top-to-bottom path costs seventeen.'),([[[0,1],[2,3]],[[0,0],[0,0],[0,0],[0,0]]],'With free moves, choosing values zero then two costs two.')],[[g,m] for g,m in [([[0],[1]],[[0],[0]]),([[5,3],[4,0],[2,1]],[[9,8],[1,5],[10,12],[18,6],[2,4],[14,3]]),([[0,1],[2,3]],[[0,0],[0,0],[0,0],[0,0]]),([[0,1],[2,3]],[[5,1],[2,4],[3,3],[0,0]]),([[0,1,2],[3,4,5]],[[0,1,2],[2,1,0],[3,3,3],[1,1,1],[2,2,2],[4,4,4]]),([[2,0],[3,1]],[[1,5],[5,1],[2,2],[3,3]]),([[0],[1],[2]],[[4],[5],[6]]),([[3,2],[1,0]],[[1,2],[3,4],[5,6],[7,8]]),([[0,2],[3,1],[4,5]],[[1,1],[2,2],[3,3],[4,4],[5,5],[6,6]]),([[1,0],[3,2]],[[9,0],[0,9],[5,5],[1,1]]),([[0,1,2],[5,4,3]],[[1,2,3],[3,2,1],[2,2,2],[0,1,2],[2,1,0],[3,3,3]]),([[4],[0]],[[1],[2],[3],[4],[5]]),([[1,3],[2,0],[5,4]],[[2,5],[1,4],[3,0],[0,3],[4,1],[5,2]]),([[2,1],[0,3]],[[0,5],[5,0],[1,1],[2,2]])]],PATH,[PATH.replace('costs[previous]+move_cost','move_cost'),PATH.replace('value+min','min')],['Omits the accumulated cost of all earlier rows.','Omits the value of each newly visited cell.'],path_oracle,random_path,['Dynamic programming needs only the cheapest cost ending at each column of the current row.','To enter next cell value at column c, try every previous column and add its path cost plus move_cost[previous_value][c].','Add the new cell value to the best transition, repeat rows, and return the minimum final cost.','Every path has one predecessor in the prior row; minimizing all such transitions preserves the cheapest path to each state.'],'O(rows*columns^2)','O(columns)',6),
    2305: entry('minimum_cookie_unfairness',[('cookies','list[int]'),('k','int')],'int',['arrays','backtracking','branch and bound'],['Each bag is indivisible and must be assigned to exactly one of k children.','A child may receive no bag; unfairness is the maximum total assigned to any child.','Return the minimum possible unfairness.'],[([[8,15,10,20,8],2],'An optimal partition has child totals thirty-one and thirty, so unfairness is thirty-one.'),([[6,1,3,2,2,4,1,2],3],'The bags can be divided so the maximum child load is seven.')],[[c,k] for c,k in [([1],1),([1,2],2),([8,15,10,20,8],2),([6,1,3,2,2,4,1,2],3),([5,5,5],2),([1,2,3],1),([1,2,3],3),([10,1,1,1],2),([4,3,2,1],2),([9,8,7],2),([2,2,2,2],3),([7,3,5,1],3),([20,10,5,5],2),([1,1,1,1,1],4)]],COOKIES,[COOKIES.replace('max(loads)>=answer','sum(loads)>=answer'),COOKIES.replace('if loads[child]==0:break','')],['Prunes when total assigned load reaches the current bound, even though unfairness depends only on the maximum.','Explores symmetric empty-child assignments without stopping, causing exponential duplicate branches.'],cookies_oracle,random_cookies,['Assign larger bags first so bad branches exceed the current bound early.','Backtrack over child loads, pruning when the current maximum cannot beat the best and skipping equal load states.','Try the next bag on each distinct load; undo it, and after the first empty child stop trying other empty children.','Every distinct assignment-load state is explored unless its current maximum already proves it cannot improve the incumbent.'],'O(k^n) worst case','O(k+n)',7),
}

BATCH[2303]['comparator'] = 'float'
BATCH[2305]['wrong'][1] = '''\
def minimum_cookie_unfairness(cookies,k):
    loads=[0]*k
    for bag in sorted(cookies,reverse=True):
        child=loads.index(min(loads))
        loads[child]+=bag
    return max(loads)
'''
BATCH[2305]['wrong_reasons'][1] = 'Greedily assigns each next bag to the lightest child, which can miss a globally better partition.'
