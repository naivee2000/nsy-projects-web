"""First slice of workbook batch 129."""

from collections import Counter

from .import_batch_055 import entry


def poker_oracle(args):
    ranks, suits = args
    if len(set(suits)) == 1: return 'Flush'
    frequency = max(Counter(ranks).values())
    if frequency >= 3: return 'Three of a Kind'
    if frequency == 2: return 'Pair'
    return 'High Card'


def random_poker(rng):
    return [[rng.randint(1, 13) for _ in range(5)], [rng.choice('abcd') for _ in range(5)]]


def zero_oracle(args):
    nums = args[0]; answer = 0
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            if all(value == 0 for value in nums[left:right + 1]): answer += 1
    return answer


def random_zero(rng):
    return [[rng.randint(0, 3) for _ in range(rng.randint(1, 25))]]


def repeat_oracle(args):
    text = args[0]
    for index, char in enumerate(text):
        if char in text[:index]: return char


def random_repeat(rng):
    alphabet = list('abcdefghijklmnopqrstuvwxyz'); rng.shuffle(alphabet)
    length = rng.randint(2, 20); text = alphabet[:length]
    text.insert(rng.randint(1, length), rng.choice(text))
    return [''.join(text)]


def row_column_oracle(args):
    grid = args[0]; n = len(grid); answer = 0
    for row in range(n):
        for column in range(n):
            if all(grid[row][index] == grid[index][column] for index in range(n)): answer += 1
    return answer


def random_row_column(rng):
    n = rng.randint(1, 6)
    return [[[rng.randint(0, 4) for _ in range(n)] for _ in range(n)]]


def reductions_oracle(args):
    values = list(args[0]); operations = 0
    while any(values):
        smallest = min(value for value in values if value)
        values = [value - smallest if value else 0 for value in values]; operations += 1
    return operations


def random_reductions(rng):
    return [[rng.randint(0, 15) for _ in range(rng.randint(1, 20))]]


POKER='''\
def best_poker_hand(ranks,suits):
    if len(set(suits))==1:return 'Flush'
    frequency=max(__import__('collections').Counter(ranks).values())
    if frequency>=3:return 'Three of a Kind'
    if frequency==2:return 'Pair'
    return 'High Card'
'''

ZERO='''\
def count_zero_filled_subarrays(nums):
    run=answer=0
    for value in nums:
        run=run+1 if value==0 else 0;answer+=run
    return answer
'''

REPEAT='''\
def first_repeated_letter(s):
    seen=set()
    for char in s:
        if char in seen:return char
        seen.add(char)
'''

EQUAL='''\
def count_equal_row_column_pairs(grid):
    rows=__import__('collections').Counter(map(tuple,grid))
    return sum(rows[tuple(column)] for column in zip(*grid))
'''

REDUCE='''\
def minimum_operations_to_zero(nums):
    return len({value for value in nums if value>0})
'''


BATCH={
2347:entry('best_poker_hand',[('ranks','list[int]'),('suits','list[str]')],'str',['arrays','counting'],['Exactly five cards are provided.','Return Flush, Three of a Kind, Pair, or High Card in that priority order.','Only rank equality and suit equality matter; straights are not a category.'],[([[13,2,3,1,9],['a','a','a','a','a']],'All suits match, so Flush has highest priority.'),([[4,4,2,4,4],['d','a','a','b','c']],'Four equal ranks satisfy the Three of a Kind category.')],[[r,s] for r,s in [([1,2,3,4,5],list('abcda')),([1,1,2,3,4],list('abcda')),([1,1,1,2,3],list('abcda')),([1,1,2,2,3],list('abcda')),([7,7,7,7,7],list('abcda')),([1,2,3,4,5],list('bbbbb')),([2,2,3,3,4],list('abcde')),([9,8,7,6,5],list('abcde')),([13,13,1,2,3],list('aabcd')),([3,3,3,4,5],list('abcdd')),([1,2,1,2,1],list('abcde')),([10,11,12,13,1],list('ccccc')),([5,6,7,8,5],list('abcde')),([2,3,4,2,2],list('aabcc'))]],POKER,[POKER.replace("if len(set(suits))==1:return 'Flush'",''),POKER.replace('frequency>=3','frequency==3')],['Never checks for a flush before rank-based categories.','Rejects four or five equal ranks even though they contain three of a kind.'],poker_oracle,random_poker,['Check whether all five suits are identical first.','Count occurrences of every rank.','Use the maximum rank frequency to distinguish three-or-more, exactly two, and all distinct.','The categories are tested in required priority order, so the first match is the best hand.'],'O(1)','O(1)',3),
2348:entry('count_zero_filled_subarrays',[('nums','list[int]')],'int',['arrays','dynamic programming'],['Count nonempty contiguous subarrays containing only zeroes.','Nonzero values end the current zero run.','Return the total count across all runs.'],[([[1,3,0,0,2,0,0,4]],'Each length-two zero run contributes three subarrays, totaling six.'),([[0,0,0]],'A length-three run contributes one plus two plus three, which is six.')],[[a] for a in [[0],[1],[0,1],[1,0],[0,0],[1,0,1],[0,0,0,0],[2,0,0,0,3],[0,1,0,1,0],[5,4,3],[0,0,1,0],[1,0,0,0],[0,2,0,0,2,0],[3,0,0,1,0,0,0]]],ZERO,[ZERO.replace('answer+=run','answer+=1 if run else 0'),ZERO.replace('else 0','else run')],['Counts only one subarray for each zero position and misses longer endings.','Fails to reset the run at nonzero values, joining separated runs.'],zero_oracle,random_zero,['Track the length of the zero run ending at the current position.','A nonzero resets that run to zero.','A zero extends the run; add the new run length because that many zero-only subarrays end here.','Every qualifying subarray has one right endpoint and is counted exactly in that endpoint’s run contribution.'],'O(n)','O(1)',5),
2351:entry('first_repeated_letter',[('s','str')],'str',['strings','hash sets'],['The lowercase string contains at least one repeated letter.','Return the letter whose second occurrence appears earliest.','Scan order, not alphabetic order, determines the answer.'],[(['abccbaacz'],'The second c is the earliest second occurrence.'),(['abcdd'],'The final d is the first character encountered for a second time.')],[[s] for s in ['aa','aba','abb','abca','xyzx','qwertyq','abcdefgg','zxyzy','aabb','abcadeaf','mnopqm','hello','leetcode','programming']],REPEAT,[REPEAT.replace('for char in s:',"for char in sorted(s):"),REPEAT.replace('return char','return min(seen)')],['Sorts characters and returns an alphabetic duplicate instead of the earliest second occurrence.','Returns the smallest previously seen character rather than the character that just repeated.'],repeat_oracle,random_repeat,['Maintain a set of letters already visited.','Read the string from left to right.','Return immediately when the current letter is already in the set; otherwise add it.','The first membership hit is precisely the earliest second occurrence by scan order.'],'O(n)','O(1)',3),
2352:entry('count_equal_row_column_pairs',[('grid','list[list[int]]')],'int',['matrices','hash maps'],['The grid is square.','A row-column pair is equal only when all values match in the same order.','Count index pairs, so duplicate equal rows or columns contribute separately.'],[([[[3,2,1],[1,7,6],[2,7,7]]],'Only the first row equals the first column.'),([[[3,1,2,2],[1,4,4,5],[2,4,2,2],[2,4,2,2]]],'Duplicate matching rows and columns produce three index pairs.')],[[g] for g in [[[1]],[[1,2],[1,2]],[[1,1],[1,1]],[[1,2],[2,1]],[[1,2,3],[1,2,3],[1,2,3]],[[1,0,0],[0,1,0],[0,0,1]],[[2,2,1],[2,2,1],[1,1,0]],[[0,1],[1,0]],[[1,2,1],[2,3,2],[1,2,1]],[[5,6],[7,8]],[[1,2,3],[4,5,6],[7,8,9]],[[3,3,3],[3,3,3],[3,3,3]],[[1,0,1],[0,1,0],[1,0,1]],[[2,1],[1,2]]]],EQUAL,[EQUAL.replace('sum(rows[tuple(column)]','sum(tuple(column) in rows'),EQUAL.replace('zip(*grid)','grid')],['Counts only whether a row exists and loses duplicate row multiplicity.','Compares rows with rows rather than constructing columns.'],row_column_oracle,random_row_column,['Represent each row as an immutable tuple.','Count duplicate row tuples in a frequency map.','Transpose with zip to obtain each column tuple, adding its row frequency.','For every column, the frequency is exactly the number of row indexes forming an equal pair with it.'],'O(n^2)','O(n^2)',5),
2357:entry('minimum_operations_to_zero',[('nums','list[int]')],'int',['arrays','hash sets','greedy'],['In one operation choose a positive x no larger than the smallest positive value and subtract x from every positive element.','Repeat until every element equals zero.','Return the minimum operation count.'],[([[1,5,0,3,5]],'Choosing one, then two, then two eliminates the three distinct positive levels in three operations.'),([[0]],'No operation is needed because the array is already zero.')],[[a] for a in [[1],[1,1],[1,2],[2,4,6],[0,1,0],[5,5,5],[1,3,3,7],[0,0,0],[10,1,10],[2,2,3,3],[9,8,7,6],[1,2,3,4,5],[100,50,0,100],[4,1,4,2,1]]],REDUCE,[REDUCE.replace('if value>0',''),REDUCE.replace('len({value for value in nums if value>0})','max(nums)')],['Counts zero as an operation level even though it never needs subtraction.','Returns the largest value, confusing unit decrements with allowed bulk subtraction.'],reductions_oracle,random_reductions,['Each operation can eliminate at most one distinct positive level relative to the lower levels.','Choose the current smallest positive level each time.','This shifts all remaining positives downward and removes exactly that distinct level.','Thus every distinct positive value is necessary and the greedy sequence achieves one operation per distinct value.'],'O(n)','O(n)',3),
}
