"""Good captions, target multiples, parity frequencies, diagonals, and divisibility assignment."""
from itertools import product
from math import gcd

from .import_batch_055 import entry


def caption_oracle(args):
    caption=args[0];n=len(caption)
    if n<3:return ''
    partitions=[]
    def divide(remaining,current):
        if remaining==0:partitions.append(current[:]);return
        for length in range(3,remaining+1):divide(remaining-length,current+[length])
    divide(n,[]);best_cost=10**30;best=''
    for lengths in partitions:
        for letters in product(range(26),repeat=len(lengths)):
            if any(letters[i]==letters[i-1] for i in range(1,len(letters))):continue
            candidate=''.join(chr(97+letter)*length for letter,length in zip(letters,lengths))
            cost=sum(abs(ord(left)-ord(right)) for left,right in zip(caption,candidate))
            if cost<best_cost or (cost==best_cost and candidate<best):best_cost,best=cost,candidate
    return best


def random_caption(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,9)))]


def multiples_oracle(args):
    nums,target=args;m=len(target);lcm=[1]*(1<<m)
    for mask in range(1,1<<m):
        bit=(mask&-mask).bit_length()-1;prior=mask^(1<<bit);lcm[mask]=lcm[prior]*target[bit]//gcd(lcm[prior],target[bit])
    answer=10**30
    for choices in product(range(1<<m),repeat=len(nums)):
        covered=cost=0
        for value,mask in zip(nums,choices):covered|=mask;cost+=(-value)%lcm[mask]
        if covered==(1<<m)-1:answer=min(answer,cost)
    return answer


def random_multiples(rng):
    return [[rng.randint(1,15) for _ in range(rng.randint(1,4))],[rng.randint(1,8) for _ in range(rng.randint(1,3))]]


def difference_oracle(args):
    text,k=args;answer=-10**9
    for left in range(len(text)):
        counts=[0]*5
        for right in range(left,len(text)):
            counts[int(text[right])]+=1
            if right-left+1>=k:
                for odd in range(5):
                    for even in range(5):
                        if odd!=even and counts[odd]%2==1 and counts[even]>0 and counts[even]%2==0:answer=max(answer,counts[odd]-counts[even])
    return answer


def random_difference(rng):
    while True:
        n=rng.randint(4,12);text=''.join(str(rng.randrange(5)) for _ in range(n));k=rng.randint(1,n)
        if difference_oracle([text,k])>-10**9:return [text,k]


def diagonal_oracle(args):
    grid=args[0];n=len(grid);result=[[0]*n for _ in range(n)];groups={}
    for row in range(n):
        for column in range(n):groups.setdefault(row-column,[]).append(grid[row][column])
    for key,values in groups.items():values.sort(reverse=key>=0)
    used={key:0 for key in groups}
    for row in range(n):
        for column in range(n):
            key=row-column;result[row][column]=groups[key][used[key]];used[key]+=1
    return result


def random_diagonal(rng):
    n=rng.randint(1,6);return [[[rng.randint(-15,15) for _ in range(n)] for _ in range(n)]]


def assignment_oracle(args):
    groups,elements=args
    return [next((index for index,value in enumerate(elements) if group%value==0),-1) for group in groups]


def random_assignment(rng):
    return [[rng.randint(1,30) for _ in range(rng.randint(1,12))],[rng.randint(1,20) for _ in range(rng.randint(1,10))]]


CAPTION='''def minimum_cost_good_caption(caption):
    n=len(caption)
    if n<3:return ''
    infinity=10**30;states=78;following=[infinity]*states
    for letter in range(26):following[letter*3+2]=0
    decisions=[None]*n;first_letter=0
    for index in range(n-1,-1,-1):
        value=ord(caption[index])-97;start=[abs(value-letter)+following[letter*3] for letter in range(26)];choice=bytearray(states);current=[infinity]*states
        for previous in range(26):
            base=previous*3;change=abs(value-previous)
            current[base]=change+following[base+1];choice[base]=previous
            current[base+1]=change+following[base+2];choice[base+1]=previous
            candidates=[(start[letter],letter) for letter in range(26) if letter!=previous]
            switch_cost,switch_letter=min(candidates)
            stay=change+following[base+2]
            if (stay,previous)<=(switch_cost,switch_letter):current[base+2]=stay;choice[base+2]=previous
            else:current[base+2]=switch_cost;choice[base+2]=switch_letter
        if index==0:_,first_letter=min((cost,letter) for letter,cost in enumerate(start))
        decisions[index]=choice;following=current
    letter=first_letter
    answer=[chr(97+letter)];run=1
    for index in range(1,n):
        selected=decisions[index][letter*3+run-1]
        if selected==letter:run=min(3,run+1)
        else:letter=selected;run=1
        answer.append(chr(97+letter))
    return ''.join(answer)
'''

MULTIPLES='''def minimum_target_multiple_increments(nums,target):
    from math import gcd
    size=1<<len(target);lcm=[1]*size
    for mask in range(1,size):
        bit=(mask&-mask).bit_length()-1;prior=mask^(1<<bit);lcm[mask]=lcm[prior]*target[bit]//gcd(lcm[prior],target[bit])
    infinity=10**30;dp=[0]+[infinity]*(size-1)
    for value in nums:
        following=dp[:]
        for covered in range(size):
            for gained in range(1,size):following[covered|gained]=min(following[covered|gained],dp[covered]+(-value)%lcm[gained])
        dp=following
    return dp[-1]
'''

DIFFERENCE='''def maximum_odd_even_frequency_difference(s,k):
    infinity=10**9;answer=-infinity
    for odd in range(5):
        for even in range(5):
            if odd==even:continue
            current_odd=current_even=prefix_odd=prefix_even=0;best=[[infinity,infinity],[infinity,infinity]];left=-1
            for right,char in enumerate(s):
                value=int(char);current_odd+=value==odd;current_even+=value==even
                while right-left>=k and current_even-prefix_even>=2:
                    parity_odd=prefix_odd&1;parity_even=prefix_even&1;best[parity_odd][parity_even]=min(best[parity_odd][parity_even],prefix_odd-prefix_even)
                    left+=1;value=int(s[left]);prefix_odd+=value==odd;prefix_even+=value==even
                prior=best[(current_odd&1)^1][current_even&1]
                if prior<infinity:answer=max(answer,current_odd-current_even-prior)
    return answer
'''

DIAGONALS='''def sort_matrix_diagonals(grid):
    n=len(grid)
    for start_row in range(n):
        values=[];row=start_row;column=0
        while row<n and column<n:values.append(grid[row][column]);row+=1;column+=1
        values.sort();row=start_row;column=0
        while row<n and column<n:grid[row][column]=values.pop();row+=1;column+=1
    for start_column in range(1,n):
        values=[];row=0;column=start_column
        while row<n and column<n:values.append(grid[row][column]);row+=1;column+=1
        values.sort(reverse=True);row=0;column=start_column
        while row<n and column<n:grid[row][column]=values.pop();row+=1;column+=1
    return grid
'''

ASSIGN='''def assign_divisible_element_indices(groups,elements):
    maximum=max(groups);assigned=[-1]*(maximum+1)
    for index,value in enumerate(elements):
        if value>maximum or assigned[value]!=-1:continue
        for multiple in range(value,maximum+1,value):
            if assigned[multiple]==-1:assigned[multiple]=index
    return [assigned[group] for group in groups]
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


CAPTION_CASES=[[text] for text in ['cdcd','aca','ab','aaa','zzz','abc','abcd','azaz','aabbb','fedcba','aaabbb','abccba','leetcode','xyzxyz']]
MULTIPLE_CASES=[[nums,target] for nums,target in [([1,2,3],[4]),([8,4],[10,5]),([1],[1]),([1],[6]),([2,3],[2,3]),([5],[2,3]),([1,1],[2,3]),([7,11],[4,6]),([10,20],[5,10]),([3,9,10],[6,8]),([1,5,9],[2,4,8]),([6,10],[4,9]),([2,7,13],[3,5,7]),([100,101],[6,10])]]
DIFFERENCE_CASES=[[text,k] for text,k in [('12233',4),('1122211',3),('00112',4),('00011',2),('01234',3),('111122',5),('121212',2),('4440004',4),('230032',3),('0101010',5),('3332200',4),('123401234',6),('222211110',7),('40404044',3)]]
DIAGONAL_CASES=[[[row[:] for row in grid]] for grid in [[[1,7,3],[9,8,2],[4,5,6]],[[5]],[[2,1],[4,3]],[[1,2],[3,4]],[[9,8,7],[6,5,4],[3,2,1]],[[1,1,1],[1,1,1],[1,1,1]],[[-1,3],[2,-4]],[[5,2,9],[8,1,4],[7,6,3]],[[4,3,2,1],[8,7,6,5],[12,11,10,9],[16,15,14,13]],[[0,-1,2],[-3,4,-5],[6,-7,8]],[[2,9,1],[4,7,3],[6,5,8]],[[10,2,3],[4,50,6],[7,8,90]],[[3,1,4,1],[5,9,2,6],[5,3,5,8],[9,7,9,3]],[[8,6,7],[5,3,0],[9,4,2]]]]
ASSIGN_CASES=[[groups,elements] for groups,elements in [([8,4,3,2,4],[4,2]),([2,3,5,7],[5,3,3]),([1],[1]),([5],[2]),([6,10,15],[2,3,5]),([12,18],[6,3]),([4,8],[8,4]),([9,27,10],[3,5]),([7,14,21],[7,2]),([16,25,36],[4,5,6]),([2,4,6],[1]),([30,42,70],[7,5,3]),([11,22,33],[2,11]),([100,50,25],[10,5])]]


BATCH={
3441:entry('minimum_cost_good_caption',[('caption','str')],'str',['strings','dynamic programming'],['caption has 1–50,000 lowercase letters.','One operation changes a letter one alphabet step; its total transformation cost is the absolute alphabet distance.','Every run in the result must contain at least three equal letters; return the lexicographically smallest minimum-cost result, or an empty string if impossible.'],[(['cdcd'],'Changing both d letters to c produces good caption cccc at cost two.'),(['ab'],'A length-two string cannot contain a run of at least three, so return an empty string.')],CAPTION_CASES,CAPTION,[CAPTION.replace('following[letter*3+2]=0','following[letter*3+1]=0;following[letter*3+2]=0'),CAPTION.replace("if (stay,previous)<=(switch_cost,switch_letter)","if stay<=switch_cost")],['Allows a final run of only two characters.','Breaks equal-cost choices by staying even when switching produces a lexicographically smaller caption.'],caption_oracle,random_caption,lesson('Only the previous output letter and its run length capped at three determine which next letters are legal.','Compute minimum suffix costs backward for 26 letters and three run states, storing one byte-sized choice per state.','Continue forced runs of length one or two; from a mature run compare staying with switching to any other letter, breaking ties by the next letter.','The state captures the complete validity constraint, and choosing the smallest next letter among optimal transitions yields the lexicographically smallest global optimum.'),'O(26^2*n)','O(26*n)',8),
3444:entry('minimum_target_multiple_increments',[('nums','list[int]'),('target','list[int]')],'int',['arrays','bitmask dynamic programming','number theory'],['nums has up to 50,000 positive integers and target has at most four positive integers.','Incrementing one nums element by one costs one operation.','Every target value must divide at least one resulting nums value; one nums value may cover several targets.'],[([[1,2,3],[4]],'Increment three once to four, giving a multiple of the sole target.'),([[5],[2,3]],'Increment five once to six, whose divisibility by both targets covers them together.')],MULTIPLE_CASES,MULTIPLES,[MULTIPLES.replace('//gcd(lcm[prior],target[bit])','//1'),MULTIPLES.replace('for gained in range(1,size):','for gained in [1<<bit for bit in range(len(target))]:')],['Uses the product instead of the least common multiple for combined targets and can overpay.','Lets each nums element cover only one target and misses cheaper shared multiples.'],multiples_oracle,random_multiples,lesson('One adjusted number covers a subset of targets exactly when it reaches a multiple of their least common multiple.','Precompute each subset LCM and update a bitmask DP once per nums value.','For every covered mask and gained subset, add the distance to the next multiple and relax their union.','Every assignment of target requirements to nums elements corresponds to one sequence of mask transitions, so the minimum transition cost is optimal.'),'O(n*3^t)','O(2^t)',8),
3445:entry('maximum_odd_even_frequency_difference',[('s','str'),('k','int')],'int',['strings','prefix sums','sliding window'],['s has 3–30,000 digits from 0 through 4 and k is at least one.','Choose a substring of length at least k and two distinct digits: the first has odd frequency and the second has positive even frequency.','Maximize first frequency minus second frequency.'],[(['12233',4],'Among qualifying substrings and digit pairs, the largest valid difference is negative one.'),(['00112',4],'The full string has digit two once and each of zero and one twice, producing difference negative one.')],DIFFERENCE_CASES,DIFFERENCE,[DIFFERENCE.replace('current_even-prefix_even>=2','current_even-prefix_even>=0'),DIFFERENCE.replace('(current_odd&1)^1','current_odd&1')],['Allows the even-frequency digit to occur zero times.','Matches an even first-digit frequency instead of the required odd frequency.'],difference_oracle,random_difference,lesson('For a fixed ordered digit pair, prefix-count parities identify valid odd/even frequency differences.','Scan right endpoints while retaining the smallest eligible prefix difference for each parity pair.','Release prefixes only after the length bound and two occurrences of the even digit; query the opposite odd parity and same even parity.','Subtracting the minimum compatible prefix maximizes the frequency difference, and enumerating 20 ordered pairs covers every choice.'),'O(25*n)','O(1)',8),
3446:entry('sort_matrix_diagonals',[('grid','list[list[int]]')],'list[list[int]]',['matrices','sorting'],['grid is a nonempty n by n integer matrix with n <= 10.','Diagonals beginning in the first column, including the main diagonal, must be non-increasing from top-left to bottom-right.','Diagonals beginning in the top row to the right of the main diagonal must be non-decreasing in that direction.'],[([[[1,7,3],[9,8,2],[4,5,6]]],'The main and lower diagonals descend while upper diagonals ascend, producing [[8,2,3],[9,6,7],[4,5,1]].'),([[[2,1],[4,3]]],'Sorting the main diagonal downward gives [[3,1],[4,2]].')],DIAGONAL_CASES,DIAGONALS,[DIAGONALS.replace('values.sort(reverse=True)','values.sort()'),DIAGONALS.replace('values.sort();row=start_row','values.sort(reverse=True);row=start_row')],['Sorts upper-right diagonals in the descending direction.','Sorts lower-left diagonals in the ascending direction.'],diagonal_oracle,random_diagonal,lesson('Every cell belongs to exactly one diagonal identified by row minus column.','Process first-column starts and top-row starts separately because their required order differs.','Collect a diagonal, sort it, and write it back in traversal order with descending values below-left and ascending values above-right.','Independent diagonal sorting cannot interfere because diagonals partition the matrix.'),'O(n^2 log n)','O(n)',6),
3447:entry('assign_divisible_element_indices',[('groups','list[int]'),('elements','list[int]')],'list[int]',['arrays','sieve','divisibility'],['groups and elements contain positive integers; groups has up to 100,000 entries and values up to 100,000.','For each group value, choose an element that divides it.','Return the smallest qualifying element index for every group, or -1 when none divides it; elements may be reused.'],[([[8,4,3,2,4],[4,2]],'Element index zero divides groups eight and four, while index one is the first divisor of two; three has none.'),([[2,3,5,7],[5,3,3]],'The first threes divisor is index one, five uses index zero, and two and seven have none.')],ASSIGN_CASES,ASSIGN,[ASSIGN.replace('if assigned[multiple]==-1:assigned[multiple]=index','assigned[multiple]=index'),ASSIGN.replace('range(value,maximum+1,value)','range(1,maximum//value+1)')],['Overwrites earlier valid indices with later elements.','Marks quotients rather than multiples and reverses the divisibility relationship.'],assignment_oracle,random_assignment,lesson('An element value qualifies for every group value among its multiples.','Visit elements by index and sieve their multiples, assigning only previously unassigned group values.','For each distinct useful element, walk value, 2*value, and so on through the maximum group; store its index only once.','Indices are processed ascending, so the first write to a group is exactly its smallest qualifying element index.'),'O(max_group log max_group+m)','O(max_group)',6),
}
