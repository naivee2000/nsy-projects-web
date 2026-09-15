"""Dominant substrings, recency ordering, palindromic grids, and odd subsequences."""
from itertools import product
from .import_batch_055 import entry

def dominant_oracle(args):
    s=args[0];answer=0
    for left in range(len(s)):
        zeros=ones=0
        for right in range(left,len(s)):
            zeros+=s[right]=='0';ones+=s[right]=='1';answer+=ones>=zeros*zeros
    return answer
def random_dominant(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,20)))]

def alt_oracle(args):
    windows,queries=args;order=windows[:]
    for window in queries:order.remove(window);order.insert(0,window)
    return order
def random_alt(rng):
    n=rng.randint(1,14);windows=list(range(1,n+1));rng.shuffle(windows)
    return [windows,[rng.randint(1,n) for _ in range(rng.randint(1,20))]]

def palindrome_one_oracle(args):
    grid=args[0];rows=sum(grid[r][c]!=grid[r][-1-c] for r in range(len(grid)) for c in range(len(grid[0])//2))
    columns=sum(grid[r][c]!=grid[-1-r][c] for r in range(len(grid)//2) for c in range(len(grid[0])))
    return min(rows,columns)
def random_grid(rng):
    m=rng.randint(1,4);n=rng.randint(1,4);return [[[rng.randrange(2) for _ in range(n)] for _ in range(m)]]

def palindrome_two_oracle(args):
    grid=args[0];m=len(grid);n=len(grid[0]);seen=set();groups=[]
    for r in range(m):
        for c in range(n):
            group=frozenset(((r,c),(m-1-r,c),(r,n-1-c),(m-1-r,n-1-c)))
            if group not in seen:seen.add(group);groups.append(group)
    answer=m*n+1
    for values in product((0,1),repeat=len(groups)):
        if sum(value*len(group) for value,group in zip(values,groups))%4:continue
        answer=min(answer,sum(grid[r][c]!=value for value,group in zip(values,groups) for r,c in group))
    return answer

def odd_oracle(args):
    nums=args[0];return sum(sum(nums[i] for i in range(len(nums)) if mask>>i&1)%2 for mask in range(1,1<<len(nums)))
def random_odd(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,14))]]

DOMINANT='''def count_dominant_one_substrings(s):
    n=len(s);zeros=[-1]+[i for i,char in enumerate(s) if char=='0']+[n];answer=0
    for left,right in zip(zeros,zeros[1:]):
        run=right-left-1;answer+=run*(run+1)//2
    count=len(zeros)-2
    for amount in range(1,count+1):
        required_length=amount*amount+amount
        if required_length>n:break
        for first in range(1,count-amount+2):
            last=first+amount-1;base=zeros[last]-zeros[first]+1
            left_choices=zeros[first]-zeros[first-1];right_choices=zeros[last+1]-zeros[last]
            needed=max(0,required_length-base)
            full=min(left_choices,max(0,needed-right_choices));stop=min(left_choices,needed)
            terms=stop-full;invalid=full*right_choices+terms*needed-(full+stop-1)*terms//2
            answer+=left_choices*right_choices-invalid
    return answer
'''
ALT='''def simulate_alt_tab(windows,queries):
    seen=set();front=[]
    for window in reversed(queries):
        if window not in seen:seen.add(window);front.append(window)
    return front+[window for window in windows if window not in seen]
'''
PAL_ONE='''def minimum_palindromic_grid_flips(grid):
    m=len(grid);n=len(grid[0])
    rows=sum(grid[r][c]!=grid[r][n-1-c] for r in range(m) for c in range(n//2))
    columns=sum(grid[r][c]!=grid[m-1-r][c] for r in range(m//2) for c in range(n))
    return min(rows,columns)
'''
PAL_TWO='''def minimum_fully_palindromic_grid_flips(grid):
    m=len(grid);n=len(grid[0]);answer=0
    for r in range(m//2):
        for c in range(n//2):
            ones=grid[r][c]+grid[r][n-1-c]+grid[m-1-r][c]+grid[m-1-r][n-1-c]
            answer+=min(ones,4-ones)
    mismatched=paired_ones=0
    if m%2:
        r=m//2
        for c in range(n//2):
            if grid[r][c]!=grid[r][n-1-c]:mismatched+=1
            elif grid[r][c]:paired_ones+=2
    if n%2:
        c=n//2
        for r in range(m//2):
            if grid[r][c]!=grid[m-1-r][c]:mismatched+=1
            elif grid[r][c]:paired_ones+=2
    answer+=mismatched if mismatched else paired_ones%4
    if m%2 and n%2:answer+=grid[m//2][n//2]
    return answer
'''
ODD='''def count_odd_sum_subsequences(nums):
    modulo=10**9+7;even=odd=0
    for number in nums:
        if number%2:even,odd=(even+odd)%modulo,(odd+even+1)%modulo
        else:even,odd=(2*even+1)%modulo,(2*odd)%modulo
    return odd
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3234:entry('count_dominant_one_substrings',[('s','str')],'int',['strings','enumeration','prefix sums'],['1≤len(s)≤40,000 and s contains only 0 and 1.','A nonempty substring is dominant when its one count is at least the square of its zero count.','Return the number of dominant substrings.'],[(['00011'],'The dominant substrings are the two single ones, 11, 01, and 011, giving five.'),(['101101'],'Sixteen of the twenty-one substrings satisfy ones≥zeros².')],[[s] for s in ['0','1','00','01','10','11','00011','101101','1111','0000','0101','10001','110011','0010110']],DOMINANT,[DOMINANT.replace('required_length=amount*amount+amount','required_length=amount*amount'),DOMINANT.replace('answer+=left_choices*right_choices-invalid','answer+=left_choices*right_choices')],['Forgets that total length includes both the required ones and selected zeros.','Counts every placement of a zero group even when the substring is too short.'],dominant_oracle,random_dominant,lesson('A valid substring with z zeros needs length at least z²+z, so z is at most about sqrt(n).','Count all-one runs, then enumerate each consecutive group of z zeros and legal endpoints.','Use zero-position sentinels and subtract endpoint pairs whose extensions are too short.','Every substring has one unique consecutive zero group, and the arithmetic count enforces its exact minimum length.'),'O(n sqrt(n))','O(n)',8),
3237:entry('simulate_alt_tab',[('windows','list[int]'),('queries','list[int]')],'list[int]',['arrays','hash maps','simulation'],['windows is a permutation of 1..n in top-to-bottom order.','Each query moves that window to the top without reordering the others.','Return the final top-to-bottom order.'],[([[1,2,3],[3,3,2]],'The successive orders are 3,1,2; 3,1,2; then 2,3,1.'),([[1,4,2,3],[4,1,3]],'Moving 4, then 1, then 3 to the top leaves 3,1,4,2.')],[[w,q] for w,q in [([1],[1]),([1,2],[1]),([1,2],[2]),([2,1],[1,2]),([1,2,3],[3,3,2]),([1,4,2,3],[4,1,3]),([3,1,2],[2,1]),([1,2,3,4],[4,3,2,1]),([1,2,3,4],[2,2,2]),([5,4,3,2,1],[1,3,5]),([2,4,1,3],[4,3,4]),([1,3,5,2,4],[5,1,2]),([4,1,3,2],[2,4]),([6,1,5,2,4,3],[3,6,1,3])]],ALT,[ALT.replace('reversed(queries)','queries'),ALT.replace('if window not in seen:','if True:')],['Uses first-query rather than last-query recency.','Keeps duplicate queried windows in the result.'],alt_oracle,random_alt,lesson('Only the final occurrence of each queried window determines recency.','Scan queries backward, keep each window once, then append untouched windows in original order.','Build a seen set and front list from reversed queries; filter windows by seen.','Backward first encounters are decreasing last-use times, while untouched windows retain relative order.'),'O(n+q)','O(n)',3),
3239:entry('minimum_palindromic_grid_flips',[('grid','list[list[int]]')],'int',['matrices','two pointers'],['grid is a nonempty rectangular binary matrix with at most 200,000 cells.','Flip cells to make either every row palindromic or every column palindromic.','Return the smaller required flip count.'],[([[[1,0,0],[0,0,0],[0,0,1]]],'Two mirrored row pairs disagree, so two flips make every row palindromic.'),([[[0,1],[0,1],[0,0]]],'The columns contain one vertically mirrored mismatch, so one flip suffices.')],[[g] for g in [[[0]],[[1]],[[1],[0]],[[0,1]],[[0,1],[0,1],[0,0]],[[1,0,0],[0,0,0],[0,0,1]],[[1,0],[0,1]],[[1,1],[0,0]],[[1,0,1],[0,1,0]],[[1,0,0,1]],[[1],[0],[1]],[[0,1,1],[1,0,0]],[[1,0,1,0],[0,1,0,1]],[[1,1,0],[0,1,1],[1,0,0]]]],PAL_ONE,[PAL_ONE.replace('return min(rows,columns)','return rows'),PAL_ONE.replace('grid[m-1-r][c]','grid[r][c]')],['Always chooses rows even when columns are cheaper.','Compares each cell with itself instead of its vertical mirror.'],palindrome_one_oracle,random_grid,lesson('A mirrored pair needs one flip exactly when its cells differ.','Total horizontal disagreements for rows and vertical disagreements for columns independently.','Compare each pair once and return the smaller total.','Pairs in either orientation are disjoint, so mismatch costs add and no cheaper repair exists.'),'O(mn)','O(1)',5),
3240:entry('minimum_fully_palindromic_grid_flips',[('grid','list[list[int]]')],'int',['matrices','greedy','symmetry'],['grid is a nonempty rectangular binary matrix with at most 200,000 cells.','After flips, every row and column must be palindromic.','The final one count must be divisible by four; return the minimum flips.'],[([[[1,0,0],[0,1,0],[0,0,1]]],'The corners form one orbit and the center must be zero; three flips satisfy every condition.'),([[[0,1],[0,1],[0,0]]],'Two flips make all symmetry groups equal with a multiple of four ones.')],[[g] for g in [[[0]],[[1]],[[1],[1]],[[1],[0]],[[0,1]],[[1,1]],[[0,1],[0,1],[0,0]],[[1,0,0],[0,1,0],[0,0,1]],[[1,0],[0,1]],[[1,1],[1,1]],[[1,0,1],[0,0,0]],[[1,0,0,1]],[[1],[0],[1]],[[1,0,1],[1,1,1],[1,0,1]]]],PAL_TWO,[PAL_TWO.replace('min(ones,4-ones)','ones'),PAL_TWO.replace('paired_ones%4','0')],['Always clears four-cell orbits, missing cheaper all-one repairs.','Ignores the modulo-four correction when every middle pair already matches.'],palindrome_two_oracle,random_grid,lesson('Both symmetries partition cells into four-cell orbits, middle pairs, and possibly a center.','Repair four-cell groups by majority, then resolve middle pairs modulo four and clear the center.','Count mismatched middle pairs and matched-one pairs; a mismatch can absorb parity, otherwise two extra flips may be needed.','Four-cell groups never alter the remainder; the pair parity rule is necessary and constructively sufficient.'),'O(mn)','O(1)',6),
3247:entry('count_odd_sum_subsequences',[('nums','list[int]')],'int',['dynamic programming','combinatorics'],['1≤len(nums)≤100,000 and values are positive integers.','Subsequences preserve order and are distinguished by selected indices.','Return the odd-sum count modulo 1,000,000,007.'],[([[1,1,1]],'Three singleton choices and the three-element choice give four.'),([[1,2,2]],'Choose the odd value and any subset of the two evens, giving four.')],[[a] for a in [[1],[2],[1,1],[1,2],[2,2],[1,1,1],[1,2,2],[2,1,2],[1,3],[2,4,6],[1,2,3,4],[5,5,2],[7,8,9],[1,1,2,2]]],ODD,[ODD.replace('(odd+even+1)%modulo','(odd+1)%modulo'),ODD.replace('(2*odd)%modulo','odd')],['Fails to convert existing even sums when adding an odd value.','Fails to double odd choices when an even value may be included or skipped.'],odd_oracle,random_odd,lesson('Only subsequence-sum parity matters.','Maintain counts of nonempty even- and odd-sum subsequences.','Odd values swap parity when appended; even values preserve it. Add the singleton and reduce modulo M.','Partitioning by final index yields the two-state recurrence exactly once per index set.'),'O(n)','O(1)',5),
}
