"""Disjoint-subarray DP, matrix patterns, marking, replacement, and power sums."""
from itertools import combinations_with_replacement
from string import ascii_lowercase

from .import_batch_055 import entry


def strength_oracle(args):
    nums, count = args; prefix = [0]
    for value in nums:
        prefix.append(prefix[-1] + value)
    best = -10**30

    def choose(position, used, total):
        nonlocal best
        if used == count:
            best = max(best, total); return
        remaining = count - used
        coefficient = (count - used) * (1 if used % 2 == 0 else -1)
        for left in range(position, len(nums) - remaining + 1):
            for right in range(left + 1, len(nums) - remaining + 2):
                choose(right, used + 1, total + coefficient * (prefix[right] - prefix[left]))

    choose(0, 0, 0)
    return best


def random_strength(rng):
    size = rng.randint(1, 9)
    choices = [value for value in (1, 3, 5) if value <= size]
    return [[rng.randint(-9, 9) for _ in range(size)], rng.choice(choices)]


def pattern_oracle(args):
    board, pattern = args
    height, width = len(pattern), len(pattern[0])
    for top in range(len(board) - height + 1):
        for left in range(len(board[0]) - width + 1):
            letters, values = {}, {}
            valid = True
            for row in range(height):
                for column in range(width):
                    symbol = pattern[row][column]; value = board[top + row][left + column]
                    if symbol.isdigit():
                        valid &= int(symbol) == value
                    elif ((symbol in letters and letters[symbol] != value) or
                          (value in values and values[value] != symbol)):
                        valid = False
                    else:
                        letters[symbol] = value; values[value] = symbol
            if valid:
                return [top, left]
    return [-1, -1]


def random_pattern(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    board = [[rng.randrange(5) for _ in range(columns)] for _ in range(rows)]
    height, width = rng.randint(1, rows), rng.randint(1, columns)
    pattern = [''.join(rng.choice('abc01234') for _ in range(width)) for _ in range(height)]
    return [board, pattern]


def marking_oracle(args):
    nums, queries = args; marked = set(); answer = []
    for index, count in queries:
        marked.add(index)
        available = sorted((value, position) for position, value in enumerate(nums) if position not in marked)
        marked.update(position for _, position in available[:count])
        answer.append(sum(value for position, value in enumerate(nums) if position not in marked))
    return answer


def random_marking(rng):
    size = rng.randint(1, 10)
    nums = [rng.randint(1, 15) for _ in range(size)]
    queries = [[rng.randrange(size), rng.randint(0, size)] for _ in range(rng.randint(1, 8))]
    return [nums, queries]


def replacement_oracle(args):
    text = args[0]; missing = text.count('?'); fixed = [text.count(letter) for letter in ascii_lowercase]
    best_key = None; best_letters = None
    for indexes in combinations_with_replacement(range(26), missing):
        counts = fixed[:]
        for index in indexes:
            counts[index] += 1
        value = sum(count * (count - 1) // 2 for count in counts)
        letters = ''.join(ascii_lowercase[index] for index in indexes)
        key = (value, letters)
        if best_key is None or key < best_key:
            best_key, best_letters = key, letters
    iterator = iter(best_letters or '')
    return ''.join(next(iterator) if char == '?' else char for char in text)


def random_replacement(rng):
    size = rng.randint(1, 9); missing = rng.randint(0, min(3, size))
    chars = [rng.choice('abcdef') for _ in range(size)]
    for index in rng.sample(range(size), missing):
        chars[index] = '?'
    return [''.join(chars)]


def power_oracle(args):
    nums, target = args; answer = 0; size = len(nums)
    for mask in range(1 << size):
        total = sum(nums[index] for index in range(size) if mask >> index & 1)
        if total == target:
            answer += 1 << (size - mask.bit_count())
    return answer % 1_000_000_007


def random_power(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(1, 10))], rng.randint(1, 20)]


STRENGTH = '''def maximum_k_subarray_strength(nums,k):
    negative=-10**30
    closed=[negative]*(k+1);opened=[negative]*(k+1);closed[0]=0
    for value in nums:
        old_closed=closed;old_opened=opened
        closed=[negative]*(k+1);opened=[negative]*(k+1)
        closed[0]=0
        for used in range(1,k+1):
            coefficient=(k-used+1)*(1 if used%2 else -1)
            closed[used]=max(old_closed[used],old_opened[used])
            opened[used]=max(old_opened[used]+coefficient*value,
                max(old_closed[used-1],old_opened[used-1])+coefficient*value)
    return max(closed[k],opened[k])
'''


PATTERN = '''def find_alphanumeric_matrix_pattern(board,pattern):
    height=len(pattern);width=len(pattern[0])
    for top in range(len(board)-height+1):
        for left in range(len(board[0])-width+1):
            forward={};reverse={};valid=True
            for row in range(height):
                for column in range(width):
                    symbol=pattern[row][column];value=board[top+row][left+column]
                    if symbol.isdigit():
                        if int(symbol)!=value:valid=False
                    elif ((symbol in forward and forward[symbol]!=value) or
                          (value in reverse and reverse[value]!=symbol)):valid=False
                    else:forward[symbol]=value;reverse[value]=symbol
            if valid:return [top,left]
    return [-1,-1]
'''


MARKING = '''def unmarked_sums_after_queries(nums,queries):
    ordered=sorted((value,index) for index,value in enumerate(nums));marked=[False]*len(nums)
    remaining=sum(nums);cursor=0;answer=[]
    for index,count in queries:
        if not marked[index]:marked[index]=True;remaining-=nums[index]
        while count and cursor<len(ordered):
            value,position=ordered[cursor];cursor+=1
            if not marked[position]:marked[position]=True;remaining-=value;count-=1
        answer.append(remaining)
    return answer
'''


REPLACEMENT = '''def minimize_question_mark_string(s):
    from collections import Counter
    from heapq import heapify,heapreplace
    from string import ascii_lowercase
    counts=Counter(s);heap=[(counts[letter],letter) for letter in ascii_lowercase];heapify(heap)
    chosen=[]
    for _ in range(s.count('?')):
        count,letter=heap[0];chosen.append(letter);heapreplace(heap,(count+1,letter))
    chosen.sort();iterator=iter(chosen)
    return ''.join(next(iterator) if char=='?' else char for char in s)
'''


POWER = '''def sum_of_subsequence_powers(nums,k):
    modulo=1000000007;dp=[0]*(k+1);dp[0]=1
    for value in nums:
        following=[count*2%modulo for count in dp]
        for total in range(value,k+1):following[total]=(following[total]+dp[total-value])%modulo
        dp=following
    return dp[k]
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3077: entry('maximum_k_subarray_strength',[('nums','list[int]'),('k','int')],'int',['dynamic programming','subarrays','state machines'],['nums is nonempty, may contain negative values, and k is a positive odd integer no larger than its length.','Choose exactly k nonempty disjoint subarrays in left-to-right order.','Subarray number i has alternating coefficient +(k-i+1) for odd i and -(k-i+1) for even i; maximize the weighted sum.'],[([[1,2,3,-1,2],3],'Choosing [1,2,3], [-1], and [2] gives 3*6 - 2*(-1) + 2 = 22.'),([[-1,-2,-3],1],'The best single nonempty subarray is [-1], so the maximum strength is -1.')],[[a,k] for a,k in [([5],1),([-5],1),([1,2,3],1),([-1,-2,-3],3),([1,-1,1],3),([1,2,3,-1,2],3),([4,-5,6,-2,3],3),([0,0,0],3),([9,-10,9,-10,9],3),([1,2,3,4,5],3),([-5,10,-5,10,-5],5),([3,-1,4,-1,5,-9,2],3),([8,-2,-2,8,-2,8],5),([2,-7,6,1,-4,5,3],3)]],STRENGTH,[STRENGTH.replace('(1 if used%2 else -1)','1'),STRENGTH.replace('return max(closed[k],opened[k])','return max(max(closed),max(opened))')],['Uses positive coefficients for every selected subarray instead of alternating signs.','Allows fewer than exactly k subarrays by returning the best state at any count.'],strength_oracle,random_strength,lesson('At each position a selected subarray may start, continue, or a previous one may remain closed.','Track the best score after j subarrays with the current position outside or inside subarray j.','For each value and j, carry the best closed state, extend an open state, or start j from the previous j-1 state using its signed coefficient.','The two states enumerate every legal boundary choice exactly once, and restricting the final state to j=k enforces exactly k nonempty subarrays.'),'O(n*k)','O(k)',8),
3078: entry('find_alphanumeric_matrix_pattern',[('board','list[list[int]]'),('pattern','list[str]')],'list[int]',['matrices','hash maps','pattern matching'],['board is a nonempty rectangular digit matrix and pattern is a nonempty rectangular array of digit-or-lowercase-character strings that fits inside it.','Pattern digits must equal board digits literally; repeated letters map consistently to one digit.','Different letters must map to different digits; return the first matching top-left coordinate in row-major order, or [-1,-1].'],[([[[1,2,2],[2,2,3],[2,3,3]],['ab','bb']],'At [0,0], a maps to one and b maps to two consistently, so the first submatrix matches.'),([[[1,2],[2,1]],['a1']],'No row has a second cell equal to literal digit one while maintaining the placement, so no match exists.')],[[b,p] for b,p in [([[1]],['a']),([[1]],['1']),([[1]],['2']),([[1,1]],['aa']),([[1,1]],['ab']),([[1,2]],['ab']),([[1,2]],['aa']),([[1,2],[2,1]],['ab','ba']),([[1,2],[2,1]],['a2','2a']),([[0,1,2],[2,1,0]],['ab']),([[3,3,4],[4,3,3]],['aa','ba']),([[1,2,2],[2,2,3],[2,3,3]],['ab','bb']),([[1,2,3],[4,5,6],[7,8,9]],['ab','cd']),([[1,2,1],[2,1,2]],['aba'])]],PATTERN,[PATTERN.replace("elif ((symbol in forward", "elif False and ((symbol in forward"),PATTERN.replace("or\n                          (value in reverse and reverse[value]!=symbol)","or False")],['Accepts inconsistent repeated-letter assignments after their first occurrence.','Enforces letter consistency but not the required one-to-one mapping between distinct letters and digits.'],pattern_oracle,random_pattern,lesson('Letters form a bijection with the board values used by letters, while digit symbols are literal constraints.','Test placements in row-major order with forward and reverse maps local to each placement.','For every pattern cell, compare digits directly; for letters reject either mapping conflict, otherwise record both directions.','The two maps are exactly the consistency and distinctness rules, and the first successful row-major placement has the requested smallest coordinates.'),'O(board rows*board cols*pattern area)','O(distinct letters)',5),
3080: entry('unmarked_sums_after_queries',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['sorting','simulation','arrays'],['nums contains positive integers; all elements begin unmarked.','Each query first marks its stated index if needed, then marks up to count smallest unmarked values, breaking value ties by smaller index.','Return the sum of all unmarked values after every query.'],[([[1,2,2,1,2,3,1],[[1,2],[3,3],[4,2]]],'The remaining sums after the three rounds are eight, three, and zero.'),([[5,1,4,2],[[0,1],[0,1]]],'The first query marks values five and one, leaving six; the repeated index is already marked, then value two is marked, leaving four.')],[[a,q] for a,q in [([1],[[0,0]]),([1],[[0,1]]),([3,1,2],[[1,1]]),([3,1,2],[[0,0]]),([2,2,2],[[2,1]]),([5,1,4,2],[[0,1],[0,1]]),([1,2,3],[[0,5]]),([4,3,2,1],[[3,0],[2,1]]),([1,1,2,2],[[1,1],[3,1]]),([10,1,9,2],[[2,2]]),([8,6,7,5,3,4,9],[[0,3],[6,2]]),([1,2,2,1,2,3,1],[[1,2],[3,3],[4,2]]),([6,5,4,3,2,1],[[5,2],[0,1],[3,4]]),([2,9,1,8,3],[[1,0],[4,2],[2,2]])]],MARKING,[MARKING.replace('ordered=sorted((value,index)','ordered=sorted((-value,index)'),MARKING.replace('if not marked[index]:marked[index]=True;remaining-=nums[index]','marked[index]=True;remaining-=nums[index]')],['Marks the largest remaining values first instead of the smallest.','Subtracts a queried value again when its index was already marked.'],marking_oracle,random_marking,lesson('A global value/index ordering never changes; only marked entries become ineligible.','Sort once, advance one cursor past marked entries, and maintain the remaining sum.','Mark the query index conditionally; then scan sorted pairs until count new indices are marked; append remaining sum.','The cursor encounters every unmarked candidate in exact tie-breaking order, and conditional subtraction removes each value from the sum once.'),'O((n+queries) log n)','O(n)',5),
3081: entry('minimize_question_mark_string',[('s','str')],'str',['greedy','heaps','counting'],['s contains lowercase letters and question marks.','A completed string costs the number of equal-character pairs, equivalently the sum of equal predecessors at every index.','Minimize that cost, then return the lexicographically smallest minimizing completed string.'],[(['???'],'Using three distinct smallest letters gives minimum cost zero and lexicographically smallest result abc.'),(['a?a?'],'The missing letters b and c avoid increasing the two existing a characters, producing abac.')],[[s] for s in ['?','??','???','a?','?a','a?a?','abcdefghijklmnopqrstuvwxyz?','aaaaaaaa??','ab??','??ab','a?b?c','zz?zz?','leetcode','????','abcabc???']],REPLACEMENT,[REPLACEMENT.replace('chosen.sort()','chosen.sort(reverse=True)'),REPLACEMENT.replace('(counts[letter],letter)','(counts[letter],-ord(letter))').replace('count,letter=heap[0]','count,code=heap[0];letter=chr(-code)').replace('(count+1,letter)','(count+1,code)')],['Uses the optimal multiset but places its letters in descending order, losing the lexicographic tie-break.','Breaks equal-frequency heap ties toward larger letters instead of smaller ones.'],replacement_oracle,random_replacement,lesson('Adding one occurrence of a letter increases pair cost by its current frequency.','Repeatedly choose the least frequent letter, breaking ties alphabetically; sort all chosen letters before filling question-mark positions.','Use a heap of (frequency,letter), increment the chosen frequency, then place the sorted chosen multiset left to right.','Minimum marginal-cost choices minimize total pairs; rearranging the chosen multiset does not change cost, and sorted placement minimizes the final string.'),'O((n+questions) log 26)','O(n)',5),
3082: entry('sum_of_subsequence_powers',[('nums','list[int]'),('k','int')],'int',['dynamic programming','knapsack','subsequences'],['nums contains positive integers and k is positive.','For every subsequence T of nums, its power is the number of subsequences of T whose sum equals k.','Return the sum of those powers modulo 1,000,000,007.'],[([[1,2,3],3],'Target subset [3] belongs to four outer subsequences and [1,2] belongs to two, so the total power is six.'),([[1,1,1],2],'Each of the three target pairs belongs to two outer subsequences, giving total power six.')],[[a,k] for a,k in [([1],1),([1],2),([1,2],1),([1,2],3),([1,2,3],3),([1,1,1],2),([2,2,2],4),([3,1,4,1],5),([5,5,5,5],10),([1,2,4,8],7),([2,3,5,7],10),([1,1,2,3,5],5),([10,1,2,3],6),([4,4,1,1,2],6)]],POWER,[POWER.replace('count*2','count'),POWER.replace('following[total]+dp[total-value]','following[total]+2*dp[total-value]')],['Counts target-sum subsequences only once instead of once per containing outer subsequence.','Doubles the newly selected branch instead of the branch that omits the current element.'],power_oracle,random_power,lesson('Each target-sum chosen subset contributes once for every outer subsequence containing it; an unused element doubles the number of containers.','Use sum-indexed DP where skipping the current value doubles existing power and selecting it adds the prior lower-sum power once.','next[sum]=2*dp[sum]; when sum≥value add dp[sum-value], all modulo the required prime.','Every nested pair (target subset, containing outer subsequence) uniquely either omits the current element from both or selects it into the target subset, matching the two transitions.'),'O(n*k)','O(k)',8),
}
