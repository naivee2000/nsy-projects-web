"""First half of batch 55: ordinary array, string, and matrix functions."""
from collections import Counter
from fractions import Fraction
from itertools import permutations
from .import_batch_003 import entry as base_entry


EXTRA_BOUNDARIES = {
    "optimal_division": [[[10, 20, 30, 40]]],
    "reshape_matrix": [[[[5, 6], [7, 8]], 2, 2]],
}


def entry(*args, **kwargs):
    """Keep this batch's compact four-level lesson helper compatible with entry()."""
    values = list(args)
    if (len(values) >= 16 and isinstance(values[12], list) and len(values[12]) == 4
            and isinstance(values[13], str) and values[13].startswith("O(")
            and isinstance(values[14], str) and values[14].startswith("O(")
            and isinstance(values[15], int)):
        values.insert(13, values[12][3])
    spec = base_entry(*values, **kwargs)
    visible = {repr(arguments) for arguments, _ in spec["examples"]}
    unique = []
    for arguments in spec["boundaries"]:
        fingerprint = repr(arguments)
        if fingerprint not in visible:
            unique.append(arguments)
            visible.add(fingerprint)
    while len(unique) < 12:
        unique.extend(EXTRA_BOUNDARIES.get(spec["name"], []))
        if len(unique) < 12:
            raise ValueError(f"{spec['name']}: add a distinct hidden test")
    spec["boundaries"] = unique
    return spec


def attendance_oracle(args):
    absent=late=0
    for char in args[0]:
        absent += char == 'A'; late = late + 1 if char == 'L' else 0
        if absent >= 2 or late >= 3:return False
    return True

def division_oracle(args):
    nums=args[0]
    if len(nums)==1:return str(nums[0])
    if len(nums)==2:return f'{nums[0]}/{nums[1]}'
    return f'{nums[0]}/('+'/'.join(map(str,nums[1:]))+')'

def brick_oracle(args):
    wall=args[0]; width=sum(wall[0]);best=len(wall)
    for line in range(1,width):best=min(best,sum(line not in {sum(row[:i]) for i in range(1,len(row))} for row in wall))
    return best

def greater_oracle(args):
    digits=str(args[0]); candidates=[int(''.join(p)) for p in permutations(digits) if p[0]!='0' and int(''.join(p))>args[0]]
    answer=min(candidates,default=2**31)
    return answer if answer<2**31 else -1

def reverse_words_oracle(args):return ' '.join(''.join(reversed(word)) for word in args[0].split(' '))

def pairing_oracle(args):
    if not args:return 0
    nums=args[0]
    if not nums:return 0
    first=nums[0];return max(min(first,nums[i])+pairing_oracle([[v for j,v in enumerate(nums[1:],1) if j!=i]]) for i in range(1,len(nums)))

def reshape_oracle(args):
    mat,r,c=args;flat=[v for row in mat for v in row]
    return [flat[i*c:(i+1)*c] for i in range(r)] if len(flat)==r*c else mat

def inclusion_oracle(args):
    left,right=args; target=Counter(left)
    return any(Counter(right[i:i+len(left)])==target for i in range(max(0,len(right)-len(left)+1)))

def candy_oracle(args):return min(len(args[0])//2,len(set(args[0])))

def unsorted_oracle(args):
    nums=args[0]; ordered=sorted(nums); changed=[i for i,(a,b) in enumerate(zip(nums,ordered)) if a!=b]
    return 0 if not changed else changed[-1]-changed[0]+1

def random_attendance(rng):return [''.join(rng.choice('ALP') for _ in range(rng.randint(1,80)))]
def random_division(rng):return [[rng.randint(2,1000) for _ in range(rng.randint(1,8))]]
def random_wall(rng):
    width=rng.randint(2,15);wall=[]
    for _ in range(rng.randint(1,8)):
        cuts=sorted(rng.sample(range(1,width),rng.randint(0,min(5,width-1))));wall.append([b-a for a,b in zip([0]+cuts,cuts+[width])])
    return [wall]
def random_greater(rng):
    while True:
        value=rng.randint(1,9_999_999)
        if len(str(value))<=7:return [value]
def random_sentence(rng):return [' '.join(''.join(rng.choice('abcXYZ!') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,10)))]
def random_pairs(rng):return [[rng.randint(-20,20) for _ in range(2*rng.randint(1,5))]]
def random_reshape(rng):
    rows,cols=rng.randint(1,5),rng.randint(1,5);mat=[[rng.randint(-9,9) for _ in range(cols)] for _ in range(rows)]
    if rng.random()<.7:
        choices=[(r,len(mat)*cols//r) for r in range(1,len(mat)*cols+1) if len(mat)*cols%r==0];r,c=rng.choice(choices)
    else:r,c=rng.randint(1,8),rng.randint(1,8)
    return [mat,r,c]
def random_inclusion(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,8))),''.join(rng.choice('abc') for _ in range(rng.randint(1,25)))]
def random_candy(rng):return [[rng.randint(-20,20) for _ in range(2*rng.randint(1,30))]]
def random_unsorted(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(1,80))]]

ATTEND='''\
def eligible_attendance_record(s):
    absences=late_run=0
    for char in s:
        if char=='A':
            absences+=1
            if absences==2:return False
        if char=='L':
            late_run+=1
            if late_run==3:return False
        else:late_run=0
    return True
'''
DIVIDE='''\
def optimal_division(nums):
    if len(nums)==1:return str(nums[0])
    if len(nums)==2:return f"{nums[0]}/{nums[1]}"
    return f"{nums[0]}/({'/'.join(map(str,nums[1:]))})"
'''
BRICKS='''\
def least_crossed_bricks(wall):
    from collections import Counter
    edges=Counter()
    for row in wall:
        total=0
        for width in row[:-1]:
            total+=width;edges[total]+=1
    return len(wall)-max(edges.values(),default=0)
'''
GREATER='''\
def next_greater_same_digits(n):
    digits=list(str(n));pivot=len(digits)-2
    while pivot>=0 and digits[pivot]>=digits[pivot+1]:pivot-=1
    if pivot<0:return -1
    swap=len(digits)-1
    while digits[swap]<=digits[pivot]:swap-=1
    digits[pivot],digits[swap]=digits[swap],digits[pivot]
    digits[pivot+1:]=reversed(digits[pivot+1:])
    answer=int(''.join(digits))
    return answer if answer<2**31 else -1
'''
REVERSE='''\
def reverse_each_word(s):
    return ' '.join(word[::-1] for word in s.split(' '))
'''
PAIR='''\
def maximum_pair_min_sum(nums):
    nums=sorted(nums)
    return sum(nums[::2])
'''
RESHAPE='''\
def reshape_matrix(mat,r,c):
    if len(mat)*len(mat[0])!=r*c:return mat
    return [[mat[index//len(mat[0])][index%len(mat[0])] for index in range(row*c,(row+1)*c)] for row in range(r)]
'''
INCLUSION='''\
def contains_permutation(s1,s2):
    if len(s1)>len(s2):return False
    from collections import Counter
    need=Counter(s1);window=Counter(s2[:len(s1)])
    if window==need:return True
    for right in range(len(s1),len(s2)):
        window[s2[right]]+=1;left=s2[right-len(s1)];window[left]-=1
        if window[left]==0:del window[left]
        if window==need:return True
    return False
'''
CANDY='''\
def maximum_candy_types(candy_type):
    return min(len(candy_type)//2,len(set(candy_type)))
'''
UNSORTED='''\
def shortest_unsorted_window(nums):
    low=float('inf');high=float('-inf')
    maximum=float('-inf')
    for value in nums:
        if value<maximum:low=min(low,value)
        maximum=max(maximum,value)
    minimum=float('inf')
    for value in reversed(nums):
        if value>minimum:high=max(high,value)
        minimum=min(minimum,value)
    if low==float('inf'):return 0
    return next(i for i,v in enumerate(nums) if v>low) and 0
'''

# The final reference for 581 is written separately to keep the boundary search explicit.
UNSORTED='''\
def shortest_unsorted_window(nums):
    ordered=sorted(nums)
    left=0
    while left<len(nums) and nums[left]==ordered[left]:left+=1
    right=len(nums)-1
    while right>=left and nums[right]==ordered[right]:right-=1
    return right-left+1
'''

def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]

BATCH={
551:entry('eligible_attendance_record',[('s','str')],'bool',['strings','state'],['1 <= len(s) <= 1,000; s contains only P, A, and L.','Accept only fewer than two total absences and no run of three late days.'],
 [(['PPALLP'],'One absence and no late run reaches three, so it is eligible.'),(['PPALLL'],'The final three L values are consecutive, so return false.')],
 [[x] for x in ('P','A','L','AA','LL','LLL','ALL','LAL','PALPAL','APLLP','PPALLP','LLALL','ALALAL','PPPAAA')],ATTEND,[ATTEND.replace("if absences==2:return False","if absences>2:return False"),ATTEND.replace("if late_run==3:return False","if late_run>3:return False")],['Allows two absences.','Allows exactly three consecutive late days.'],attendance_oracle,random_attendance,lesson('Track two independent rules.','Count A and reset a late streak on non-L.','Scan characters; reject at the second A or third consecutive L.','The rules are local except for total absences. One pass maintains both counters.'),'O(n)','O(1)',3),
553:entry('optimal_division',[('nums','list[int]')],'str',['math','greedy','strings'],['1 <= len(nums) <= 10; 2 <= nums[i] <= 1,000.','Use every number in order with division and return the unique maximum-value expression without redundant parentheses.'],
 [([[1000,100,10,2]],'Put every denominator after the first inside one pair: 1000/(100/10/2).'),([[2,3,4]],'2/(3/4) is larger than every left-associated alternative.')],
 [[x] for x in ([2],[2,3],[3,2],[2,3,4],[5,2,3,4],[1000,2,2],[2,2,2,2],[7,8,9],[9,2,3,5,7],[100,100,100],[999,2,999],[2,1000,2])],DIVIDE,[DIVIDE.replace("if len(nums)==2:return f\"{nums[0]}/{nums[1]}\"","if len(nums)>=2:return '/'.join(map(str,nums))"),DIVIDE.replace("return f\"{nums[0]}/({'/'.join(map(str,nums[1:]))})\"","return '/'.join(map(str,nums))")],['Never groups all denominator divisions together.','Uses left association for three or more numbers.'],division_oracle,random_division,lesson('Division by a quotient multiplies by its later factors.','Only the first value stays outside; all later values form one denominator chain.','Handle one/two values, otherwise format first/(rest joined by /).','For positive values, moving a later divisor into the denominator increases rather than decreases the result.'),'O(n)','O(n)',5),
554:entry('least_crossed_bricks',[('wall','list[list[int]]')],'int',['arrays','hash-maps'],['1 <= rows <= 10,000; total brick count <= 20,000.','Each row has equal total width. A line through an internal edge crosses no brick; it may not use either outer wall edge.'],
 [([[[1,2,2,1],[3,1,2],[1,3,2],[2,4],[3,1,2],[1,3,1,1]]],'Four rows share an internal edge, so six minus four equals two crossed bricks.'),([[[1],[1],[1]]],'There are no internal edges to use, so every one of three bricks is crossed.')],
 [[x] for x in ([[1]],[[1],[1]],[[1,1],[2]],[[2,1],[1,2]],[[1,2,1],[2,2]],[[3,1],[1,3]],[[1,1,1,1],[2,2],[3,1]],[[5],[5]],[[1,4],[2,3],[3,2]],[[2,2,2],[1,3,2],[4,2]],[[1,2,3],[3,3],[2,1,3]],[[7,1],[4,4]])],BRICKS,[BRICKS.replace('row[:-1]','row'),BRICKS.replace('len(wall)-max(edges.values(),default=0)','max(edges.values(),default=0)')],['Counts the outer right edge as a safe cut.','Returns shared edges instead of crossed bricks.'],brick_oracle,random_wall,lesson('Safe cuts occur at cumulative internal widths.','Choose the internal edge shared by the most rows.','Count each row prefix except its full width; return rows minus best count.','The line crosses exactly rows that lack its position as an internal brick boundary.'),'O(total bricks)','O(total bricks)',5),
556:entry('next_greater_same_digits',[('n','int')],'int',['strings','two-pointers'],['1 <= n <= 2^31 - 1.','Return the smallest larger positive 32-bit integer using exactly the same decimal digits, or -1.'],
 [([12],'Swap the ascending tail 1,2 to get the next arrangement 21.'),([21],'Digits are fully descending, so no larger arrangement exists.')],
 [[x] for x in (1,9,10,11,12,20,102,120,123,132,199,230241,12443322,1999999999,2147483476)],GREATER,[GREATER.replace("digits[pivot+1:]=reversed(digits[pivot+1:])","digits[pivot+1:]=sorted(digits[pivot+1:],reverse=True)"),GREATER.replace("return answer if answer<2**31 else -1","return answer")],['Leaves the suffix descending after the swap.','Returns a valid digit permutation that exceeds 32-bit signed range.'],greater_oracle,random_greater,lesson('Find the rightmost position that can increase.','Swap it with the smallest larger suffix digit, then make the suffix smallest.','Scan down for pivot and swap; reverse the decreasing suffix; check 32-bit limit.','The suffix was decreasing, so reversal produces the minimum suffix after the smallest possible pivot increase.'),'O(digits)','O(digits)',5),
557:entry('reverse_each_word',[('s','str')],'str',['strings','two-pointers'],['1 <= len(s) <= 50,000; printable ASCII; words are separated by one space with no leading/trailing spaces.','Reverse characters inside each word while preserving word order and spaces.'],
 [(["Let's take LeetCode contest"],"Reverse each word separately: s'teL ekat edoCteeL tsetnoc."),(['Mr Ding'],'The two word positions stay Mr, Ding; their characters become rM, gniD.')],
 [[x] for x in ('a','ab','a b','hello world','abc def ghi','A! b?','same','x y z','123 abc','aBc DeF','word '*0+'word','longword short')],REVERSE,[REVERSE.replace("word[::-1]","word"),REVERSE.replace("word[::-1] for word in s.split(' ')","word for word in reversed(s.split(' '))")],['Leaves every word unchanged.','Reverses the order of words instead of their characters.'],reverse_words_oracle,random_sentence,lesson('Word positions are fixed; only each word reverses.','Split at the known single spaces and reverse each piece.','Map reversal over words and join with one space.','Every character remains in its original word, so no global reversal or word-order change is allowed.'),'O(n)','O(n)',3),
561:entry('maximum_pair_min_sum',[('nums','list[int]')],'int',['arrays','greedy','sorting'],['2 <= len(nums) <= 20,000; length is even; -10,000 <= nums[i] <= 10,000.','Partition into pairs to maximize the sum of the smaller value in every pair.'],
 [([[1,4,3,2]],'Sorting gives 1,2,3,4; pair adjacent values and take 1+3=4.'),([[6,2,6,5,1,2]],'Sorted adjacent pairs contribute 1,2,6 for a total of 9.')],
 [[x] for x in ([0,0],[-1,1],[1,2],[2,1],[1,1,1,1],[-3,-2,-1,0],[1,2,3,4,5,6],[10,9,8,7],[1,100,2,99],[0,5,5,10],[-10,10,-9,9],[4,4,4,4,4,4])],PAIR,[PAIR.replace('sum(nums[::2])','sum(nums[1::2])'),PAIR.replace('nums=sorted(nums)','nums=list(nums)')],['Adds the larger member of every sorted pair.','Pairs input neighbors without sorting.'],pairing_oracle,random_pairs,lesson('Large values should not be wasted as the partner of a small value.','Sort and pair adjacent values.','Sort nums; sum indices 0,2,4,...','An exchange argument removes crossed pairings without lowering the sum of pair minima.'),'O(n log n)','O(n)',3),
566:entry('reshape_matrix',[('mat','list[list[int]]'),('r','int'),('c','int')],'list[list[int]]',['matrices','simulation'],['1 <= input rows, columns <= 100; -1,000 <= values <= 1,000; 1 <= r,c <= 300.','If r*c differs from the input cell count, return the original matrix; otherwise preserve row-traversal order in r rows and c columns.'],
 [([[[1,2],[3,4]],1,4],'Flattening row order gives 1,2,3,4 in one row.'),([[[1,2],[3,4]],2,4],'Four cells cannot fill eight positions, so return the original shape.')],
 [[m,r,c] for m,r,c in (([[1]],1,1),([[1]],1,2),([[1,2]],2,1),([[1,2],[3,4]],4,1),([[1,2],[3,4]],1,4),([[1,2,3]],3,1),([[-1,0],[1,2]],2,2),([[1,2],[3,4],[5,6]],2,3),([[1,2,3],[4,5,6]],3,2),([[1,2],[3,4]],3,3),([[7,8,9,10]],2,2),([[1],[2],[3],[4]],1,4))],RESHAPE,[RESHAPE.replace('if len(mat)*len(mat[0])!=r*c:return mat','if len(mat)*len(mat[0])!=r*c:return []'),RESHAPE.replace('range(row*c,(row+1)*c)','range(row*c,(row+1)*c-1)')],['Returns an empty matrix instead of the required original on an impossible reshape.','Drops the final cell of each output row.'],reshape_oracle,random_reshape,lesson('Only the shape changes; flattened row order does not.','First compare cell counts, then map each flat index to old and new coordinates.','Return original if counts differ; fill output from flat index i.','Both matrices represent the same linear row-major sequence when their total cell counts agree.'),'O(r*c)','O(r*c)',3),
567:entry('contains_permutation',[('s1','str'),('s2','str')],'bool',['strings','sliding-window','hash-maps'],['1 <= len(s1),len(s2) <= 10,000; lowercase English letters.','Return true exactly when some contiguous substring of s2 is a permutation of s1.'],
 [(['ab','eidbaooo'],'The window ba has the same two character counts as ab.'),(['ab','eidboaoo'],'No contiguous length-two window has both a and b.')],
 [[a,b] for a,b in (('a','a'),('a','b'),('ab','ba'),('ab','ab'),('ab','aab'),('abc','cba'),('abc','ab'),('aab','aba'),('aab','abb'),('abc','cabx'),('abcd','dcba'),('aa','aaaa'),('abc','bbbccc'))],INCLUSION,[INCLUSION.replace('if len(s1)>len(s2):return False','if len(s1)>len(s2):return True'),INCLUSION.replace('window==need','set(window)==set(need)')],['Treats a longer pattern as automatically present.','Compares only character sets and ignores repeated counts.'],inclusion_oracle,random_inclusion,lesson('A permutation preserves a multiset, not order.','Maintain counts for a fixed-size window of len(s1).','Initialize first window; slide one character out and one in; compare counts.','Every candidate substring has exactly the pattern length, so matching frequency maps is necessary and sufficient.'),'O(len(s1)+len(s2))','O(alphabet)',5),
575:entry('maximum_candy_types',[('candy_type','list[int]')],'int',['arrays','hash-maps'],['2 <= len(candy_type) <= 10,000; length is even; values are in -100,000..100,000.','Choose exactly half the candies while maximizing the number of distinct types.'],
 [([[1,1,2,2,3,3]],'There are three types and three allowed candies, so take one of each.'),([[6,6,6,6]],'Two candies may be eaten, but only one distinct type exists.')],
 [[x] for x in ([1,1],[1,2],[1,1,2,2],[1,1,2,3],[0,0,0,0],[-1,-1,2,2],[-1,0,1,2],[1,2,3,4,5,6],[1,1,1,2,2,3],[9,8,7,6],[1,2,2,3,3,4],[5,5,5,5,6,6])],CANDY,[CANDY.replace('min(len(candy_type)//2,len(set(candy_type)))','len(set(candy_type))'),CANDY.replace('len(set(candy_type))','1')],['Forgets the half-candy limit.','Always claims one type.'],candy_oracle,random_candy,lesson('Distinct types cannot exceed candies selected.','The answer is bounded by both half the list and the number of types.','Return min(n/2, size of set).','If enough types exist, choose different ones; otherwise choose every available type once.'),'O(n)','O(n)',3),
581:entry('shortest_unsorted_window',[('nums','list[int]')],'int',['arrays','sorting','two-pointers'],['1 <= len(nums) <= 10,000; -100,000 <= nums[i] <= 100,000.','Return the shortest continuous window which, when sorted nondecreasingly, makes all nums sorted; return zero if already sorted.'],
 [([[2,6,4,8,10,9,15]],'Only indices 1 through 5 must be sorted, so return length 5.'),([[1,2,3,4]],'The entire array is already nondecreasing, so no window is needed.')],
 [[x] for x in ([1],[2,1],[1,2],[1,1],[1,3,2,2,2],[2,2,1],[1,2,4,3,5],[1,2,3,3,3],[3,2,1],[1,5,3,4,2,6],[0,-1,0],[1,2,5,3,4],[2,6,4,8,10,9,15],[1,1,1,0,1])],UNSORTED,[UNSORTED.replace('ordered=sorted(nums)','ordered=list(nums)'),UNSORTED.replace('return right-left+1','return max(0,right-left)')],['Compares the array to itself rather than a sorted baseline.','Has an off-by-one window length.'],unsorted_oracle,random_unsorted,lesson('The unchanged prefix and suffix already match sorted positions.','Compare to a sorted copy from both ends until the first mismatches.','Advance left while equal; retreat right while equal; return right-left+1.','Any changed sorted position lies inside the minimum repair interval, and sorting that interval restores global order.'),'O(n log n)','O(n)',5),
}
