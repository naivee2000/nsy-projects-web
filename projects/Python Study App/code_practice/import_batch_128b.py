"""Second slice of workbook batch 128: greedy and counting problems."""

from collections import Counter, deque

from .import_batch_055 import entry


def cups_oracle(args):
    start = tuple(sorted(args[0])); queue = deque([(start, 0)]); seen = {start}
    while queue:
        state, steps = queue.popleft()
        if not any(state): return steps
        positive = [i for i, value in enumerate(state) if value]
        choices = [(i,) for i in positive] + [(i, j) for x, i in enumerate(positive) for j in positive[x + 1:]]
        for chosen in choices:
            updated = list(state)
            for index in chosen: updated[index] -= 1
            candidate = tuple(sorted(updated))
            if candidate not in seen: seen.add(candidate); queue.append((candidate, steps + 1))


def random_cups(rng):
    return [[rng.randint(0, 8) for _ in range(3)]]


def pieces_oracle(args):
    start, target = args
    if start.replace('_', '') != target.replace('_', ''): return False
    source = [(char, i) for i, char in enumerate(start) if char != '_']
    destination = [(char, i) for i, char in enumerate(target) if char != '_']
    return all((char == 'L' and old >= new) or (char == 'R' and old <= new)
               for (char, old), (_, new) in zip(source, destination))


def random_pieces(rng):
    n = rng.randint(1, 10)
    return [''.join(rng.choice('_LR') for _ in range(n)), ''.join(rng.choice('_LR') for _ in range(n))]


def swaps_oracle(args):
    (nums,) = args; start = tuple(nums); queue = deque([(start, 0)]); seen = {start}
    low, high = min(nums), max(nums)
    while queue:
        state, distance = queue.popleft()
        if state[0] == low and state[-1] == high: return distance
        for i in range(len(state) - 1):
            candidate = list(state); candidate[i], candidate[i + 1] = candidate[i + 1], candidate[i]
            candidate = tuple(candidate)
            if candidate not in seen: seen.add(candidate); queue.append((candidate, distance + 1))


def random_swaps(rng):
    return [[rng.randint(0, 9) for _ in range(rng.randint(2, 7))]]


def pairs_oracle(args):
    counts = Counter(args[0]); pairs = sum(value // 2 for value in counts.values())
    return [pairs, len(args[0]) - pairs * 2]


def random_pairs(rng):
    return [[rng.randint(0, 8) for _ in range(rng.randint(1, 25))]]


def digit_pair_oracle(args):
    nums = args[0]; best = -1
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if sum(map(int, str(nums[i]))) == sum(map(int, str(nums[j]))): best = max(best, nums[i] + nums[j])
    return best


def random_digit_pair(rng):
    return [[rng.randint(1, 9999) for _ in range(rng.randint(2, 18))]]


CUPS = '''\
def minimum_seconds_to_fill_cups(amount):
    return max(max(amount),(sum(amount)+1)//2)
'''

PIECES = '''\
def can_move_pieces(start,target):
    if start.replace('_','')!=target.replace('_',''):return False
    left=right=0;n=len(start)
    while left<n or right<n:
        while left<n and start[left]=='_':left+=1
        while right<n and target[right]=='_':right+=1
        if left==n or right==n:return left==right
        if start[left]=='L' and left<right:return False
        if start[left]=='R' and left>right:return False
        left+=1;right+=1
    return True
'''

SWAPS = '''\
def minimum_swaps_for_valid_array(nums):
    minimum=nums.index(min(nums))
    maximum=len(nums)-1-nums[::-1].index(max(nums))
    return minimum+(len(nums)-1-maximum)-(minimum>maximum)
'''

PAIRS = '''\
def maximum_pairs_and_leftovers(nums):
    pairs=sum(count//2 for count in __import__('collections').Counter(nums).values())
    return [pairs,len(nums)-2*pairs]
'''

DIGITS = '''\
def maximum_pair_sum_equal_digit_sum(nums):
    largest={};answer=-1
    for number in nums:
        key=sum(map(int,str(number)))
        if key in largest:answer=max(answer,number+largest[key])
        largest[key]=max(number,largest.get(key,0))
    return answer
'''


BATCH = {
2335: entry('minimum_seconds_to_fill_cups',[('amount','list[int]')],'int',['arrays','greedy'],['There are exactly three water types and amount[i] cups still need type i.','Each second fills either one cup or two cups of different types.','Return the minimum seconds needed to fill every requested cup.'],[([[1,4,2]],'Four seconds suffice because the largest type needs four fills and other types can be paired with it.'),([[5,4,4]],'Thirteen cups require at least seven seconds, and balanced pairing achieves seven.')],[[a] for a in [[0,0,0],[1,0,0],[1,1,0],[1,1,1],[2,0,0],[2,2,0],[2,2,2],[10,1,1],[3,5,7],[8,8,1],[0,4,4],[6,2,5],[9,3,3],[1,7,6]]],CUPS,[CUPS.replace('max(max(amount),(sum(amount)+1)//2)','max(amount)'),CUPS.replace('(sum(amount)+1)//2','sum(amount)//2')],['Uses only the largest pile and ignores the total-work lower bound.','Rounds an odd total down even though the final unpaired cup needs another second.'],cups_oracle,random_cups,['Two lower bounds matter: the largest single type and half the total number of cups.','A second handles at most two cups, so round total/2 upward.','Return the larger of max(amount) and ceil(sum(amount)/2).','When one type dominates it determines the time; otherwise repeated cross-type pairing reaches the total-work bound.'],'O(1)','O(1)',3),
2337: entry('can_move_pieces',[('start','str'),('target','str')],'bool',['strings','two pointers'],['L pieces may move left into adjacent blanks but never right.','R pieces may move right into adjacent blanks but never left.','Pieces cannot cross, and underscores denote blank positions.'],[(['_L__R__R_','L______RR'],'After ignoring blanks the order is LRR, and every piece moves only in its allowed direction.'),(['R_L_','__LR'],'The R would have to cross the L, so the target is impossible.')],[[a,b] for a,b in [('_','_'),('L_','L_'),('_L','L_'),('L_','_L'),('R_','_R'),('_R','R_'),('LR','LR'),('RL','LR'),('__L','L__'),('R__','__R'),('_L_R','L__R'),('L_R_','_LR_'),('R_L','_RL'),('__','LR')]],PIECES,[PIECES.replace("start.replace('_','')!=target.replace('_','')","sorted(start)!=sorted(target)"),PIECES.replace("start[left]=='L' and left<right","start[left]=='L' and left>right")],['Checks only piece counts, allowing L and R to cross and reorder.','Reverses the movement restriction for L pieces.'],pieces_oracle,random_pieces,['First remove blanks; the remaining L/R sequence must be identical.','Match pieces in order with two pointers that skip underscores.','For each L require target_index <= start_index; for each R require target_index >= start_index.','Order equality prevents crossings, and the index inequalities are exactly the allowed movements.'],'O(n)','O(1)',5),
2340: entry('minimum_swaps_for_valid_array',[('nums','list[int]')],'int',['arrays','greedy'],['Use adjacent swaps only.','A valid array has a minimum value at index zero and a maximum value at the final index.','When values repeat, choose occurrences minimizing the number of swaps.'],[([[3,4,5,5,3,1]],'Move the last value one leftward five places; the rightmost maximum then needs one fewer net move, totaling six.'),([[9]],'The single value is both minimum and maximum, so no swap is required.')],[[a] for a in [[1,2],[2,1],[1,2,3],[3,2,1],[2,1,2],[3,1,3,1],[5,5],[1,1,2,2],[2,2,1,1],[4,1,3,4],[4,4,1,4],[0,5,2,0,5],[7,3,7,1,7],[2,9,1,9,3]]],SWAPS,[SWAPS.replace("nums.index(min(nums))","len(nums)-1-nums[::-1].index(min(nums))"),SWAPS.replace('-(minimum>maximum)','')],['Moves the rightmost minimum, wasting swaps compared with the leftmost minimum.','Double-counts one crossing swap when the chosen minimum begins right of the chosen maximum.'],swaps_oracle,random_swaps,['Use the leftmost minimum because it is closest to index zero.','Use the rightmost maximum because it is closest to the final index.','Add their distances, subtracting one when the minimum starts after the maximum because their moves cross once.','Any solution must cover both endpoint distances; these occurrence choices minimize them and only the shared crossing can reduce the sum.'],'O(n)','O(1)',5),
2341: entry('maximum_pairs_and_leftovers',[('nums','list[int]')],'list[int]',['arrays','counting'],['A pair contains two equal values and each input occurrence may be used once.','Form as many pairs as possible.','Return [number_of_pairs, number_of_unpaired_elements].'],[([[1,3,2,1,3,2,2]],'There is one pair for each of one, two, and three, leaving one extra two.'),([[1,1]],'The two equal values form one pair with nothing left.')],[[a] for a in [[1],[1,2],[1,1,1],[1,1,2,2],[0,0,0,0],[1,2,3,4],[5,5,5,5,5],[2,3,2,3,2,3],[9,8,9],[1,1,1,1,2],[4,4,5,6,6],[7,7,8,8,9,9],[0,1,0,1,0],[3,3,3,4,4,5]]],PAIRS,[PAIRS.replace('count//2','count%2'),PAIRS.replace('len(nums)-2*pairs','len(nums)-pairs')],['Adds parity values instead of the number of complete pairs.','Subtracts only one element per pair when computing leftovers.'],pairs_oracle,random_pairs,['Count occurrences of each value.','A frequency f contributes floor(f/2) disjoint pairs.','Sum those pairs; every pair consumes two elements, so leftovers equal n-2*pairs.','Pairing within each value is independent and floor(f/2) is maximal, so their sum is globally maximal.'],'O(n)','O(n)',3),
2342: entry('maximum_pair_sum_equal_digit_sum',[('nums','list[int]')],'int',['arrays','hash maps'],['Choose two distinct array positions whose values have equal decimal digit sums.','Return the maximum sum of such a pair, or -1 if no pair exists.','All values are positive integers.'],[([[18,43,36,13,7]],'Eighteen and thirty-six both have digit sum nine and total fifty-four.'),([[10,12,19,14]],'All digit sums differ, so no valid pair exists.')],[[a] for a in [[1,2],[1,10],[99,18],[5,5],[100,1,10],[23,32,41],[999,27,72],[11,20,2],[123,321,222],[8,80,800],[19,91,55],[44,8,26],[7,16,25,34],[1000,100,10,1]]],DIGITS,[DIGITS.replace('number+largest[key]','largest[key]'),DIGITS.replace('max(number,largest.get(key,0))','min(number,largest.get(key,number))')],['Returns only the earlier number rather than the pair sum.','Keeps the smallest value for each digit sum, which can miss the maximum pair.'],digit_pair_oracle,random_digit_pair,['Use decimal digit sum as a hash-map key.','Store the largest value seen for each digit sum.','Before updating a key, combine the current number with its stored largest value and maximize the answer.','For a fixed second endpoint, the largest earlier compatible value always gives its best pair; scanning all endpoints covers every optimum.'],'O(n log(max(nums)))','O(n)',5),
}
