"""Final string layer, equal-score recursion, modified runs, digit prefixes, and primes."""
from collections import Counter
from functools import lru_cache
from itertools import product
from math import isqrt

from .import_batch_055 import entry


def last_string_oracle(args):
    current = args[0]
    while current:
        previous = current; removed = set(); following = []
        for char in current:
            if char not in removed:
                removed.add(char)
            else:
                following.append(char)
        current = ''.join(following)
    return previous


def random_last_string(rng):
    return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1, 35)))]


def operations_oracle(args):
    nums = tuple(args[0])

    @lru_cache(None)
    def continue_with(values, score):
        if len(values) < 2:
            return 0
        choices = ((values[:2], values[2:]), (values[-2:], values[:-2]),
                   ((values[0], values[-1]), values[1:-1]))
        return max([1 + continue_with(rest, score) for removed, rest in choices if sum(removed) == score] or [0])

    choices = ((nums[:2], nums[2:]), (nums[-2:], nums[:-2]), ((nums[0], nums[-1]), nums[1:-1]))
    return max(1 + continue_with(rest, sum(removed)) for removed, rest in choices)


def random_operations(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(2, 12))]]


def consecutive_oracle(args):
    nums = args[0]; answer = 1
    for changed in product((0, 1), repeat=len(nums)):
        values = {value + changed[index] for index, value in enumerate(nums)}
        for start in values:
            length = 0
            while start + length in values:
                length += 1
            answer = max(answer, length)
    return answer


def random_consecutive(rng):
    return [[rng.randint(1, 15) for _ in range(rng.randint(1, 10))]]


def prefix_oracle(args):
    first, second = args; answer = 0
    for left in first:
        for right in second:
            length = 0
            for a, b in zip(str(left), str(right)):
                if a != b:
                    break
                length += 1
            answer = max(answer, length)
    return answer


def random_prefix(rng):
    return [[rng.randint(1, 999999) for _ in range(rng.randint(1, 10))],
            [rng.randint(1, 999999) for _ in range(rng.randint(1, 10))]]


def prime_oracle(args):
    matrix = args[0]; rows, columns = len(matrix), len(matrix[0]); counts = Counter()

    def prime(value):
        return value > 10 and all(value % divisor for divisor in range(2, isqrt(value) + 1))

    for row in range(rows):
        for column in range(columns):
            for dr, dc in product((-1, 0, 1), repeat=2):
                if dr == dc == 0:
                    continue
                r, c, value = row + dr, column + dc, matrix[row][column]
                while 0 <= r < rows and 0 <= c < columns:
                    value = value * 10 + matrix[r][c]
                    if prime(value):
                        counts[value] += 1
                    r += dr; c += dc
    return max(counts, key=lambda value: (counts[value], value)) if counts else -1


def random_prime(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    return [[[rng.randint(1, 9) for _ in range(columns)] for _ in range(rows)]]


LAST_STRING = '''def last_nonempty_removal_string(s):
    counts=Counter(s);maximum=max(counts.values());last={char:index for index,char in enumerate(s)}
    return ''.join(char for index,char in enumerate(s) if counts[char]==maximum and last[char]==index)
'''

SORTED_LAST = '''def last_nonempty_removal_string(s):
    counts=Counter(s);maximum=max(counts.values());last={char:index for index,char in enumerate(s)}
    return ''.join(sorted(char for index,char in enumerate(s) if counts[char]==maximum and last[char]==index))
'''


OPERATIONS = '''def maximum_equal_score_operations(nums):
    from functools import lru_cache
    def evaluate(score,left,right):
        @lru_cache(None)
        def search(i,j):
            if j-i<1:return 0
            answer=0
            if nums[i]+nums[i+1]==score:answer=max(answer,1+search(i+2,j))
            if nums[i]+nums[j]==score:answer=max(answer,1+search(i+1,j-1))
            if nums[j-1]+nums[j]==score:answer=max(answer,1+search(i,j-2))
            return answer
        return 1+search(left,right)
    size=len(nums)
    return max(evaluate(nums[0]+nums[1],2,size-1),evaluate(nums[-2]+nums[-1],0,size-3),evaluate(nums[0]+nums[-1],1,size-2))
'''


CONSECUTIVE = '''def maximum_modified_consecutive_elements(nums):
    best={};answer=1
    for value in sorted(nums):
        extended=best.get(value,0)+1
        best[value]=max(best.get(value,0),best.get(value-1,0)+1)
        best[value+1]=max(best.get(value+1,0),extended)
        answer=max(answer,best[value],best[value+1])
    return answer
'''


PREFIX = '''def longest_integer_common_prefix(arr1,arr2):
    prefixes=set()
    for value in arr1:
        while value:prefixes.add(value);value//=10
    answer=0
    for value in arr2:
        while value and value not in prefixes:value//=10
        if value:answer=max(answer,len(str(value)))
    return answer
'''


PRIME = '''def most_frequent_directional_prime(mat):
    from collections import Counter
    from itertools import product
    from math import isqrt
    def prime(value):return value>10 and all(value%divisor for divisor in range(2,isqrt(value)+1))
    rows=len(mat);columns=len(mat[0]);counts=Counter()
    for row in range(rows):
        for column in range(columns):
            for dr,dc in product((-1,0,1),repeat=2):
                if dr==dc==0:continue
                r=row+dr;c=column+dc;value=mat[row][column]
                while 0<=r<rows and 0<=c<columns:
                    value=value*10+mat[r][c]
                    if prime(value):counts[value]+=1
                    r+=dr;c+=dc
    return max(counts,key=lambda value:(counts[value],value)) if counts else -1
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3039: entry('last_nonempty_removal_string',[('s','str')],'str',['counting','strings','hash maps'],['s is a nonempty lowercase string.','Each round removes the first remaining occurrence of every character that is still present.','Return the exact remaining string immediately before the final round, preserving its order.'],[(['aabcbbca'],'After two rounds the remaining string is ba; the third round removes both characters.'),(['abcd'],'Every character occurs once, so the original string is the state immediately before the only round.')],[[s] for s in ['a','aa','aba','abba','abcabc','zzzyyy','aabbccdd','mississippi','leetcode','banana','abracadabra','abcddcba','eeeeabcd','qwertyqwerty']],LAST_STRING,[LAST_STRING.replace('last[char]==index','s.index(char)==index'),SORTED_LAST],['Keeps the first maximum-frequency occurrence rather than the last surviving occurrence.','Sorts the final characters alphabetically instead of preserving their positions in the current string.'],last_string_oracle,random_last_string,lesson('A character survives into the final nonempty round exactly when its total frequency is globally maximal.','Keep the last occurrence of every maximum-frequency character in original position order.','Count frequencies, record last indices, and emit positions that are both last and have maximum count.','After maximum-1 rounds only maximum-frequency characters remain once each, specifically at their original last occurrences; all others were exhausted earlier.'),'O(n)','O(26)',5),
3040: entry('maximum_equal_score_operations',[('nums','list[int]')],'int',['recursion','dynamic programming','intervals'],['nums contains at least two positive integers.','Each operation deletes the first pair, last pair, or two endpoints; every chosen pair must have the same sum as the first operation.','Return the maximum possible number of deletions.'],[([[3,2,1,2,3,4]],'Choose score five: remove the first pair, then both endpoints twice, for three operations.'),([[3,2,6,1,4]],'With score five, removing the first pair then the last pair yields two operations, which is optimal.')],[[n] for n in [[1,1],[1,2,3],[1,1,1,1],[1,2,1,2],[2,1,1,2],[1,2,3,4],[4,3,2,1],[2,2,3,1,2,2],[5,1,2,4,3,3],[3,3,3,3,3,3],[1,5,2,4,3,3,6,7],[10,1,9,2,8,3],[2,7,4,5,6,3,8,1],[1,4,2,3,5,7,6,1]]],OPERATIONS,[OPERATIONS.replace("if nums[i]+nums[j]==score:answer=max(answer,1+search(i+1,j-1))",''),OPERATIONS.replace('return max(evaluate(nums[0]+nums[1],2,size-1),evaluate(nums[-2]+nums[-1],0,size-3),evaluate(nums[0]+nums[-1],1,size-2))','return evaluate(nums[0]+nums[1],2,size-1)')],['Never considers deleting the two endpoints after the score is fixed.','Assumes the first operation removes the first two elements and ignores the other two possible initial scores.'],operations_oracle,random_operations,lesson('Only three first-operation scores are possible; after fixing one, the remaining state is an interval.','Memoize the best continuation for each [left,right] interval under each candidate score.','Try matching first-two, endpoints, and last-two transitions; evaluate all three initial removals and add the first operation.','Every legal deletion maps to exactly one interval transition, and memoization explores all choices without recomputing overlapping intervals.'),'O(n^2)','O(n^2)',5),
3041: entry('maximum_modified_consecutive_elements',[('nums','list[int]')],'int',['dynamic programming','sorting','arrays'],['nums is a nonempty positive-integer array.','Each element may independently stay unchanged or increase by exactly one before selection.','Choose the largest subset whose sorted values are distinct consecutive integers.'],[([[2,1,5,1,1]],'Modify one two to three and one one to two, then select values one, two, and three.'),([[1,4,7,10]],'No two values can be made adjacent, so only one element can be selected.')],[[n] for n in [[1],[1,1],[1,2],[2,2],[1,1,1],[1,2,3],[3,2,1],[1,3],[1,3,3],[2,3,5,6],[5,5,6,7],[1,2,2,3,4],[10,8,9,9,7],[2,4,4,5,7,8]]],CONSECUTIVE,[CONSECUTIVE.replace('best.get(value,0)+1','best.get(value-1,0)+1',1),CONSECUTIVE.replace('for value in sorted(nums)','for value in nums')],['Extends an incremented value from chains ending at value-1 instead of value.','Processes input order even though the recurrence requires nondecreasing values.'],consecutive_oracle,random_consecutive,lesson('After sorting, an element x can end a chain at x unchanged or at x+1 after incrementing.','Track the best chain length by final endpoint and update both choices using pre-update states.','Save old best[x]; set best[x] from best[x-1]+1 and best[x+1] from old best[x]+1.','Sorting ensures all earlier chain elements are available, and the two transitions exhaust the allowed final value of each processed element.'),'O(n log n)','O(n)',8),
3043: entry('longest_integer_common_prefix',[('arr1','list[int]'),('arr2','list[int]')],'int',['hash sets','digit prefixes','arrays'],['Both arrays are nonempty and contain positive integers.','A prefix consists of one or more leading decimal digits.','Return the maximum common-prefix length across one number from each array, or zero.'],[([[1,10,100],[1000]],'The pair one hundred and one thousand shares prefix 100 of length three.'),([[1,2,3],[4,4,4]],'No cross-array pair shares even its first digit, so the result is zero.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([12],[123]),([123],[12]),([1234],[1299]),([98,765],[9876]),([10,20],[100,299]),([555,123],[556,124]),([99999999],[99990000]),([1,10,100],[1000]),([123,456],[789,451]),([31415,2718],[314,27]),([808,80],[8]),([42,420,4200],[421,4209])]],PREFIX,[PREFIX.replace('while value:prefixes.add(value);value//=10','prefixes.add(value)'),PREFIX.replace('answer=max(answer,len(str(value)))','answer=max(answer,value)')],['Stores only complete first-array numbers rather than all of their prefixes.','Maximizes the numeric prefix value and returns it instead of maximizing and returning its digit length.'],prefix_oracle,random_prefix,lesson('Removing trailing decimal digits enumerates every nonempty prefix of an integer.','Store all prefixes from the first array, then shorten each second-array value until it matches one.','Repeatedly divide by ten; on the first stored match update the maximum digit length.','The first match while shortening is the longest for that pair, and checking every second-array number covers all cross-array pairs.'),'O(total digits)','O(total digits)',5),
3044: entry('most_frequent_directional_prime',[('mat','list[list[int]]')],'int',['matrices','enumeration','primality'],['mat is a nonempty matrix up to 6×6 containing digits one through nine.','From every cell, extend in one fixed one of eight directions and count every formed prime greater than ten.','Return the highest-frequency prime, breaking ties toward the larger value, or -1.'],[([[[1,1],[9,9],[1,1]]],'Prime nineteen is formed most often across vertical and diagonal directions.'),([[[7]]],'Seven is prime but not greater than ten, so no qualifying result exists.')],[[m] for m in [[[1,3]],[[3,1]],[[1,1]],[[2,3]],[[9,7,8],[4,6,5],[2,8,6]],[[1,9,1]],[[1],[3]],[[2,9],[3,1]],[[4,1],[1,3]],[[9,9],[9,9]],[[1,7,3],[7,1,7]],[[2,3,5],[7,1,1]],[[8,9,7],[6,5,4]],[[1,2,3],[4,5,6],[7,8,9]]]],PRIME,[PRIME.replace("product((-1,0,1),repeat=2)","((1,0),(-1,0),(0,1),(0,-1))"),PRIME.replace('max(counts,key=lambda value:(counts[value],value))','min(counts,key=lambda value:(-counts[value],value))')],['Searches only four cardinal directions and misses diagonal numbers.','Breaks equal-frequency ties toward the smaller prime.'],prime_oracle,random_prime,lesson('Each start and fixed direction generates one decimal prefix per step, and repeated generation contributes repeated frequency.','Enumerate eight rays, extend the numeric value digit by digit, and count values passing trial-division primality.','For every cell and direction, walk in bounds; value=10*value+digit; count primes >10; maximize (frequency,value).','Every legal generated number corresponds to one unique ray prefix, so enumeration preserves exact multiplicity and the tuple maximum implements the tie rule.'),'O(rows*columns*8*rayLength*sqrt(value))','O(distinct primes)',5),
}
