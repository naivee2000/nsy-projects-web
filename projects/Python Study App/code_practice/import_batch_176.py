"""Reverse matrix updates, digit DP, digit checks, sliding windows, and robot distance batch 176."""

from collections import Counter
from itertools import combinations

from .import_batch_055 import entry


def matrix_oracle(args):
    n,queries=args;matrix=[[0]*n for _ in range(n)]
    for kind,index,value in queries:
        if kind==0:matrix[index]=[value]*n
        else:
            for row in range(n):matrix[row][index]=value
    return sum(map(sum,matrix))


def random_matrix(rng):
    n=rng.randint(1,6);queries=[[rng.randrange(2),rng.randrange(n),rng.randint(0,20)] for _ in range(rng.randint(1,18))]
    return [n,queries]


def integers_oracle(args):
    low,high,minimum,maximum=args
    return sum(minimum<=sum(map(int,str(value)))<=maximum for value in range(int(low),int(high)+1))%1_000_000_007


def random_integers(rng):
    low=rng.randint(1,4500);high=rng.randint(low,5000);minimum=rng.randint(1,25);maximum=rng.randint(minimum,35)
    return [str(low),str(high),minimum,maximum]


def fascinating_oracle(args):
    n=args[0];counts=Counter(str(n)+str(2*n)+str(3*n))
    return counts==Counter('123456789')


def random_fascinating(rng):return [rng.randint(100,999)]


def semi_repetitive_oracle(args):
    s=args[0];best=0
    for left in range(len(s)):
        for right in range(left,len(s)):
            if sum(s[index]==s[index-1] for index in range(left+1,right+1))<=1:best=max(best,right-left+1)
    return best


def random_semi_repetitive(rng):return [''.join(rng.choice('0123456789') for _ in range(rng.randint(1,35)))]


def robots_oracle(args):
    nums,s,d=args;positions=[value+(d if direction=='R' else -d) for value,direction in zip(nums,s)]
    return sum(abs(first-second) for first,second in combinations(positions,2))%1_000_000_007


def random_robots(rng):
    size=rng.randint(2,25);nums=rng.sample(range(-200,201),size);directions=''.join(rng.choice('LR') for _ in nums)
    return [nums,directions,rng.randint(0,100)]


MATRIX="""\
def matrix_sum_after_queries(n,queries):
    used_rows=set();used_columns=set();answer=0
    for kind,index,value in reversed(queries):
        if kind==0 and index not in used_rows:
            answer+=value*(n-len(used_columns));used_rows.add(index)
        elif kind==1 and index not in used_columns:
            answer+=value*(n-len(used_rows));used_columns.add(index)
    return answer
"""

INTEGERS="""\
def count_integers_by_digit_sum(num1,num2,min_sum,max_sum):
    MOD=1_000_000_007
    def count(bound):
        if bound<0:return 0
        digits=list(map(int,str(bound)));memo={}
        def visit(index,total,tight):
            if total>max_sum:return 0
            if index==len(digits):return int(total>=min_sum)
            key=(index,total,tight)
            if key in memo:return memo[key]
            limit=digits[index] if tight else 9
            answer=sum(visit(index+1,total+digit,tight and digit==limit) for digit in range(limit+1))%MOD
            memo[key]=answer;return answer
        return visit(0,0,True)
    return (count(int(num2))-count(int(num1)-1))%MOD
"""

FASCINATING="""\
def is_fascinating_number(n):
    text=str(n)+str(2*n)+str(3*n)
    return len(text)==9 and set(text)==set('123456789')
"""

SEMI_REPETITIVE="""\
def longest_semi_repetitive_substring(s):
    left=0;previous_pair=0;answer=1
    for right in range(1,len(s)):
        if s[right]==s[right-1]:left=previous_pair;previous_pair=right
        answer=max(answer,right-left+1)
    return answer
"""

ROBOTS="""\
def sum_robot_distances(nums,s,d):
    MOD=1_000_000_007
    positions=sorted(value+(d if direction=='R' else -d) for value,direction in zip(nums,s))
    prefix=0;answer=0
    for index,value in enumerate(positions):answer=(answer+index*value-prefix)%MOD;prefix+=value
    return answer
"""


BATCH={
2718:entry('matrix_sum_after_queries',[('n','int'),('queries','list[list[int]]')],'int',['matrices','arrays','reverse processing'],
 ['Begin with an n by n matrix of zeroes.','A query [0,i,v] assigns v to every cell in row i; [1,i,v] does the same for column i.','Apply queries in order and return the final sum of all cells.'],
 [([3,[[0,0,1],[1,2,2],[0,2,3],[1,0,4]]],'After all overwrites the rows are [4,1,2], [4,0,2], and [4,3,3], totaling twenty-three.'),([2,[[0,0,5],[0,0,1]]],'The later row assignment overwrites the earlier one, leaving row zero sum two.')],
 [[n,q] for n,q in [(1,[[0,0,5]]),(1,[[1,0,7]]),(2,[[0,0,5]]),(2,[[1,1,3]]),(2,[[0,0,5],[0,0,1]]),(2,[[0,0,2],[1,0,3]]),(3,[[0,0,1],[1,2,2],[0,2,3],[1,0,4]]),(3,[[0,1,4],[1,1,5]]),(3,[[1,0,2],[1,2,8],[0,1,3]]),(4,[[0,0,1],[0,1,2],[0,2,3],[0,3,4]]),(4,[[1,0,1],[1,1,2],[1,2,3],[1,3,4]]),(3,[[0,0,0],[1,1,9]]),(2,[[1,0,8],[0,1,7],[1,0,1]]),(5,[[0,2,6],[1,4,3],[0,2,9]])]],
 MATRIX,[MATRIX.replace('reversed(queries)','queries'),MATRIX.replace('(n-len(used_columns))','n')],
 ['Processes earliest writes first and therefore ignores later overwrites.','Counts every newly fixed row cell even when some columns were already fixed by later queries.'],matrix_oracle,random_matrix,
 ['Process queries backward so the first unseen assignment is each row or column’s final one.','Track rows and columns already fixed by later queries.','A new row contributes value times the number of unfixed columns, and symmetrically for a column.','Every final cell is counted exactly when the later of its row and column assignments is encountered in reverse.'],'O(n+q)','O(n)',5),
2719:entry('count_integers_by_digit_sum',[('num1','str'),('num2','str'),('min_sum','int'),('max_sum','int')],'int',['strings','dynamic programming','digit DP'],
 ['Consider every integer in the inclusive decimal range num1 through num2.','Count values whose decimal digit sum lies between min_sum and max_sum inclusive.','Return the count modulo 1,000,000,007.'],
 [(['1','12',1,8],'Every value except nine has digit sum at most eight, so eleven values qualify.'),(['1','5',5,5],'Only the endpoint five has digit sum exactly five.')],
 [[a,b,l,h] for a,b,l,h in [('1','1',1,1),('1','5',5,5),('1','12',1,8),('10','20',1,2),('50','75',5,7),('99','101',1,18),('100','250',1,4),('1','999',1,27),('123','456',6,12),('500','500',5,5),('500','500',1,4),('1000','1200',1,3),('8','80',8,8),('321','1234',10,20)]],
 INTEGERS,[INTEGERS.replace('count(int(num1)-1)','count(int(num1))'),INTEGERS.replace('total>=min_sum','total>min_sum')],
 ['Subtracts the count through num1 itself, incorrectly excluding the lower endpoint.','Treats min_sum as an exclusive lower bound.'],integers_oracle,random_integers,
 ['Write a helper that counts qualifying integers from zero through one bound.','Digit DP state stores position, accumulated digit sum, and whether the prefix still equals the bound.','Subtract count(num1-1) from count(num2), reducing modulo the required constant.','Every bounded decimal representation follows exactly one DP digit path, and the terminal range check accepts precisely the desired digit sums.'],'O(digits*max_sum*10)','O(digits*max_sum)',8),
2729:entry('is_fascinating_number',[('n','int')],'bool',['math','strings','hash maps'],
 ['Concatenate the decimal representations of n, 2*n, and 3*n in that order.','The number is fascinating when the resulting text contains each digit 1 through 9 exactly once and contains no zero.','Return whether n is fascinating.'],
 [([192],'The concatenation 192384576 contains every nonzero digit exactly once.'),([100],'The concatenation 100200300 contains zeroes and repeats, so it is not fascinating.')],
 [[n] for n in [100,123,192,219,267,273,327,384,555,729,783,918,999,198]],
 FASCINATING,[FASCINATING.replace("len(text)==9 and ",''),FASCINATING.replace("set(text)==set('123456789')","len(set(text))==9")],
 ['Checks only which digits appear and can ignore an extra repeated digit in a ten-character concatenation.','Accepts nine distinct digits even when zero replaces one required nonzero digit.'],fascinating_oracle,random_fascinating,
 ['Build the three-part decimal concatenation.','The target multiset has exactly the nine characters 1 through 9.','Require length nine and set equality with those target digits.','At length nine, equality with a nine-element target set proves every required digit appears exactly once and zero is absent.'],'O(digits)','O(digits)',3),
2730:entry('longest_semi_repetitive_substring',[('s','str')],'int',['strings','sliding window','two pointers'],
 ['A substring is semi-repetitive when it contains at most one adjacent equal-digit pair.','Pairs may overlap; for example, 111 contains two equal adjacent pairs.','Return the maximum length of a semi-repetitive substring.'],
 [(['52233'],'The substring 5223 has only the pair 22 and length four; including the final 3 creates a second pair.'),(['5494'],'No adjacent digits match, so the entire string of length four qualifies.')],
 [[s] for s in ['0','00','000','01','11','111','52233','5494','11234','12344','122334','101010','99909','0010203']],
 SEMI_REPETITIVE,[SEMI_REPETITIVE.replace('left=previous_pair','left=previous_pair+1'),SEMI_REPETITIVE.replace('previous_pair=0','previous_pair=-1')],
 ['Moves one character too far right when discarding the older equal pair.','Uses a sentinel before the string, incorrectly shortening windows beginning with an equal pair.'],semi_repetitive_oracle,random_semi_repetitive,
 ['A valid sliding window may contain zero or one equal-adjacent boundary.','Remember the right index of the most recent equal pair.','When a new equal pair appears, move left just after the previous pair’s left character, then remember the new pair.','This removes exactly the oldest forbidden pair while retaining the longest suffix that contains at most the newest one.'],'O(n)','O(1)',5),
2731:entry('sum_robot_distances',[('nums','list[int]'),('s','str'),('d','int')],'int',['arrays','sorting','prefix sums'],
 ['Robot i starts at nums[i] and moves left or right according to s[i], one unit per second for d seconds.','Robots pass through one another equivalently when they collide.','After d seconds, return the sum of distances over every unordered robot pair modulo 1,000,000,007.'],
 [([[-2,0,2],'RLL',3],'Final pass-through positions are one, minus three, and minus one; pair distances total eight.'),([[1,0],'RL',2],'The final positions three and minus two are five units apart.')],
 [[a,s,d] for a,s,d in [([0,2],'RL',1),([1,0],'RL',2),([-2,0,2],'RLL',3),([0,10],'LR',5),([-5,5],'RL',0),([1,4,7],'RRR',10),([1,4,7],'LLL',10),([-10,-1,8],'LRL',4),([0,3,9,15],'RLRL',2),([-100,0,100],'RRL',50),([1,1000000000],'LR',1000000000),([-7,-3,2,11],'LLRR',6),([5,1,-4],'RLR',9),([-20,-10,0,10,20],'RLRLR',7)]],
 ROBOTS,[ROBOTS.replace('%MOD','',1),ROBOTS.replace("value+(d if direction=='R' else -d)",'value')],
 ['Omits the required modulo reduction on the accumulated answer.','Computes distances from starting positions and ignores robot movement.'],robots_oracle,random_robots,
 ['Collisions can be modeled as robots passing through because exchanging identities does not change the multiset of positions.','Compute every final position and sort them.','For sorted position x at index i, its distance to all earlier positions is i*x minus their prefix sum.','Sorting fixes every pair’s order, and the prefix formula counts each unordered pair exactly once.'],'O(n log n)','O(n)',5),
}
