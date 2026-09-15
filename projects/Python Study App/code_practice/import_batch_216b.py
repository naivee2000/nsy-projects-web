"""Stride energy, grid differences, cyclic permutations, parity ranges, and digit pairs."""
from itertools import permutations

from .import_batch_055 import entry


def energy_oracle(args):
    energy, step = args
    return max(sum(energy[index::step]) for index in range(len(energy)))


def random_energy(rng):
    size = rng.randint(1, 16)
    return [[rng.randint(-15, 15) for _ in range(size)], rng.randint(1, size)]


def grid_oracle(args):
    grid = args[0]; rows = len(grid); columns = len(grid[0]); best = -10**30
    for r1 in range(rows):
        for c1 in range(columns):
            for r2 in range(r1, rows):
                for c2 in range(c1, columns):
                    if r1 != r2 or c1 != c2:best = max(best, grid[r2][c2] - grid[r1][c1])
    return best


def random_grid(rng):
    rows = rng.randint(1, 5); columns = rng.randint(1, 5)
    if rows * columns == 1:columns = 2
    return [[[rng.randint(1, 30) for _ in range(columns)] for _ in range(rows)]]


def permutation_score(nums, perm):
    return sum(abs(perm[index] - nums[perm[(index + 1) % len(perm)]]) for index in range(len(perm)))


def permutation_oracle(args):
    nums = args[0]; best = None; score = 10**30
    for tail in permutations(range(1, len(nums))):
        candidate = (0,) + tail; value = permutation_score(nums, candidate)
        if value < score:score = value; best = candidate
    return list(best)


def random_permutation(rng):
    nums = list(range(rng.randint(2, 7))); rng.shuffle(nums); return [nums]


def special_oracle(args):
    nums, queries = args
    return [all((nums[index] ^ nums[index+1]) & 1 for index in range(left, right)) for left, right in queries]


def random_special(rng):
    nums = [rng.randint(0, 30) for _ in range(rng.randint(1, 16))]; queries = []
    for _ in range(rng.randint(1, 10)):
        left = rng.randrange(len(nums)); queries.append([left, rng.randint(left, len(nums)-1)])
    return [nums, queries]


def digits_oracle(args):
    nums = [str(value) for value in args[0]]; answer = 0
    for left in range(len(nums)):
        for right in range(left + 1, len(nums)):
            answer += sum(a != b for a, b in zip(nums[left], nums[right]))
    return answer


def random_digits(rng):
    width = rng.randint(1, 5); low = 1 if width == 1 else 10 ** (width - 1); high = 10 ** width - 1
    return [[rng.randint(low, high) for _ in range(rng.randint(2, 14))]]


ENERGY = '''def maximum_teleport_energy(energy,k):
    best=[0]*len(energy);answer=-10**30
    for index in range(len(energy)-1,-1,-1):
        best[index]=energy[index]+(best[index+k] if index+k<len(energy) else 0)
        answer=max(answer,best[index])
    return answer
'''


GRID = '''def maximum_grid_difference_score(grid):
    rows=len(grid);columns=len(grid[0]);minimum=[[10**30]*columns for _ in range(rows)];answer=-10**30
    for row in range(rows):
        for column in range(columns):
            prior=min(minimum[row-1][column] if row else 10**30,minimum[row][column-1] if column else 10**30)
            if prior<10**30:answer=max(answer,grid[row][column]-prior)
            minimum[row][column]=min(grid[row][column],prior)
    return answer
'''


PERMUTATION = '''def minimum_cost_array_permutation(nums):
    from functools import lru_cache
    n=len(nums);full=(1<<n)-1
    @lru_cache(None)
    def cost(mask,last):
        if mask==full:return abs(last-nums[0])
        return min(abs(last-nums[nxt])+cost(mask|1<<nxt,nxt) for nxt in range(1,n) if not mask>>nxt&1)
    mask=1;last=0;answer=[0]
    while mask!=full:
        target=cost(mask,last)
        for nxt in range(1,n):
            if not mask>>nxt&1 and abs(last-nums[nxt])+cost(mask|1<<nxt,nxt)==target:
                answer.append(nxt);mask|=1<<nxt;last=nxt;break
    return answer
'''


SPECIAL = '''def special_parity_subarrays(nums,queries):
    bad=[0]*len(nums)
    for index in range(1,len(nums)):bad[index]=bad[index-1]+((nums[index]&1)==(nums[index-1]&1))
    return [bad[right]==bad[left] for left,right in queries]
'''


DIGITS = '''def sum_pair_digit_differences(nums):
    texts=[str(value) for value in nums];answer=0
    for position in range(len(texts[0])):
        counts={}
        for index,text in enumerate(texts):
            digit=text[position];answer+=index-counts.get(digit,0);counts[digit]=counts.get(digit,0)+1
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3147: entry('maximum_teleport_energy',[('energy','list[int]'),('k','int')],'int',['dynamic programming','arrays'],['energy is nonempty and may contain positive or negative integers.','Choose any starting index, collect its value, then repeatedly jump exactly k positions right until leaving the array.','Return the maximum total energy over all starting positions.'],[([[-2,-3,-1],2],'Starting at index two collects -1 and stops, which is better than every other route.'),([[5,2,-10,-5,1],3],'Starting at index one collects 2 then 1, for the maximum total of three.')],[[a,k] for a,k in [([5],1),([-7],1),([-2,-3,-1],2),([5,2,-10,-5,1],3),([1,2,3],1),([-5,10,-2,7],2),([4,-10,4,-10,4],2),([9,-1,-1],3),([-1,-2,-3,-4],1),([3,0,3,0],2),([8,-20,7,6,-1],4),([1,-1,1,-1,1,-1],3),([10,-9,-8,10],3),([2,4,-20,8,16],2)]],ENERGY,[ENERGY.replace('answer=max(answer,best[index])','answer=best[index]'),ENERGY.replace('energy[index]+','max(0,energy[index])+')],['Returns only the route beginning at index zero after the reverse scan finishes.','Illegally skips negative energy at visited magicians.'],energy_oracle,random_energy,lesson('Routes from indices with the same remainder modulo k form chains, and each route total is a suffix sum of one chain.','Scan right to left and add the already-computed route total k positions ahead.','dp[i]=energy[i]+dp[i+k] when in bounds; return max(dp).','The forced next jump gives the recurrence exactly, and considering every starting index considers every legal route.'),'O(n)','O(n)',5),
3148: entry('maximum_grid_difference_score',[('grid','list[list[int]]')],'int',['dynamic programming','matrices','prefix minima'],['grid is rectangular, positive-valued, and contains at least two cells.','From a cell, a move may go any positive distance down in the same column or right in the same row; make at least one move.','The scores telescope, so maximize final value minus starting value over reachable distinct cells.'],[([[[9,5,7,3],[8,9,6,1],[6,7,14,3],[2,5,3,1]]],'Start at 5, move down to 7, then right to 14; the scores telescope to nine.'),([[[10,8,6]]],'Every move decreases the value; moving from 10 to 8 gives the maximum score -2.')],[[g] for g in [[[1,2]],[[2],[1]],[[10,8,6]],[[9,5,7],[3,8,12]],[[1,2],[3,4]],[[4,3],[2,1]],[[5,1,9]],[[8],[2],[10]],[[7,7],[7,7]],[[9,1,2],[8,3,20]],[[100,2],[3,4]],[[6,5,4],[3,2,1]],[[1,100,1],[2,3,4]],[[12,4,8],[9,2,11],[3,10,7]]]],GRID,[GRID.replace('minimum[row][column]=min(grid[row][column],prior)','minimum[row][column]=grid[row][column]'),GRID.replace('answer=max(answer,grid[row][column]-prior)','answer=max(answer,abs(grid[row][column]-prior))')],['Forgets smaller values from earlier reachable cells, considering only immediate predecessors.','Uses absolute difference and therefore rewards moving from a larger value to a smaller one.'],grid_oracle,random_grid,lesson('Any move sequence score telescopes to destination value minus start value; a valid start for (r,c) lies anywhere above or left.','Maintain the minimum value in the inclusive upper-left reachable region, but score before adding the current cell to enforce at least one move.','prior=min(prefix above,prefix left); answer=max(answer,cell-prior); prefix=min(cell,prior).','The prefix recurrence contains exactly all possible starts that can reach the current cell, so subtracting its minimum maximizes this destination’s score.'),'O(rows*columns)','O(rows*columns)',5),
3149: entry('minimum_cost_array_permutation',[('nums','list[int]')],'list[int]',['bitmask dynamic programming','permutations'],['nums is a permutation of 0 through n-1 and n is at least two.','For permutation perm, score is sum of abs(perm[i]-nums[perm[(i+1) mod n]]) over all cyclic adjacent positions.','Return the lexicographically smallest permutation attaining the minimum score.'],[([[1,0,2]],'The normalized order [0,1,2] has score two and is the lexicographically smallest minimum-cost permutation.'),([[0,2,1]],'Among cyclic orders beginning with zero, [0,2,1] has the minimum score and is lexicographically first.')],[[p] for p in [[1,0],[0,1],[0,2,1],[2,0,1],[1,2,0],[3,0,2,1],[1,3,0,2],[4,0,3,1,2],[2,4,1,0,3],[5,1,4,0,3,2],[3,2,1,0],[0,1,2,3,4],[6,2,5,1,4,0,3],[2,0,4,1,3]]],PERMUTATION,[PERMUTATION.replace('abs(last-nums[0])','0'),PERMUTATION.replace('for nxt in range(1,n):','for nxt in range(n-1,0,-1):')],['Omits the closing cyclic edge from the final element back to the first.','Reconstructs in descending order and therefore returns a non-lexicographic optimum on ties.'],permutation_oracle,random_permutation,lesson('Rotating a cyclic permutation does not change its score, so every optimum has a unique rotation beginning with zero.','Use subset DP keyed by visited mask and last value, then greedily choose the smallest next value that preserves optimal cost.','cost(mask,last)=min edge(last,next)+cost(mask+next,next); base adds closing edge to zero; reconstruct ascending.','The recurrence enumerates every normalized cyclic order, and ascending optimal reconstruction supplies the lexicographically smallest minimizer.'),'O(n^2*2^n)','O(n*2^n)',8),
3152: entry('special_parity_subarrays',[('nums','list[int]'),('queries','list[list[int]]')],'list[bool]',['prefix sums','arrays'],['nums is nonempty; every query is an inclusive pair [left,right] within the array.','A subarray is special when every adjacent pair in it has opposite parity.','Return one boolean per query in the given order.'],[([[3,4,1,2,6],[[0,4]]],'The final adjacent values 2 and 6 are both even, so the queried subarray is not special.'),([[4,3,1,6],[[0,2],[2,3]]],'The first query contains adjacent odd values 3 and 1; the second alternates odd and even.')],[[n,q] for n,q in [([1],[[0,0]]),([1,2],[[0,1]]),([2,4],[[0,1]]),([3,4,1,2,6],[[0,3],[1,4],[4,4]]),([2,4,6],[[0,1],[1,2]]),([1,3,2],[[0,2],[1,2]]),([0,1,0,1],[[0,3],[1,1]]),([7,5,3],[[0,2]]),([2,3,5,6],[[0,1],[0,2],[2,3]]),([9,8,7,6,5],[[0,4],[1,3]]),([4,4,5,7,8],[[1,4]]),([1,2,4,3],[[0,3],[2,3]]),([6,1,8,3,10],[[0,4]]),([0,2,1,3,4],[[0,4],[2,4]])]],SPECIAL,[SPECIAL.replace('bad[right]==bad[left]','bad[right]-bad[left]<=1'),SPECIAL.replace('==','!=',1)],['Allows one bad adjacency even though every adjacent pair must alternate.','Counts opposite-parity edges as bad instead of equal-parity edges.'],special_oracle,random_special,lesson('A query fails exactly when its interior contains at least one equal-parity adjacent edge.','Build a prefix count of bad edges and compare the count at the query endpoints.','bad[i]=bad[i-1]+sameParity(nums[i-1],nums[i]); answer bad[r]==bad[l].','Subtracting endpoint prefix counts counts precisely the bad edges whose right endpoint lies in (left,right].'),'O(n+queries)','O(n)',5),
3153: entry('sum_pair_digit_differences',[('nums','list[int]')],'int',['counting','combinatorics','digits'],['nums contains at least two positive integers and all have the same decimal digit length.','For every unordered pair, count positions where their decimal digits differ.','Return the sum of those counts over all unordered pairs.'],[([[13,23,12]],'The pairs differ in 1, 1, and 2 positions respectively, totaling four.'),([[10,10,10]],'All digits match at every position, so the total is zero.')],[[n] for n in [[1,2],[10,11],[13,23,12],[10,10,10],[123,456],[111,222,121],[99,10,90],[100,101,110,111],[7,8,9,7],[555,505,550],[1000,9999],[314,159,265,358],[42,24,44,22],[98765,98764,18765]]],DIGITS,[DIGITS.replace('answer+=index-counts.get(digit,0)','answer+=counts.get(digit,0)'),DIGITS.replace('for position in range(len(texts[0]))','for position in range(len(texts[0])-1)')],['Counts earlier matching digits rather than earlier differing digits.','Skips the final digit position entirely.'],digits_oracle,random_digits,lesson('At one position, each new number differs from all earlier numbers except those with the same digit.','Scan positions and numbers, maintaining counts of previously seen digits at that position.','For item index i add i-count[digit], then increment count[digit]; sum across positions.','Every unordered pair is counted once when its later member is processed, exactly at the positions where the two digits differ.'),'O(n*digits)','O(10)',5),
}
