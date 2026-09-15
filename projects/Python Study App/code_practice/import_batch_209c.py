"""Balanced matrix paths, feedback ranking, disjoint sets, cyclic subsequences, and k-avoidance."""
from itertools import combinations

from .import_batch_055 import entry


def equal_binary_path_oracle(args):
    grid = args[0]; rows, cols = len(grid), len(grid[0]); stack = [(0, 0, grid[0][0])]
    while stack:
        row, col, ones = stack.pop()
        if row == rows - 1 and col == cols - 1:
            if ones * 2 == rows + cols - 1: return True
            continue
        if row + 1 < rows: stack.append((row + 1, col, ones + grid[row + 1][col]))
        if col + 1 < cols: stack.append((row, col + 1, ones + grid[row][col + 1]))
    return False


def random_equal_binary_path(rng):
    rows, cols = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randrange(2) for _ in range(cols)] for _ in range(rows)]]


def top_students_oracle(args):
    positive, negative, reports, student_ids, count = args
    score = lambda report: sum(3 if word in positive else -1 if word in negative else 0 for word in report.split())
    ranked = [(score(report), student) for report, student in zip(reports, student_ids)]
    result = []
    while ranked and len(result) < count:
        best_score = max(value for value, _ in ranked)
        student = min(student for value, student in ranked if value == best_score)
        result.append(student); ranked.remove((best_score, student))
    return result


def random_top_students(rng):
    positive = ['good', 'smart']; negative = ['bad', 'late']; neutral = ['student', 'work']
    size = rng.randint(1, 8); ids = rng.sample(range(1, 60), size)
    reports = [' '.join(rng.choice(positive + negative + neutral) for _ in range(rng.randint(1, 7))) for _ in range(size)]
    return [positive, negative, reports, ids, rng.randint(1, size)]


def minimize_arrays_oracle(args):
    divisor1, divisor2, count1, count2 = args
    for maximum in range(1, 100):
        first = [value for value in range(1, maximum + 1) if value % divisor1]
        second = [value for value in range(1, maximum + 1) if value % divisor2]
        for chosen in combinations(first, count1):
            used = set(chosen)
            if sum(value not in used for value in second) >= count2: return maximum
    raise AssertionError('small oracle bound exceeded')


def random_minimize_arrays(rng):
    return [rng.randint(2, 8), rng.randint(2, 8), rng.randint(1, 5), rng.randint(1, 5)]


def cyclic_subsequence_oracle(args):
    source, target = args
    if len(target) > len(source): return False
    def matches(left, right): return right == left or ord(right) - ord(left) in (1, -25)
    return any(all(matches(source[index], char) for index, char in zip(indices, target)) for indices in combinations(range(len(source)), len(target)))


def random_cyclic_subsequence(rng):
    return [''.join(rng.choice('abcyz') for _ in range(rng.randint(1, 10))), ''.join(rng.choice('abcyz') for _ in range(rng.randint(1, 7)))]


def avoiding_sum_oracle(args):
    size, forbidden = args; upper = size + forbidden + 2
    return min(sum(values) for values in combinations(range(1, upper + 1), size) if all(a + b != forbidden for a, b in combinations(values, 2)))


def random_avoiding_sum(rng):
    return [rng.randint(1, 5), rng.randint(1, 10)]


EQUAL_PATH = '''def has_equal_binary_path(grid):
    rows=len(grid);cols=len(grid[0]);length=rows+cols-1
    if length%2:return False
    reachable=[[set() for _ in range(cols)] for _ in range(rows)];reachable[0][0].add(grid[0][0])
    for row in range(rows):
        for col in range(cols):
            if row==0 and col==0:continue
            previous=set()
            if row:previous|=reachable[row-1][col]
            if col:previous|=reachable[row][col-1]
            reachable[row][col]={ones+grid[row][col] for ones in previous}
    return length//2 in reachable[-1][-1]
'''


WHOLE_GRID_BALANCE = '''def has_equal_binary_path(grid):
    cells=len(grid)*len(grid[0])
    return 2*sum(sum(row) for row in grid)==cells
'''


TOP_STUDENTS = '''def reward_top_students(positive_feedback,negative_feedback,report,student_id,k):
    positive=set(positive_feedback);negative=set(negative_feedback);ranked=[]
    for text,student in zip(report,student_id):
        score=0
        for word in text.split():
            if word in positive:score+=3
            elif word in negative:score-=1
        ranked.append((-score,student))
    ranked.sort()
    return [student for _,student in ranked[:k]]
'''


MINIMIZE_ARRAYS = '''def minimize_two_array_maximum(divisor1,divisor2,unique_cnt1,unique_cnt2):
    import math
    common=math.lcm(divisor1,divisor2)
    def feasible(maximum):
        available1=maximum-maximum//divisor1
        available2=maximum-maximum//divisor2
        available_total=maximum-maximum//common
        return available1>=unique_cnt1 and available2>=unique_cnt2 and available_total>=unique_cnt1+unique_cnt2
    low=1;high=1
    while not feasible(high):high*=2
    while low<high:
        middle=(low+high)//2
        if feasible(middle):high=middle
        else:low=middle+1
    return low
'''


CYCLIC_SUBSEQUENCE = '''def can_make_cyclic_subsequence(str1,str2):
    target=0
    for char in str1:
        following='a' if char=='z' else chr(ord(char)+1)
        if target<len(str2) and str2[target] in (char,following):target+=1
    return target==len(str2)
'''


AVOIDING_SUM = '''def minimum_k_avoiding_sum(n,k):
    chosen=[];blocked=set();candidate=1
    while len(chosen)<n:
        if candidate not in blocked:
            chosen.append(candidate);blocked.add(k-candidate)
        candidate+=1
    return sum(chosen)
'''


SKIP_HALF = '''def minimum_k_avoiding_sum(n,k):
    chosen=[];candidate=1
    while len(chosen)<n:
        if 2*candidate!=k and all(candidate+value!=k for value in chosen):chosen.append(candidate)
        candidate+=1
    return sum(chosen)
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


BATCH = {
    2510: entry(
        'has_equal_binary_path',[('grid','list[list[int]]')],'bool',['dynamic programming','matrices','pathfinding'],
        ['grid is a nonempty rectangular binary matrix.','Move only right or down from the top-left through the bottom-right cell.','Return whether some path visits equal counts of zeros and ones.'],
        [([[[0,1,0,0],[0,1,0,0],[1,0,1,0]]],'A six-cell route exists with three zeros and three ones.'),([[[1,1,0],[0,0,1],[1,0,0]]],'Every five-cell path has odd length, so equal counts are impossible.')],
        [[[row[:] for row in grid]] for grid in [[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]],[[0,0],[1,1]],[[1,0],[0,1]],[[0,1,0],[1,0,1]],[[1,1,1],[0,0,0]],[[0,1,1],[0,0,1],[1,0,0]],[[1,0,1,0],[0,1,0,1]],[[0,0,1],[1,1,0],[0,1,0]],[[0,1],[0,1],[1,0]],[[1,0],[1,0],[0,1]],[[0,1,1,0],[1,0,0,1]],[[1,1,0],[0,1,0],[1,0,1],[0,1,0]]]],
        EQUAL_PATH,
        [WHOLE_GRID_BALANCE,EQUAL_PATH.replace('length=rows+cols-1','length=rows+cols')],
        ['Checks whether the whole matrix is balanced instead of whether one valid path is balanced.','Uses the number of moves rather than visited cells when deciding the required balance.'],
        equal_binary_path_oracle,random_equal_binary_path,
        lesson('All paths to a cell share the same length but may contain different counts of ones.','Store the reachable one-counts at every cell from its top and left predecessors.','Reject odd total path length; otherwise test whether half the length is reachable at the destination.','The transition enumerates every right/down predecessor and adds the current bit, so the destination set contains exactly all possible one-counts.'),
        'O(rows*cols*(rows+cols))','O(rows*cols*(rows+cols))',5,
    ),
    2512: entry(
        'reward_top_students',[('positive_feedback','list[str]'),('negative_feedback','list[str]'),('report','list[str]'),('student_id','list[int]'),('k','int')],'list[int]',
        ['hash maps','sorting','strings'],
        ['Positive and negative vocabularies are disjoint.','A positive word scores +3, a negative word -1, and every other report word zero.','Return the top k student IDs by descending score and then ascending ID.'],
        [([['smart','brilliant','studious'],['not'],['this student is studious','the student is smart'],[1,2],2],'Both students score three, so ID one ranks first.'),([['smart','brilliant','studious'],['not'],['this student is not studious','the student is smart'],[1,2],2],'Student two scores three versus student one’s two.')],
        [[p,n,r,s,k] for p,n,r,s,k in [(['good'],['bad'],['good'],[1],1),(['good'],['bad'],['bad'],[2],1),(['good'],['bad'],['work','student'],[2,1],2),(['good'],['bad'],['good','good'],[5,3],2),(['good'],['bad'],['good bad','good'],[1,2],2),(['a','b'],['x'],['a b','a x','none'],[9,3,5],2),(['smart'],['late'],['smart late','smart smart','late'],[10,20,30],3),(['up'],['down'],['up','up','down'],[3,2,1],1),(['yes'],['no'],['yes no no','no','yes'],[8,7,6],2),(['kind','fast'],['slow'],['kind fast','kind','fast slow'],[4,2,9],3),(['p'],['q'],['p q','p q','p q'],[10,1,5],2),(['win'],['lose'],['neutral','win lose','win'],[11,12,13],2),(['x'],['y'],['x x y','x y y','x'],[100,50,75],2),(['great'],['poor'],['great poor','poor poor','great great'],[6,4,2],3)]],
        TOP_STUDENTS,
        [TOP_STUDENTS.replace('score+=3','score+=1'),TOP_STUDENTS.replace('ranked.append((-score,student))','ranked.append((-score,-student))').replace('return [student for _,student in ranked[:k]]','return [-student for _,student in ranked[:k]]')],
        ['Awards only one point for positive feedback.','Breaks equal-score ties in favor of the larger student ID.'],
        top_students_oracle,random_top_students,
        lesson('Each report can be reduced to one numeric score.','Use sets for feedback lookup, then sort score-ID records by (-score,ID).','Tokenize every report, accumulate weights, sort, and return the first k IDs.','The sort key exactly encodes the primary descending score rule and secondary ascending-ID tie rule.'),
        'O(total words+n log n)','O(vocabulary+n)',5,
    ),
    2513: entry(
        'minimize_two_array_maximum',[('divisor1','int'),('divisor2','int'),('unique_cnt1','int'),('unique_cnt2','int')],'int',
        ['binary search','number theory','inclusion-exclusion'],
        ['Both divisors are at least two and both requested distinct counts are positive.','The first array excludes multiples of divisor1, the second excludes multiples of divisor2, and the arrays are disjoint.','Return the smallest possible maximum selected value.'],
        [([2,7,1,3],'Values through four can supply arr1=[1] and arr2=[2,3,4].'),([3,5,2,1],'Values through three can supply arr1=[1,2] and arr2=[3].')],
        [[a,b,x,y] for a,b,x,y in [(2,3,1,1),(2,4,8,2),(3,5,1,1),(3,5,2,2),(4,6,3,2),(2,2,1,1),(2,2,3,3),(5,7,4,1),(6,4,2,5),(7,8,5,4),(2,9,6,2),(10,3,2,6),(4,9,7,3),(8,12,5,5)]],
        MINIMIZE_ARRAYS,
        [MINIMIZE_ARRAYS.replace('and available_total>=unique_cnt1+unique_cnt2',''),MINIMIZE_ARRAYS.replace('maximum-maximum//divisor1','maximum-(maximum+divisor1-1)//divisor1')],
        ['Checks each array separately but ignores that their chosen values must be disjoint.','Subtracts an incorrect ceiling count of forbidden multiples.'],
        minimize_arrays_oracle,random_minimize_arrays,
        lesson('Feasibility below a maximum depends only on counts of allowed values and shared candidates.','Count each array’s allowed numbers and all numbers allowed by at least one array using the divisors’ LCM.','Binary-search the first maximum meeting both individual counts and the combined disjoint count.','The three inclusion-exclusion inequalities are necessary and sufficient to allocate exclusive values first and fill remaining slots from the shared pool; feasibility is monotone.'),
        'O(log answer)','O(1)',5,
    ),
    2825: entry(
        'can_make_cyclic_subsequence',[('str1','str'),('str2','str')],'bool',['two pointers','strings','subsequences'],
        ['Both strings are nonempty lowercase strings.','In one operation, any selected source characters advance once, with z wrapping to a.','Return whether str2 can become a subsequence after at most one such simultaneous operation.'],
        [(['abc','ad'],'Keep a and advance c to d, producing the target as a subsequence.'),(['zc','ad'],'Advance z to a and c to d, using both selected indices in the one operation.')],
        [[a,b] for a,b in [('a','a'),('a','b'),('a','c'),('z','a'),('z','z'),('ab','d'),('abc','abc'),('abc','bcd'),('abc','ac'),('xyz','ya'),('zz','aa'),('azby','ba'),('leetcode','mf'),('cabz','dba')]],
        CYCLIC_SUBSEQUENCE,
        [CYCLIC_SUBSEQUENCE.replace("following='a' if char=='z' else chr(ord(char)+1)","following=chr(ord(char)+1)"),CYCLIC_SUBSEQUENCE.replace('str2[target] in (char,following)','str2[target]==following')],
        ['Does not wrap z cyclically to a.','Requires every matched character to be incremented and disallows keeping it unchanged.'],
        cyclic_subsequence_oracle,random_cyclic_subsequence,
        lesson('Each source character can match either itself or its single cyclic successor.','Greedily match the earliest still-needed target character while scanning the source once.','Advance the target pointer whenever the current source character or its successor equals the target character.','Using the earliest possible source position never removes a future option and leaves the longest suffix for remaining target characters, proving the subsequence greedy choice.'),
        'O(len(str1))','O(1)',5,
    ),
    2829: entry(
        'minimum_k_avoiding_sum',[('n','int'),('k','int')],'int',['greedy','sets','math'],
        ['n and k are positive integers.','Choose n distinct positive integers with no two distinct selected values summing to k.','Return the minimum possible selected-value sum.'],
        [([5,4],'The lexicographically smallest valid choice [1,2,4,5,6] sums to eighteen.'),([2,6],'Values one and two do not sum to six and give the minimum sum three.')],
        [[n,k] for n,k in [(1,1),(1,2),(2,1),(2,2),(2,3),(3,4),(4,5),(5,2),(5,5),(6,7),(7,8),(8,3),(10,10),(12,7)]],
        AVOIDING_SUM,
        [AVOIDING_SUM.replace('blocked.add(k-candidate)','blocked.add(k+candidate)'),SKIP_HALF],
        ['Blocks k+candidate instead of the complementary value k-candidate.','Incorrectly treats using k/2 once as a forbidden pair with itself.'],
        avoiding_sum_oracle,random_avoiding_sum,
        lesson('Choosing a value only forbids its complementary value k-value.','Scan positive integers upward, select every unblocked candidate, and record its complement as blocked.','Continue until n values are chosen, then return their sum.','At each position the smallest feasible unused value minimizes the sorted selection prefix; replacing it with any larger value cannot improve later feasibility or reduce the total.'),
        'O(n+k)','O(n)',5,
    ),
}
