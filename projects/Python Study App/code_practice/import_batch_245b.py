"""Exact-output dynamic-programming, parsing, and grid workbook imports."""
from collections import Counter, deque
from itertools import permutations, product

from .import_batch_055 import entry


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


def boxes_oracle(args):
    boxes = tuple(args[0])
    memo = {}
    def solve(values):
        if not values:return 0
        if values in memo:return memo[values]
        best=0;start=0
        while start<len(values):
            end=start+1
            while end<len(values) and values[end]==values[start]:end+=1
            best=max(best,(end-start)**2+solve(values[:start]+values[end:]))
            start=end
        memo[values]=best;return best
    return solve(boxes)


def random_boxes(rng):return [[rng.randint(1,4) for _ in range(rng.randint(1,8))]]


def attendance_oracle(args):
    n=args[0]
    return sum(word.count('A')<2 and 'LLL' not in word for word in map(''.join,product('ALP',repeat=n)))%1_000_000_007


def random_attendance(rng):return [rng.randint(1,6)]


def palindrome_oracle(args):
    value=int(args[0])
    for distance in range(1,value+2):
        lower=value-distance
        if lower>=0 and str(lower)==str(lower)[::-1]:return str(lower)
        upper=value+distance
        if str(upper)==str(upper)[::-1]:return str(upper)


def random_palindrome(rng):return [str(rng.randint(1,500_000))]


def vacation_oracle(args):
    flights,days=args;cities=len(flights);weeks=len(days[0]);best=0
    for route in product(range(cities),repeat=weeks):
        current=0;total=0;valid=True
        for week,next_city in enumerate(route):
            if next_city!=current and not flights[current][next_city]:valid=False;break
            total+=days[next_city][week];current=next_city
        if valid:best=max(best,total)
    return best


def random_vacation(rng):
    n=rng.randint(1,4);weeks=rng.randint(1,5)
    flights=[[int(i!=j and rng.random()<.5) for j in range(n)] for i in range(n)]
    days=[[rng.randint(0,7) for _ in range(weeks)] for _ in range(n)]
    return [flights,days]


def tag_oracle(args):
    code=args[0]
    def name_at(index,closing=False):
        start=index+(2 if closing else 1);end=code.find('>',start)
        if end<0:return None
        name=code[start:end]
        return (name,end+1) if 1<=len(name)<=9 and name.isalpha() and name.isupper() else None
    def parse(index):
        opened=name_at(index)
        if not opened:return None
        name,index=opened
        while index<len(code):
            if code.startswith('</',index):
                closed=name_at(index,True)
                return closed[1] if closed and closed[0]==name else None
            if code.startswith('<![CDATA[',index):
                end=code.find(']]>',index+9)
                if end<0:return None
                index=end+3
            elif code[index]=='<':
                nested=parse(index)
                if nested is None:return None
                index=nested
            else:index+=1
        return None
    end=parse(0)
    return end==len(code)


TAG_POOL=['<DIV>This is the first line <![CDATA[<div>]]></DIV>','<A></A>','<DIV>This is text</DIV>','<A><![CDATA[<B>bad</B>]]></A>',
          '<A></B>','<A>','text','<a></a>','<TOOLONGTAG></TOOLONGTAG>','<A><B></A></B>',
          '<A><![CDATA[x]]></A>tail','<A><!CDATA[x]]></A>','<A><B><![CDATA[<>]]></B></A>',
          '<A>1 < 2</A>','<ABC></ABC>','<A></A><B></B>']
def random_tag(rng):return [rng.choice(TAG_POOL)]


def forest_oracle(args):
    forest=args[0];rows=len(forest);cols=len(forest[0]);size=rows*cols;inf=10**6
    distance=[[inf]*size for _ in range(size)]
    for r in range(rows):
        for c in range(cols):
            if not forest[r][c]:continue
            source=r*cols+c;distance[source][source]=0
            for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0<=nr<rows and 0<=nc<cols and forest[nr][nc]:distance[source][nr*cols+nc]=1
    for middle in range(size):
        for left in range(size):
            for right in range(size):
                distance[left][right]=min(distance[left][right],distance[left][middle]+distance[middle][right])
    total=0;current=0
    for _,r,c in sorted((forest[r][c],r,c) for r in range(rows) for c in range(cols) if forest[r][c]>1):
        step=distance[current][r*cols+c]
        if step>=inf:return -1
        total+=step;current=r*cols+c
    return total


def random_forest(rng):
    rows,cols=rng.randint(1,4),rng.randint(1,4);cells=rows*cols
    forest=[[1]*cols for _ in range(rows)]
    choices=list(range(1,cells));rng.shuffle(choices)
    for cell in choices[:rng.randint(0,len(choices)//2)]:forest[cell//cols][cell%cols]=0
    open_cells=[i for i in range(cells) if forest[i//cols][i%cols]]
    for height,cell in enumerate(rng.sample(open_cells,rng.randint(1,len(open_cells))),2):forest[cell//cols][cell%cols]=height
    return [forest]


def atoms_oracle(args):
    formula=args[0]
    def number(index):
        end=index
        while end<len(formula) and formula[end].isdigit():end+=1
        return (int(formula[index:end]) if end>index else 1),end
    def parse(index):
        counts=Counter()
        while index<len(formula) and formula[index]!=')':
            if formula[index]=='(':
                nested,index=parse(index+1);index+=1;amount,index=number(index)
                for atom,count in nested.items():counts[atom]+=count*amount
            else:
                end=index+1
                while end<len(formula) and formula[end].islower():end+=1
                atom=formula[index:end];amount,index=number(end);counts[atom]+=amount
        return counts,index
    counts,_=parse(0)
    return ''.join(atom+(str(counts[atom]) if counts[atom]>1 else '') for atom in sorted(counts))


def random_formula(rng):
    atoms=['H','O','Mg','Na','Cl','C','He']
    def build(depth=0):
        parts=[]
        for _ in range(rng.randint(1,3)):
            if depth<2 and rng.random()<.3:part='('+build(depth+1)+')'
            else:part=rng.choice(atoms)
            count=rng.randint(1,4);parts.append(part+(str(count) if count>1 else ''))
        return ''.join(parts)
    return [build()]


def window_oracle(args):
    source,target=args;best=''
    for left in range(len(source)):
        for right in range(left+1,len(source)+1):
            candidate=source[left:right];at=0
            for char in candidate:
                if at<len(target) and char==target[at]:at+=1
            if at==len(target) and (not best or len(candidate)<len(best)):best=candidate
    return best


def random_window(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,14))),
            ''.join(rng.choice('abcd') for _ in range(rng.randint(1,5)))]


def pal_subsequence_oracle(args):
    text=args[0];values=set()
    for mask in range(1,1<<len(text)):
        value=''.join(text[i] for i in range(len(text)) if mask>>i&1)
        if value==value[::-1]:values.add(value)
    return len(values)%1_000_000_007


def random_pal_subsequence(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,10)))]


def gas_oracle(args):
    stations,k=args;gaps=[stations[i+1]-stations[i] for i in range(len(stations)-1)];best=float('inf')
    def assign(index,left,parts):
        nonlocal best
        if index==len(gaps)-1:
            use=left;best=min(best,max([gaps[i]/parts[i] for i in range(index)]+[gaps[index]/(use+1)]));return
        for use in range(left+1):assign(index+1,left-use,parts+[use+1])
    assign(0,k,[]);return best


def random_gas(rng):
    n=rng.randint(2,7);stations=sorted(rng.sample(range(0,60),n))
    return [stations,rng.randint(0,7)]


def chess_oracle(args):
    board=args[0];n=len(board);target=[i%2 for i in range(n)];best=10**9
    rows=range(n)
    for row_order in permutations(rows):
        row_moves=sum(a!=b for a,b in zip(row_order,rows))//2
        for col_order in permutations(rows):
            made=[[board[row_order[r]][col_order[c]] for c in rows] for r in rows]
            if all(made[r][c]==(r+c)%2 for r in rows for c in rows) or all(made[r][c]==(r+c+1)%2 for r in rows for c in rows):
                best=min(best,row_moves+sum(a!=b for a,b in zip(col_order,rows))//2)
    return -1 if best==10**9 else best


def random_chess(rng):
    n=rng.randint(2,4)
    if rng.random()<.7:
        board=[[(r+c+rng.randrange(2))%2 for c in range(n)] for r in range(n)]
        rng.shuffle(board);order=list(range(n));rng.shuffle(order);board=[[row[c] for c in order] for row in board]
    else:board=[[rng.randrange(2) for _ in range(n)] for _ in range(n)]
    return [board]


BOXES='''def maximum_remove_boxes_score(boxes):
    from functools import lru_cache
    @lru_cache(None)
    def solve(left,right,carried):
        if left>right:return 0
        while left<right and boxes[right-1]==boxes[right]:right-=1;carried+=1
        best=solve(left,right-1,0)+(carried+1)**2
        for index in range(left,right):
            if boxes[index]==boxes[right]:best=max(best,solve(left,index,carried+1)+solve(index+1,right-1,0))
        return best
    return solve(0,len(boxes)-1,0)
'''
ATTEND='''def count_rewardable_attendance_records(n):
    mod=1000000007;dp={(0,0):1}
    for _ in range(n):
        nxt={}
        for (absent,late),count in dp.items():
            nxt[(absent,0)]=(nxt.get((absent,0),0)+count)%mod
            if absent==0:nxt[(1,0)]=(nxt.get((1,0),0)+count)%mod
            if late<2:nxt[(absent,late+1)]=(nxt.get((absent,late+1),0)+count)%mod
        dp=nxt
    return sum(dp.values())%mod
'''
PALINDROME='''def nearest_palindrome(n):
    value=int(n);length=len(n);prefix=int(n[:(length+1)//2]);candidates={10**(length-1)-1,10**length+1}
    for first in (prefix-1,prefix,prefix+1):
        text=str(first);candidates.add(int(text+text[-1-(length%2)::-1]))
    candidates.discard(value)
    return str(min(candidates,key=lambda candidate:(abs(candidate-value),candidate)))
'''
VACATION='''def maximum_vacation_days(flights,days):
    n=len(flights);best=[-10**9]*n;best[0]=0
    for week in range(len(days[0])):
        nxt=[-10**9]*n
        for city in range(n):
            for destination in range(n):
                if city==destination or flights[city][destination]:nxt[destination]=max(nxt[destination],best[city]+days[destination][week])
        best=nxt
    return max(best)
'''
TAG='''def is_valid_tag_code(code):
    stack=[];index=0
    while index<len(code):
        if index and not stack:return False
        if code.startswith('<![CDATA[',index):
            if not stack:return False
            end=code.find(']]>',index+9)
            if end<0:return False
            index=end+3;continue
        if code[index]=='<':
            closing=code.startswith('</',index);end=code.find('>',index+1)
            if end<0:return False
            name=code[index+(2 if closing else 1):end]
            if not (1<=len(name)<=9 and name.isalpha() and name.isupper()):return False
            if closing:
                if not stack or stack.pop()!=name:return False
            else:stack.append(name)
            index=end+1
        else:index+=1
    return not stack and index==len(code)
'''
FOREST='''def cut_forest_trees(forest):
    from collections import deque
    rows=len(forest);cols=len(forest[0])
    def distance(start,target):
        queue=deque([(start[0],start[1],0)]);seen={start}
        while queue:
            r,c,steps=queue.popleft()
            if (r,c)==target:return steps
            for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0<=nr<rows and 0<=nc<cols and forest[nr][nc] and (nr,nc) not in seen:seen.add((nr,nc));queue.append((nr,nc,steps+1))
        return -1
    current=(0,0);answer=0
    for _,r,c in sorted((forest[r][c],r,c) for r in range(rows) for c in range(cols) if forest[r][c]>1):
        steps=distance(current,(r,c))
        if steps<0:return -1
        answer+=steps;current=(r,c)
    return answer
'''
ATOMS='''def count_formula_atoms(formula):
    from collections import Counter
    stack=[Counter()];index=0
    while index<len(formula):
        if formula[index]=='(':stack.append(Counter());index+=1
        elif formula[index]==')':
            index+=1;end=index
            while end<len(formula) and formula[end].isdigit():end+=1
            multiplier=int(formula[index:end] or 1);group=stack.pop()
            for atom,count in group.items():stack[-1][atom]+=count*multiplier
            index=end
        else:
            end=index+1
            while end<len(formula) and formula[end].islower():end+=1
            atom=formula[index:end];digits=end
            while end<len(formula) and formula[end].isdigit():end+=1
            stack[-1][atom]+=int(formula[digits:end] or 1);index=end
    return ''.join(atom+(str(stack[0][atom]) if stack[0][atom]>1 else '') for atom in sorted(stack[0]))
'''
WINDOW='''def minimum_window_subsequence(s1,s2):
    best='';index=0
    while index<len(s1):
        target=0
        while index<len(s1):
            if s1[index]==s2[target]:
                target+=1
                if target==len(s2):break
            index+=1
        if target<len(s2):break
        end=index+1;target-=1
        while target>=0:
            if s1[index]==s2[target]:target-=1
            index-=1
        start=index+1;candidate=s1[start:end]
        if not best or len(candidate)<len(best):best=candidate
        index=start+1
    return best
'''
PAL_SUB='''def count_distinct_palindromic_subsequences(s):
    mod=1000000007;n=len(s);dp=[[0]*n for _ in range(n)]
    for i in range(n):dp[i][i]=1
    for length in range(2,n+1):
        for left in range(n-length+1):
            right=left+length-1
            if s[left]!=s[right]:dp[left][right]=dp[left+1][right]+dp[left][right-1]-dp[left+1][right-1]
            else:
                low,high=left+1,right-1
                while low<=high and s[low]!=s[left]:low+=1
                while low<=high and s[high]!=s[left]:high-=1
                if low>high:dp[left][right]=2*dp[left+1][right-1]+2
                elif low==high:dp[left][right]=2*dp[left+1][right-1]+1
                else:dp[left][right]=2*dp[left+1][right-1]-dp[low+1][high-1]
            dp[left][right]%=mod
    return dp[0][n-1]
'''
GAS='''def minimize_maximum_gas_gap(stations,k):
    left=0.0;right=max(b-a for a,b in zip(stations,stations[1:]))
    for _ in range(70):
        middle=(left+right)/2
        needed=sum(int((b-a)/middle) for a,b in zip(stations,stations[1:]))
        if needed>k:left=middle
        else:right=middle
    return right
'''
CHESS='''def minimum_chessboard_swaps(board):
    n=len(board)
    if any(board[r][c]^board[0][c]^board[r][0]^board[0][0] for r in range(n) for c in range(n)):return -1
    row_sum=sum(board[0]);col_sum=sum(board[r][0] for r in range(n))
    if not n//2<=row_sum<=(n+1)//2 or not n//2<=col_sum<=(n+1)//2:return -1
    row_moves=sum(board[0][c]==c%2 for c in range(n));col_moves=sum(board[r][0]==r%2 for r in range(n))
    if n%2:row_moves=n-row_moves if row_moves%2 else row_moves;col_moves=n-col_moves if col_moves%2 else col_moves
    else:row_moves=min(row_moves,n-row_moves);col_moves=min(col_moves,n-col_moves)
    return (row_moves+col_moves)//2
'''


CASES={
546:[[x] for x in ([1,3,2,2,2,3,4,3,1],[1,1,1],[1],[1,2],[1,2,1],[1,2,2,1],[1,2,1,2],[1,1,2,2],[1,2,3,2,1],[2,2,1,2,2],[1,3,3,1,3],[4,3,2,1],[1,2,3,3,2,1],[1,1,2,1,2,2])],
552:[[n] for n in (2,1,3,4,5,6,7,8,10,12,20,50,100,101)],
564:[[s] for s in ('123','1','10','11','99','100','101','1000','999','1283','12345','9999','10001','807045053224792883')],
568:[[f,d] for f,d in [([[0,1,1],[1,0,1],[1,1,0]],[[1,3,1],[6,0,3],[3,3,3]]),([[0,0,0],[0,0,0],[0,0,0]],[[1,1,1],[7,7,7],[7,7,7]]),([[0]],[[5]]),([[0]],[[1,2,3]]),([[0,1],[0,0]],[[1],[7]]),([[0,0],[1,0]],[[4,4],[7,7]]),([[0,1],[1,0]],[[0,7],[7,0]]),([[0,1,0],[0,0,1],[1,0,0]],[[1,1],[2,2],[3,3]]),([[0,1,1],[0,0,0],[0,0,0]],[[1,1,1],[2,2,2],[7,0,7]]),([[0,1],[0,0]],[[5,0,5],[0,7,0]]),([[0,0],[0,0]],[[0,0],[7,7]]),([[0,1,0],[1,0,1],[0,1,0]],[[7,0,0],[0,7,0],[0,0,7]]),([[0,1],[1,0]],[[3,4,5,6],[6,5,4,3]]),([[0,1,1],[1,0,0],[0,1,0]],[[2,4,1],[5,1,6],[3,7,2]])]],
591:[[s] for s in TAG_POOL],
675:[[f] for f in [ [[1,2,3],[0,0,4],[7,6,5]],[[1,2,3],[0,0,0],[7,6,5]],[[2]],[[1,2]],[[1],[2],[3]],[[1,0,2]],[[1,2],[3,4]],[[1,3,2]],[[1,2,0],[0,3,4]],[[1,0,3],[2,4,5]],[[1,2,3],[4,5,6]],[[1,2],[0,3],[4,5]],[[1,0,0],[2,3,4]],[[1,5,1],[2,3,4]] ]],
726:[[s] for s in ('H2O','Mg(OH)2','K4(ON(SO3)2)2','H','He','H2O2','(H)2','NaCl','C6H12O6','((H)2O)3','Be32','((Mg)2(OH)4)3','H2He3O4','(NaCl)2H2O')],
727:[[a,b] for a,b in [('abcdebdde','bde'),('jmeqksfrsdcmsiwvaovztaqenprpvnbstl','u'),('a','a'),('a','b'),('abc','ac'),('abc','abc'),('aaaaa','aa'),('cnhczmccqouqadqtmjjzl','mm'),('abdbcc','abc'),('axbyab','ab'),('abcabc','cab'),('bbbbac','bac'),('abcdef','f'),('aaabbbccc','abc')]],
730:[[s] for s in ('bccb','a','aa','ab','aba','aaa','abcd','abca','abcba','abab','aabb','abcdabcd','ccbbcc','dacbcbad')],
774:[[s,k] for s,k in [([1,2,3,4,5,6,7,8,9,10],9),([23,24,36,39,46,56,57,65,84,98],1),([0,10],0),([0,10],1),([0,10],9),([1,5,9],2),([0,3,10],3),([2,3],5),([0,100],7),([1,2,100],4),([0,5,6,20],5),([10,20,30],1),([0,1,2,50],10),([3,8,15,24],6)]],
782:[[b] for b in [ [[0,1],[1,0]],[[1,0],[1,0]],[[1,1],[1,1]],[[0,1,1,0],[0,1,1,0],[1,0,0,1],[1,0,0,1]],[[0,1,0],[1,0,1],[0,1,0]],[[1,0,1],[0,1,0],[1,0,1]],[[0,0],[0,1]],[[0,1],[0,1]],[[1,0],[0,1]],[[0,1,0,1],[1,0,1,0],[0,1,0,1],[1,0,1,0]],[[1,1,0,0],[0,0,1,1],[1,1,0,0],[0,0,1,1]],[[0,1,1],[1,0,0],[1,0,0]],[[1,0,0],[0,1,1],[0,1,1]],[[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0]] ]],
}

BATCH={
546:entry('maximum_remove_boxes_score',[('boxes','list[int]')],'int',['dynamic programming','recursion','memoization'],['boxes has 1–100 positive color identifiers.','Removing a contiguous same-color run of length k earns k squared; maximize the total.'],[([CASES[546][0][0]],'Delaying matching colors until intervening boxes disappear produces twenty-three points.'),([CASES[546][1][0]],'Removing all three equal boxes together earns nine.')],CASES[546][2:],BOXES,[BOXES.replace('(carried+1)**2','carried+1'),BOXES.replace('carried+1)+solve','0)+solve')],['Scores a merged run linearly instead of quadratically.','Fails to carry matching right-end boxes across the removed middle interval.'],boxes_oracle,random_boxes,lesson('The future value of an interval depends on how many matching boxes are already attached to its right edge.','Memoize left, right, and carried count; either remove the right run now or merge it with an earlier equal color.','Compress equal suffix boxes, score removal, and try every matching split point.','Every optimal first action for the rightmost color is either immediate removal or one specific intervening segment removed to enable a merge.'),'O(n^4)','O(n^3)',8),
552:entry('count_rewardable_attendance_records',[('n','int')],'int',['dynamic programming','state machines'],['1 <= n <= 100,000.','Valid records use A, L, P with fewer than two total A and no LLL substring.','Return the count modulo 1,000,000,007.'],[([2],'All nine length-two records except AA are valid.'),([1],'A, L, and P are all valid one-day records.')],CASES[552][2:],ATTEND,[ATTEND.replace('absent==0','absent<=1'),ATTEND.replace('late<2','late<3')],['Allows a second absence.','Allows three consecutive late days.'],attendance_oracle,random_attendance,lesson('Only absence count and current trailing-late length affect future validity.','Maintain six states: zero/one absence crossed with late run zero, one, or two.','Append P, optionally A, or L when its state limit permits, reducing modulo each day.','The state captures every forbidden-pattern condition, and each appended character creates each valid record exactly once.'),'O(n)','O(1)',8),
564:entry('nearest_palindrome',[('n','str')],'str',['strings','math'],['n is a decimal integer string from 1 through 10^18-1 with no leading zero.','Exclude n itself; minimize absolute difference and choose the smaller palindrome on ties.'],[(['123'],'Mirroring nearby prefixes makes 121 the closest palindrome.'),(['1'],'Zero and two tie at distance one, so return zero.')],CASES[564][2:],PALINDROME,[PALINDROME.replace('prefix-1,prefix,prefix+1','prefix,prefix+1'),PALINDROME.replace('(abs(candidate-value),candidate)','(abs(candidate-value),-candidate)')],['Omits the smaller neighboring prefix and can miss the closest palindrome.','Chooses the larger palindrome when distances tie.'],palindrome_oracle,random_palindrome,lesson('A closest palindrome comes from mirroring the current prefix or one of its immediate neighbors, plus digit-length boundaries.','Generate those five candidates and rank them after removing the input itself.','Mirror prefix-1, prefix, prefix+1; add 99…9 and 100…001; minimize (distance,value).','Any farther prefix changes the leading half more than a neighboring prefix, while boundary candidates cover carries that change digit length.'),'O(digits)','O(digits)',8),
568:entry('maximum_vacation_days',[('flights','list[list[int]]'),('days','list[list[int]]')],'int',['dynamic programming','graphs'],['flights is n by n and days is n by weeks; start in city zero.','Each Monday either stay or take one available directed flight, then collect that destination week’s days.'],[([*CASES[568][0]],'Choosing reachable cities week by week yields twelve vacation days.'),([*CASES[568][1]],'With no flights, every week must be spent in city zero for three total days.')],CASES[568][2:],VACATION,[VACATION.replace('city==destination or ','') ,VACATION.replace('best[0]=0','best[-1]=0')],['Forbids staying in the current city when no self-flight is listed.','Starts in the last city instead of city zero.'],vacation_oracle,random_vacation,lesson('At each week only the current city and accumulated total matter.','Transition from every reachable city to itself and each flight destination.','next[destination]=max(next[destination],best[city]+days[destination][week]).','Every legal itinerary has one final city per week, so the layered DP considers it once and keeps its best prefix.'),'O(weeks*n²)','O(n)',8),
591:entry('is_valid_tag_code',[('code','str')],'bool',['strings','stacks','parsing'],['The whole code must be one closed root tag.','Tag names contain 1–9 uppercase letters; CDATA is recognized only inside an open tag and ends at the first ]]> marker.'],[([CASES[591][0][0]],'A single matching uppercase root tag is valid.'),([CASES[591][3][0]],'CDATA shields its apparent nested tag text from parsing.')],CASES[591][1:3]+CASES[591][4:],TAG,[TAG.replace('if index and not stack:return False','if False:return False'),TAG.replace('and name.isupper()','')],['Allows trailing content or a second root after the first tag closes.','Accepts lowercase tag names.'],tag_oracle,random_tag,lesson('A stack enforces properly nested tag names while a dedicated branch skips complete CDATA regions.','Scan left to right, rejecting content outside the one root.','Push start names, match and pop end names, skip from <![CDATA[ to ]]>, and validate names.','The stack is exactly the unmatched ancestor chain, and every special opening token is consumed according to its grammar.'),'O(length)','O(nesting depth)',8),
675:entry('cut_forest_trees',[('forest','list[list[int]]')],'int',['graphs','breadth-first search','sorting'],['0 is blocked, 1 is walkable, and each value above 1 is a uniquely tall tree.','Starting at (0,0), visit and cut every tree in increasing height order using four-directional steps.'],[([CASES[675][0][0]],'The increasing-height route follows the accessible perimeter in six steps.'),([CASES[675][1][0]],'The blocked middle row makes the lower trees unreachable.')],CASES[675][2:],FOREST,[FOREST.replace('if steps<0:return -1','if steps<0:continue'),FOREST.replace("current=(r,c)","current=(0,0)")],['Skips unreachable required trees instead of reporting failure.','Restarts every trip at the origin rather than the previously cut tree.'],forest_oracle,random_forest,lesson('Tree heights fix the visit order, leaving only shortest paths between consecutive targets.','Sort tree cells and run BFS from the current position to each next tree.','Accumulate each BFS distance; return -1 on an unreachable target.','Any valid cutting walk must visit the same target sequence, and replacing each segment by its shortest route is independently optimal.'),'O(trees*rows*cols)','O(rows*cols)',8),
726:entry('count_formula_atoms',[('formula','str')],'str',['stacks','parsing','hash maps'],['formula is a valid chemical expression using element names, counts, concatenation, and parentheses.','Return atoms lexicographically with counts omitted when equal to one.'],[(['H2O'],'Hydrogen occurs twice and oxygen once, producing H2O.'),(['Mg(OH)2'],'The parenthesized multiplier doubles O and H; lexicographic output is H2MgO2.')],CASES[726][2:],ATOMS,[ATOMS.replace('count*multiplier','count'),ATOMS.replace('for atom in sorted(stack[0])','for atom in stack[0]')],['Ignores multipliers after parenthesized groups.','Emits atoms in parsing order rather than required lexicographic order.'],atoms_oracle,random_formula,lesson('Nested parentheses require suspended count maps that are multiplied when their group closes.','Scan tokens with a stack of Counters.','Push at (, pop and multiply at ), otherwise parse an element and optional digits; sort the final keys.','Each token contributes to its innermost group, and closing groups applies every surrounding multiplier exactly once.'),'O(length log atoms)','O(length)',8),
727:entry('minimum_window_subsequence',[('s1','str'),('s2','str')],'str',['strings','two pointers'],['s1 and s2 are lowercase strings; find a contiguous s1 window containing s2 as a subsequence.','Minimize window length, breaking ties by earliest start; return empty when impossible.'],[([*CASES[727][0]],'bcde and bdde tie in length, so the earlier bcde is returned.'),([*CASES[727][1]],'The target character never appears, so no window exists.')],CASES[727][2:],WINDOW,['''def minimum_window_subsequence(s1,s2):
    start=s1.find(s2[0])
    if start<0:return ''
    at=0
    for end in range(start,len(s1)):
        if s1[end]==s2[at]:
            at+=1
            if at==len(s2):return s1[start:end+1]
    return ''
''',WINDOW.replace('len(candidate)<len(best)','len(candidate)<=len(best)')],['Stops after the first feasible start instead of searching later starts for a shorter window.','Replaces an earlier equal-length optimum with a later window.'],window_oracle,random_window,lesson('A forward scan finds a complete subsequence endpoint; a backward scan then contracts that window to its latest possible start.','Repeat forward matching and backward contraction from the next start.','Advance through s1 for s2, retreat through s2 to shrink, record if shorter, then restart just after the contracted start.','Every minimal window has a first complete endpoint found by a forward scan, and backward contraction produces its unique shortest start.'),'O(len(s1)*len(s2))','O(1)',8),
730:entry('count_distinct_palindromic_subsequences',[('s','str')],'int',['dynamic programming','strings'],['s contains 1–1000 lowercase letters.','Count distinct nonempty palindromic subsequence strings modulo 1,000,000,007.'],[(['bccb'],'The distinct results are b, c, bb, cc, bcb, and bccb.'),(['a'],'The one-character subsequence is the only nonempty palindrome.')],CASES[730][2:],PAL_SUB,[PAL_SUB.replace('-dp[low+1][high-1]','+dp[low+1][high-1]'),PAL_SUB.replace('elif low==high','elif low<=high')],['Adds rather than removes palindromes duplicated between the inner equal boundary characters.','Treats the no-inner-match case as one-inner-match and undercounts new wrapped palindromes.'],pal_subsequence_oracle,random_pal_subsequence,lesson('Interval DP can combine distinct palindrome sets while correcting duplicates created by equal boundary characters.','Use inclusion-exclusion for unequal ends; for equal ends locate the next and previous same character inside.','Double the inner count, add two/one for zero/one inner matches, or subtract the doubly represented middle for two matches.','These cases partition palindromes by whether they use neither, one, or both boundary characters and remove exactly the duplicated strings.'),'O(n³) with boundary scans','O(n²)',8),
774:entry('minimize_maximum_gas_gap',[('stations','list[int]'),('k','int')],'float',['binary search','greedy'],['stations is strictly increasing and k is the exact number of additional stations available.','Minimize the largest adjacent distance; answers within 1e-6 are accepted.'],[([*CASES[774][0]],'One station in each unit gap halves the maximum distance to 0.5.'),([*CASES[774][1]],'The best single insertion splits the largest original gap.')],CASES[774][2:],GAS,[GAS.replace('needed>k','needed>=k'),GAS.replace('range(70)','range(5)')],['Treats exactly k required insertions as infeasible.','Stops binary search too early for the required precision.'],gas_oracle,random_gas,lesson('For a proposed maximum gap d, each original gap independently requires a computable number of inserted stations.','Binary-search the smallest feasible d.','needed=sum(floor(gap/d)); if needed>k increase d, otherwise decrease it.','Feasibility is monotone in d, so repeated bisection converges to the optimum boundary.'),'O(n log precision)','O(1)',8),
782:entry('minimum_chessboard_swaps',[('board','list[list[int]]')],'int',['matrices','math','greedy'],['board is n by n binary; one move swaps any two complete rows or any two complete columns.','Return the minimum swaps to make adjacent cells differ horizontally and vertically, or -1.'],[([CASES[782][0][0]],'The two-by-two board is already a chessboard.'),([CASES[782][3][0]],'One row swap and one column swap create an alternating board.')],CASES[782][1:3]+CASES[782][4:],CHESS,['''def minimum_chessboard_swaps(board):
    n=len(board);row=sum(board[0]);column=sum(board[r][0] for r in range(n))
    return 0 if n//2<=row<=(n+1)//2 and n//2<=column<=(n+1)//2 else -1
''',CHESS.replace('//2','',1)],['Checks only first-row and first-column balance and ignores arrangement and complement consistency.','Counts displaced row positions as full swaps instead of pairs.'],chess_oracle,random_chess,lesson('Every valid board has only one row pattern and its bitwise complement, with balanced counts; columns obey the same rule.','Check the XOR rectangle invariant, then count alternating-position mismatches in the first row and column.','Validate row/column one counts, choose the only parity for odd n or cheaper parity for even n, and halve mismatches.','Whole-row and whole-column swaps are independent once the complement structure holds, and each swap fixes two misplaced patterns.'),'O(n²)','O(1)',8),
}

BATCH[774]['comparator']='float'
