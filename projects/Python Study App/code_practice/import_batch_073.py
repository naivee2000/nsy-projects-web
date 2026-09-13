"""Reviewed probability, strings, geometry, DP, and grid imports."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
import re

from . import import_batch_055 as batch_base
from .import_batch_055 import entry

batch_base.EXTRA_BOUNDARIES.update({
    'factored_binary_tree_count': [[[3,6,18]]],
    'friend_request_count': [[[21,21,21]]],
    'mask_personal_information': [['44 123 456 7890']],
})

MOD=10**9+7

def soup_oracle(args):
    n=args[0]
    if n>4800:return 1.0
    units=(n+24)//25
    @lru_cache(None)
    def chance(a,b):
        if a<=0 and b<=0:return .5
        if a<=0:return 1.0
        if b<=0:return 0.0
        return sum(chance(a-da,b-db) for da,db in ((4,0),(3,1),(2,2),(1,3)))/4
    return chance(units,units)

def expressive_oracle(args):
    target,words=args
    def groups(text):
        result=[]
        for char in text:
            if result and result[-1][0]==char:result[-1][1]+=1
            else:result.append([char,1])
        return result
    wanted=groups(target);answer=0
    for word in words:
        source=groups(word)
        answer+=len(source)==len(wanted) and all(a==b and (y==x or y>=3 and y>x) for (a,x),(b,y) in zip(source,wanted))
    return answer

def domains_oracle(args):
    counts=Counter()
    for item in args[0]:
        count_text,domain=item.split();parts=domain.split('.')
        for index in range(len(parts)):counts['.'.join(parts[index:])]+=int(count_text)
    return [f'{count} {domain}' for domain,count in sorted(counts.items())]

def triangle_oracle(args):
    points=args[0]
    return max((abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2 for a,b,c in combinations(points,3)),default=0.0)

def averages_oracle(args):
    nums,k=args;prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    @lru_cache(None)
    def solve(start,groups):
        if groups==1:return (prefix[-1]-prefix[start])/(len(nums)-start)
        return max((prefix[end]-prefix[start])/(end-start)+solve(end,groups-1) for end in range(start+1,len(nums)-groups+2))
    return solve(0,k)

def coordinates_oracle(args):
    text=args[0][1:-1]
    def forms(part):
        answer=[]
        for cut in range(1,len(part)+1):
            left,right=part[:cut],part[cut:]
            if len(left)>1 and left[0]=='0':continue
            if right and right[-1]=='0':continue
            answer.append(left+('.'+right if right else ''))
        return answer
    return [f'({left}, {right})' for cut in range(1,len(text)) for left in forms(text[:cut]) for right in forms(text[cut:])]

def common_oracle(args):
    paragraph,banned=args;words=re.findall(r'[a-z]+',paragraph.lower());blocked=set(banned);counts=Counter(word for word in words if word not in blocked)
    return max(counts,key=counts.get)

def encoding_oracle(args):
    words=set(args[0]);roots=[word for word in words if not any(other!=word and other.endswith(word) for other in words)]
    return sum(len(word)+1 for word in roots)

def distance_oracle(args):
    text,target=args
    return [min(abs(index-other) for other,char in enumerate(text) if char==target) for index in range(len(text))]

def flip_oracle(args):
    fronts,backs=args;bad={front for front,back in zip(fronts,backs) if front==back};candidates=(set(fronts)|set(backs))-bad
    return min(candidates,default=0)

def factor_trees_oracle(args):
    values=set(args[0])
    @lru_cache(None)
    def count(root):return 1+sum(count(left)*count(root//left) for left in values if root%left==0 and root//left in values)
    return sum(count(value) for value in values)%MOD

def goat_oracle(args):
    answer=[]
    for index,word in enumerate(args[0].split(),1):
        changed=word if word[0].lower() in 'aeiou' else word[1:]+word[0]
        answer.append(changed+'ma'+'a'*index)
    return ' '.join(answer)

def requests_oracle(args):
    ages=args[0]
    return sum(i!=j and not (b<=.5*a+7 or b>a or b>100>a) for i,a in enumerate(ages) for j,b in enumerate(ages))

def profit_oracle(args):
    difficulty,profit,workers=args
    return sum(max((gain for level,gain in zip(difficulty,profit) if level<=worker),default=0) for worker in workers)

def island_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0])
    def area(board):
        seen=set();best=0
        for r in range(rows):
            for c in range(columns):
                if not board[r][c] or (r,c) in seen:continue
                stack=[(r,c)];seen.add((r,c));size=0
                while stack:
                    x,y=stack.pop();size+=1
                    for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                        if 0<=nx<rows and 0<=ny<columns and board[nx][ny] and (nx,ny) not in seen:seen.add((nx,ny));stack.append((nx,ny))
                best=max(best,size)
        return best
    answer=area(grid)
    for r in range(rows):
        for c in range(columns):
            if grid[r][c]==0:
                board=[row[:] for row in grid];board[r][c]=1;answer=max(answer,area(board))
    return answer

def unique_oracle(args):
    text=args[0]
    return sum(sum(count==1 for count in Counter(text[left:right]).values()) for left in range(len(text)) for right in range(left+1,len(text)+1))

def consecutive_oracle(args):
    odd=args[0]
    while odd%2==0:odd//=2
    divisors=0;factor=1
    while factor*factor<=odd:
        if odd%factor==0:divisors+=1 if factor*factor==odd else 2
        factor+=1
    return divisors

def groups_oracle(args):
    text=args[0];answer=[];start=0
    for end in range(1,len(text)+1):
        if end==len(text) or text[end]!=text[start]:
            if end-start>=3:answer.append([start,end-1])
            start=end
    return answer

def mask_oracle(args):
    text=args[0]
    if '@' in text:
        name,domain=text.lower().split('@');return name[0]+'*****'+name[-1]+'@'+domain
    digits=''.join(char for char in text if char.isdigit());local='***-***-'+digits[-4:];return ('+'+'*'*(len(digits)-10)+'-' if len(digits)>10 else '')+local

def image_oracle(args):return [[1-value for value in reversed(row)] for row in args[0]]


def random_soup(rng):return [rng.randint(0,5000)]
def random_expressive(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,12))),[''.join(rng.choice('abc') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,8))]]
def random_domains(rng):
    domains=['com','a.com','b.com','x.a.com','y.b.com'];return [[f'{rng.randint(1,100)} {rng.choice(domains)}' for _ in range(rng.randint(1,8))]]
def random_triangle(rng):return [[[rng.randint(-10,10),rng.randint(-10,10)] for _ in range(rng.randint(3,8))]]
def random_averages(rng):
    nums=[rng.randint(1,20) for _ in range(rng.randint(1,8))];return [nums,rng.randint(1,len(nums))]
def random_coordinates(rng):return ['('+''.join(rng.choice('0123456789') for _ in range(rng.randint(2,7)))+')']
def random_common(rng):
    words=[rng.choice(['alpha','beta','gamma','delta']) for _ in range(rng.randint(2,20))];winner=Counter(words).most_common(1)[0][0];return [' '.join(words),[word for word in set(words) if word!=winner and rng.random()<.3]]
def random_encoding(rng):return [[''.join(rng.choice('abcde') for _ in range(rng.randint(1,7))) for _ in range(rng.randint(1,10))]]
def random_distance(rng):
    text=''.join(rng.choice('abcde') for _ in range(rng.randint(1,30)));return [text,rng.choice(text)]
def random_flip(rng):
    size=rng.randint(1,10);return [[rng.randint(1,12) for _ in range(size)],[rng.randint(1,12) for _ in range(size)]]
def random_factors(rng):return [sorted(set([2]+[rng.choice([2,4,8,16,3,6,12,24]) for _ in range(rng.randint(1,7))]))]
def random_goat(rng):return [' '.join(''.join(rng.choice('abcdeXYZ') for _ in range(rng.randint(1,7))) for _ in range(rng.randint(1,8)))]
def random_ages(rng):return [[rng.randint(1,120) for _ in range(rng.randint(1,20))]]
def random_profit(rng):
    size=rng.randint(1,10);return [[rng.randint(1,20) for _ in range(size)],[rng.randint(1,100) for _ in range(size)],[rng.randint(1,20) for _ in range(rng.randint(1,10))]]
def random_island(rng):
    size=rng.randint(1,5);return [[[rng.randrange(2) for _ in range(size)] for _ in range(size)]]
def random_unique(rng):return [''.join(rng.choice('ABCDE') for _ in range(rng.randint(1,10)))]
def random_consecutive(rng):return [rng.randint(1,500)]
def random_groups(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,30)))]
def random_mask(rng):
    if rng.random()<.5:return [''.join(rng.choice('abcde') for _ in range(rng.randint(2,8)))+'@x.com']
    digits=''.join(str(rng.randrange(10)) for _ in range(rng.randint(10,13)));return [digits]
def random_image(rng):
    rows,columns=rng.randint(1,6),rng.randint(1,6);return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]


SOUP='''\
def soup_serving_probability(n):
    if n>4800:return 1.0
    from functools import lru_cache
    units=(n+24)//25
    @lru_cache(None)
    def solve(a,b):
        if a<=0 and b<=0:return .5
        if a<=0:return 1.0
        if b<=0:return 0.0
        return sum(solve(a-da,b-db) for da,db in ((4,0),(3,1),(2,2),(1,3)))/4
    return solve(units,units)
'''
EXPRESSIVE='''\
def expressive_word_count(s, words):
    def groups(text):
        answer=[]
        for char in text:
            if answer and answer[-1][0]==char:answer[-1][1]+=1
            else:answer.append([char,1])
        return answer
    target=groups(s);answer=0
    for word in words:
        source=groups(word)
        if len(source)==len(target) and all(a==b and (x==y or y>=3 and x<y) for (a,x),(b,y) in zip(source,target)):answer+=1
    return answer
'''
DOMAINS='''\
def subdomain_visit_counts(cpdomains):
    from collections import Counter
    counts=Counter()
    for item in cpdomains:
        amount,domain=item.split();parts=domain.split('.')
        for index in range(len(parts)):counts['.'.join(parts[index:])]+=int(amount)
    return [f'{counts[domain]} {domain}' for domain in counts]
'''
TRIANGLE='''\
def largest_triangle_area(points):
    from itertools import combinations
    return max(abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2 for a,b,c in combinations(points,3))
'''
AVERAGES='''\
def largest_average_sum(nums, k):
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    dp=[(prefix[-1]-prefix[i])/(len(nums)-i) for i in range(len(nums))]
    for groups in range(2,k+1):
        dp=[max((prefix[end]-prefix[start])/(end-start)+dp[end] for end in range(start+1,len(nums)-groups+2)) if start<=len(nums)-groups else float('-inf') for start in range(len(nums))]
    return dp[0]
'''
COORDINATES='''\
def ambiguous_coordinates(s):
    digits=s[1:-1]
    def forms(part):
        answer=[]
        for cut in range(1,len(part)+1):
            left,right=part[:cut],part[cut:]
            if len(left)>1 and left[0]=='0':continue
            if right and right[-1]=='0':continue
            answer.append(left+('.'+right if right else ''))
        return answer
    return [f'({a}, {b})' for cut in range(1,len(digits)) for a in forms(digits[:cut]) for b in forms(digits[cut:])]
'''
COMMON='''\
def most_common_allowed_word(paragraph, banned):
    import re
    from collections import Counter
    blocked=set(banned);counts=Counter(word for word in re.findall(r'[a-z]+',paragraph.lower()) if word not in blocked)
    return counts.most_common(1)[0][0]
'''
ENCODING='''\
def shortest_word_encoding_length(words):
    remaining=set(words)
    for word in list(remaining):
        for index in range(1,len(word)):remaining.discard(word[index:])
    return sum(len(word)+1 for word in remaining)
'''
DISTANCE='''\
def shortest_character_distances(s, c):
    answer=[len(s)]*len(s);last=-len(s)
    for index,char in enumerate(s):
        if char==c:last=index
        answer[index]=index-last
    last=2*len(s)
    for index in range(len(s)-1,-1,-1):
        if s[index]==c:last=index
        answer[index]=min(answer[index],last-index)
    return answer
'''
FLIP='''\
def smallest_good_card_value(fronts, backs):
    forbidden={front for front,back in zip(fronts,backs) if front==back}
    return min((set(fronts)|set(backs))-forbidden,default=0)
'''
TREES='''\
def factored_binary_tree_count(arr):
    mod=10**9+7;values=set(arr);dp={}
    for root in sorted(arr):
        dp[root]=1+sum(dp[left]*dp[root//left] for left in dp if root%left==0 and root//left in dp)
    return sum(dp.values())%mod
'''
GOAT='''\
def to_goat_latin(sentence):
    answer=[]
    for index,word in enumerate(sentence.split(),1):
        if word[0].lower() not in 'aeiou':word=word[1:]+word[0]
        answer.append(word+'ma'+'a'*index)
    return ' '.join(answer)
'''
REQUESTS='''\
def friend_request_count(ages):
    counts=[0]*121
    for age in ages:counts[age]+=1
    return sum(counts[a]*(counts[b]-(a==b)) for a in range(1,121) for b in range(1,121) if not (b<=a*.5+7 or b>a or b>100>a))
'''
PROFIT='''\
def maximum_assignment_profit(difficulty, profit, worker):
    jobs=sorted(zip(difficulty,profit));answer=best=index=0
    for skill in sorted(worker):
        while index<len(jobs) and jobs[index][0]<=skill:best=max(best,jobs[index][1]);index+=1
        answer+=best
    return answer
'''
ISLAND='''\
def largest_island_after_flip(grid):
    size=len(grid);areas={0:0};label=2
    for row in range(size):
        for column in range(size):
            if grid[row][column]!=1:continue
            stack=[(row,column)];grid[row][column]=label;area=0
            while stack:
                r,c=stack.pop();area+=1
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<size and 0<=nc<size and grid[nr][nc]==1:grid[nr][nc]=label;stack.append((nr,nc))
            areas[label]=area;label+=1
    answer=max(areas.values())
    for row in range(size):
        for column in range(size):
            if grid[row][column]==0:answer=max(answer,1+sum(areas[x] for x in {grid[nr][nc] for nr,nc in ((row+1,column),(row-1,column),(row,column+1),(row,column-1)) if 0<=nr<size and 0<=nc<size}))
    return answer
'''
UNIQUE='''\
def unique_character_substring_sum(s):
    positions={};answer=0
    for index,char in enumerate(s):
        previous,last=positions.get(char,(-1,-1));answer+=(index-last)*(last-previous);positions[char]=(last,index)
    length=len(s)
    for previous,last in positions.values():answer+=(length-last)*(last-previous)
    return answer
'''
CONSECUTIVE='''\
def consecutive_sum_count(n):
    answer=0;length=1
    while length*(length-1)//2<n:
        remaining=n-length*(length-1)//2
        if remaining%length==0:answer+=1
        length+=1
    return answer
'''
GROUPS='''\
def large_group_positions(s):
    answer=[];start=0
    for end in range(1,len(s)+1):
        if end==len(s) or s[end]!=s[start]:
            if end-start>=3:answer.append([start,end-1])
            start=end
    return answer
'''
MASK='''\
def mask_personal_information(s):
    if '@' in s:
        name,domain=s.lower().split('@');return name[0]+'*****'+name[-1]+'@'+domain
    digits=''.join(char for char in s if char.isdigit());local='***-***-'+digits[-4:]
    return ('+'+'*'*(len(digits)-10)+'-' if len(digits)>10 else '')+local
'''
IMAGE='''\
def flip_and_invert_image(image):
    return [[value^1 for value in reversed(row)] for row in image]
'''

def lesson(a,b,c,d):return [a,b,c,d],d

BATCH={
808:entry('soup_serving_probability',[('n','int')],'float',['dynamic-programming','probability'],['Initially each soup has n ml; four equally likely operations serve multiples of 25 ml.','Return P(A empties first)+0.5*P(both empty together), within 1e-5.'],[([50],'The four first operations contribute outcomes 1, 1, 1, and one half, averaging 0.625.'),([0],'Both soups start empty, contributing one half.')],[[n] for n in (1,24,25,26,49,51,75,100,200,500,4800,5000)],SOUP,[SOUP.replace("if a<=0 and b<=0:return .5","if a<=0 and b<=0:return 1.0"),SOUP.replace('sum(solve(a-da,b-db)','sum(solve(a-db,b-da)')],['Counts a simultaneous emptying as a full A-first win.','Swaps the asymmetric serving amounts.'],soup_oracle,random_soup,*lesson('Serving amounts share a factor of 25, so rounded units preserve every state transition.','Memoize probabilities for remaining unit pairs and shortcut the converged large-n tail.','Apply four transitions; base cases return 1, 0, or 0.5 depending on which soup empties.','The recurrence conditions on the next equally likely operation and terminates as at least one amount decreases.'),'O((n/25)^2)','O((n/25)^2)',5),
809:entry('expressive_word_count',[('s','str'),('words','list[str]')],'int',['strings','two-pointers'],['Letters may be extended only when the target group has length at least three.','Count words that can become s by extending existing groups.'],[(['heeellooo',['hello','hi','helo']],'Only hello has matching groups and legal target group lengths.'),(['zzzzzyyyyy',['zzyy','zy','zyy']],'All three words can extend their z and y groups to length five.')],[[s,w] for s,w in (('a',['a']),('aaa',['a','aa','aaa']),('aa',['a']),('abb',['ab']),('heeellooo',['heeello']),('abc',['abc','ac']),('aabbcc',['abc']),('aaaab',['aab','ab']),('xyzzzz',['xyz','xyzz']),('mmmm',['m','mm']),('abcd',['abcd','abcde']),('aaabbb',['ab','aabb']))],EXPRESSIVE,[EXPRESSIVE.replace('y>=3','x>=3'),EXPRESSIVE.replace('x<y','x<=y')],['Checks the source group length instead of the target stretch length.','Allows equal groups through the stretch branch and masks other invalid logic.'],expressive_oracle,random_expressive,*lesson('Run characters must align, and only a target run of at least three may absorb extra copies.','Run-length encode target and candidate words.','Require equal group characters and either equal counts or target>=3 and source<target.','Groups cannot cross character boundaries, making these local conditions necessary and sufficient.'),'O(total characters)','O(longest word)',5),
811:entry('subdomain_visit_counts',[('cpdomains','list[str]')],'list[str]',['hash-maps','strings'],['Each input is count followed by a dot-separated domain.','Aggregate visits for each full domain and every suffix subdomain; output order is irrelevant.'],[([['9001 discuss.leetcode.com']],'All 9001 visits count for discuss.leetcode.com, leetcode.com, and com.'),([['900 google.mail.com','50 yahoo.com','1 intel.mail.com','5 wiki.org']],'Shared suffixes such as mail.com and com receive summed counts.')],[[x] for x in ((['1 a.com']),(['1 a.com','2 a.com']),(['3 com']),(['4 x.y.com']),(['1 a.b.c','2 b.c']),(['10 x.org','5 y.org']),(['7 a.io','8 b.io']),(['9 z']),(['1 a.com','1 b.com','1 com']),(['20 one.two','30 two']),(['5 a.b','6 c.b']),(['100 deep.sub.example.com']))],DOMAINS,[DOMAINS.replace('range(len(parts))','range(len(parts)-1)'),DOMAINS.replace("counts['.'.join(parts[index:])]+=int(amount)","counts[domain]+=int(amount)")],['Omits the top-level suffix.','Counts only the full domain.'],domains_oracle,random_domains,*lesson('A visit to a domain contributes once to every suffix beginning at a label boundary.','Split each counted domain and accumulate all joined suffixes.','For index in labels, counts[labels[index:]] += count.','Every valid subdomain is exactly one such suffix, so accumulation neither misses nor invents visits.'),'O(total labels)','O(distinct subdomains)',5),
812:entry('largest_triangle_area',[('points','list[list[int]]')],'float',['geometry','arrays'],['3 <= len(points) <= 50; coordinates are integers.','Return the maximum area of a triangle formed by any three points.'],[([[0,0],[0,1],[1,0],[0,2],[2,0]],'The right triangle with legs two has area two.'),([[1,0],[0,0],[0,1]],'A unit right triangle has area one half.')],[[p] for p in (([[0,0],[1,0],[0,1]]),([[0,0],[2,0],[0,2]]),([[0,0],[1,1],[2,2]]),([[-1,0],[1,0],[0,1]]),([[1,1],[2,3],[4,0]]),([[0,0],[3,0],[0,4]]),([[1,2],[3,4],[5,1],[0,0]]),([[-2,-2],[-2,2],[2,-2],[2,2]]),([[0,0],[1,0],[2,0],[0,3]]),([[5,5],[6,5],[5,6]]),([[0,1],[2,3],[4,1]]),([[-3,1],[2,-2],[4,5],[0,0]]))],TRIANGLE,[TRIANGLE.replace('/2',''),TRIANGLE.replace('abs(','(')],['Returns twice the geometric area.','Keeps signed orientation and may miss a larger clockwise triangle.'],triangle_oracle,random_triangle,*lesson('The cross-product magnitude of two side vectors equals twice the triangle area.','Enumerate every point triple and maximize absolute determinant divided by two.','area=abs((bx-ax)(cy-ay)-(by-ay)(cx-ax))/2.','Every candidate triangle appears once, and the determinant formula is orientation-independent after absolute value.'),'O(n^3)','O(1)',3),
813:entry('largest_average_sum',[('nums','list[int]'),('k','int')],'float',['dynamic-programming','arrays'],['1 <= k <= len(nums) <= 100; values are positive.','Split into at most k nonempty adjacent groups and maximize the sum of group averages.'],[([[9,1,2,3,9],3],'Splitting [9], [1,2,3], [9] gives 20.'),([[1,2,3,4,5,6,7],4],'An optimal four-part split gives 20.5.')],[[n,k] for n,k in (([1],1),([1,2],1),([1,2],2),([5,5,5],2),([1,2,3],2),([9,1,9],2),([1,10,1,10],3),([2,4,6,8],2),([10,1,1,1],2),([1,2,3,4,5],5),([4,3,2,1],3),([6,2,9,1,8],3))],AVERAGES,[AVERAGES.replace('range(2,k+1)','range(2,k)'),AVERAGES.replace('/(end-start)','//(end-start)')],['Uses only k-1 groups.','Uses integer division and loses fractional averages.'],averages_oracle,random_averages,*lesson('The final score is additive once the next partition boundary is chosen.','Use suffix DP for each allowed group count with prefix sums for O(1) averages.','dp[g][i]=max(avg(i,j)+dp[g-1][j]) over valid j.','Trying every first boundary covers every adjacent partition; positive values ensure using all k groups is never worse.'),'O(k*n^2)','O(n)',5),
816:entry('ambiguous_coordinates',[('s','str')],'list[str]',['strings','backtracking'],['s is parentheses around digits and contains no decimal point.','Insert one comma and optional decimal points without leading/trailing-zero violations.'],[(['(123)'],'The four valid coordinate renderings are (1, 2.3), (1, 23), (1.2, 3), and (12, 3).'),(['(00011)'],'Only (0, 0.011) and (0.001, 1) satisfy zero rules.')],[[s] for s in ('(12)','(000)','(100)','(101)','(001)','(1234)','(0102)','(1001)','(9999)','(12030)','(11111)','(90009)')],COORDINATES,[COORDINATES.replace("if len(left)>1 and left[0]=='0':continue",''),COORDINATES.replace("if right and right[-1]=='0':continue",'')],['Allows integer parts with leading zeros.','Allows fractional parts ending in zero.'],coordinates_oracle,random_coordinates,*lesson('Each numeric side has tightly defined zero rules independent of the comma split.','Enumerate comma positions and all valid renderings of each side.','For each decimal cut reject multi-digit leading zero and fractional trailing zero; combine valid sides.','Every output uniquely determines its comma and decimal cuts, so exhaustive valid combinations are complete and duplicate-free.'),'O(n^3)','O(n^3)',5),
819:entry('most_common_allowed_word',[('paragraph','str'),('banned','list[str]')],'str',['hash-maps','strings'],['Words compare case-insensitively and punctuation separates words.','Return the unique most frequent word not in banned.'],[(['Bob hit a ball, the hit BALL flew far after it was hit.',['hit']],'Ball occurs twice after normalization, more than every allowed word.'),(['a, a, a, a, b,b,b,c, c',['a']],'B occurs three times and is the most common allowed word.')],[[p,b] for p,b in (('a',[]),('A a b',[]),('a b b',['b']),('one, two! two',[]),('x.y x',['y']),('cat CAT dog',[]),('red blue red',['blue']),('hello-world hello',[]),('a;b;c;c',[]),('keep drop drop',['drop']),('word... WORD!',[]),('alpha beta gamma beta',['alpha']))],COMMON,[COMMON.replace('paragraph.lower()','paragraph'),COMMON.replace("re.findall(r'[a-z]+'","paragraph.split() if False else re.findall(r'[^ ]+'")],['Treats uppercase and lowercase forms separately.','Keeps punctuation attached to tokens.'],common_oracle,random_common,*lesson('Normalization determines which surface forms belong to the same word.','Lowercase, extract alphabetic runs, filter banned words, and count.','Counter(re.findall letters); delete blocked; return maximum count key.','The tokenizer removes every punctuation boundary and counting then directly implements the frequency rule.'),'O(paragraph length)','O(distinct words)',3),
820:entry('shortest_word_encoding_length',[('words','list[str]')],'int',['strings','hash-maps'],['Words contain lowercase letters.','Encode words as suffixes of # terminated strings and return minimum total reference length.'],[([['time','me','bell']],'Me is a suffix of time, so time#bell# has length ten.'),([['t']],'The encoding t# has length two.')],[[w] for w in ((['a']),(['a','a']),(['time','me']),(['me','time']),(['abc','bc','c']),(['abc','bcd']),(['bell','ell','ll']),(['x','yx','zyx']),(['cat','dog']),(['code','ode','de','e']),(['ab','ba']),(['long','ng','g','other']))],ENCODING,[ENCODING.replace('range(1,len(word))','range(2,len(word))'),ENCODING.replace('set(words)','words')],['Fails to remove one-character-shorter suffixes.','Does not deduplicate repeated words.'],encoding_oracle,random_encoding,*lesson('A word costs no extra space exactly when it is a suffix of another retained word.','Start with unique words and discard every proper suffix.','For each word discard word[i:] for i>=1; sum len+1 of survivors.','Every discarded word can point inside a survivor, while no survivor can share a terminating reference as another word’s suffix.'),'O(total squared word length)','O(total word length)',5),
821:entry('shortest_character_distances',[('s','str'),('c','str')],'list[int]',['two-pointers','strings'],['c occurs at least once in s.','Return each position’s distance to the nearest occurrence of c.'],[(['loveleetcode','e'],'The nearest e on either side yields [3,2,1,0,1,0,0,1,2,2,1,0].'),(['aaab','b'],'Distances decrease from three to zero approaching the final b.')],[[s,c] for s,c in (('a','a'),('ab','a'),('ab','b'),('aaa','a'),('abcba','a'),('abcba','c'),('bbbb','b'),('xayaz','a'),('leetcode','e'),('mississippi','i'),('01210','1'),('targetchar','r'))],DISTANCE,[DISTANCE.replace('last=2*len(s)','last=len(s)'),DISTANCE.replace('min(answer[index],last-index)','last-index')],['Initializes the right sentinel too close and underestimates leading distances.','Overwrites left distances instead of taking the nearer side.'],distance_oracle,random_distance,*lesson('Nearest distance is the minimum of nearest occurrences to the left and right.','Make one forward and one backward pass.','Store i-last_seen forward; backward replace with min(current,last_seen-i).','Each pass supplies the closest occurrence on its side, and their minimum is globally closest.'),'O(n)','O(n)',3),
822:entry('smallest_good_card_value',[('fronts','list[int]'),('backs','list[int]')],'int',['hash-maps','arrays'],['fronts and backs describe two sides of aligned cards.','After arbitrary flips, find the smallest front value absent from the back of every card showing it; return 0 if none.'],[([[1,2,4,4,7],[1,3,4,1,3]],'Values one and four are forbidden by equal-sided cards; two is the smallest remaining candidate.'),([[1],[1]],'The only value appears on both sides of its card and can never be made good.')],[[f,b] for f,b in (([1],[2]),([2],[1]),([1,2],[2,1]),([1,1],[1,2]),([2,3],[2,4]),([5,1,2],[3,1,4]),([1,2,3],[1,2,3]),([7,8],[9,10]),([3,3,4],[1,3,2]),([10,2,2],[1,2,3]),([4,5,4],[6,4,7]),([1,9,8,7],[2,9,6,5]))],FLIP,[FLIP.replace('if front==back','if front!=back'),FLIP.replace('-forbidden','&forbidden')],['Forbids values on unequal-sided cards instead of equal-sided cards.','Selects only forbidden candidates.'],flip_oracle,random_flip,*lesson('A value is impossible exactly when some card shows it on both sides.','Collect equal-side values as forbidden, then minimize all side values outside that set.','bad={front where front==back}; candidates=(fronts union backs)-bad.','Any allowed side value can be exposed by flipping its card, and forbidden values cannot be removed from their equal-sided card.'),'O(n)','O(n)',5),
823:entry('factored_binary_tree_count',[('arr','list[int]')],'int',['dynamic-programming','trees'],['arr contains distinct integers greater than one.','Each non-leaf equals the product of its children; count ordered binary trees modulo 1e9+7.'],[([[2,4]],'Trees are leaf 2, leaf 4, and root 4 with children 2 and 2.'),([[2,4,5,10]],'Seven trees arise, including both child orders for 2 and 5 under 10.')],[[a] for a in ([2],[2,4],[2,8],[2,4,8],[3,9],[2,3,6],[2,5,10],[2,4,16],[2,3,6,12],[3,5,15,45],[2,7,14,28],[2,3,4,6,12])],TREES,[TREES.replace('dp[left]*dp[root//left]','1'),TREES.replace('for left in dp','for left in list(dp)[:1]')],['Counts factor pairs but ignores the number of child subtrees.','Considers only the first possible left factor.'],factor_trees_oracle,random_factors,*lesson('Sorting ensures every factor child has already had its tree count computed.','For each root, add one leaf plus products of counts for every ordered factor pair.','dp[root]=1+sum(dp[a]*dp[root/a]) for factors present.','Choosing left and right subtree independently gives the product, and iterating every left factor includes both child orders.'),'O(n^2)','O(n)',5),
824:entry('to_goat_latin',[('sentence','str')],'str',['strings','simulation'],['Sentence words are separated by one space.','Vowel-starting words stay; consonant-starting words move first letter to end; append ma and position-count a characters.'],[(['I speak Goat Latin'],'The four transformed words are Imaa peaksmaaa oatGmaaaa atinLmaaaaa.'),(['The quick brown fox jumped over the lazy dog'],'Each word follows its starting-letter rule and receives one more a than the previous word.')],[[s] for s in ('a','b','Apple','Goat','I am','one two','Cat dog','x y z','under oak','Hello world','A e i o u','single Word Test')],GOAT,[GOAT.replace("word[0].lower() not in 'aeiou'","word[0].lower() in 'aeiou'"),GOAT.replace("'a'*index","'a'")],['Applies the consonant rotation to vowel-starting words.','Appends only one a regardless of word position.'],goat_oracle,random_goat,*lesson('Each word transforms independently except for its one-based position suffix.','Enumerate words, conditionally rotate the first character, and append ma plus repeated a.','If consonant use word[1:]+word[0]; append ma+a*index.','The construction directly applies every rule in original word order.'),'O(sentence length)','O(sentence length)',3),
825:entry('friend_request_count',[('ages','list[int]')],'int',['counting','arrays'],['1 <= age <= 120.','Count directed requests where recipient age b is not <=0.5a+7, not >a, and not >100 when a<100.'],[([[16,16]],'Each sixteen-year-old may request the other, producing two directed requests.'),([[16,17,18]],'The valid directed requests total two.')],[[a] for a in ([14],[15,15],[16,16,16],[20,30],[20,20,30],[99,100,101],[101,100],[120,120],[1,2,3],[18,17,16],[30,20,20],[50,50,51,52])],REQUESTS,[REQUESTS.replace('b<=a*.5+7','b<a*.5+7'),REQUESTS.replace('counts[b]-(a==b)','counts[b]')],['Uses a strict lower-age cutoff and admits boundary recipients.','Counts requests to oneself.'],requests_oracle,random_ages,*lesson('Only ages matter, so aggregate people into 120 buckets.','Test each sender-age/receiver-age pair once and multiply their frequencies.','For every legal a,b add count[a]*(count[b]-(a==b)).','Frequency multiplication counts all directed person pairs, and subtracting same-person choices handles equal ages.'),'O(120^2+n)','O(120)',5),
826:entry('maximum_assignment_profit',[('difficulty','list[int]'),('profit','list[int]'),('worker','list[int]')],'int',['sorting','greedy'],['Jobs may be reused by multiple workers; each worker chooses one job at or below ability.','Return maximum total profit.'],[([[2,4,6,8,10],[10,20,30,40,50],[4,5,6,7]],'Workers earn 20,20,30,30 for total 100.'),([[85,47,57],[24,66,99],[40,25,25]],'No worker can perform any listed job, so profit is zero.')],[[d,p,w] for d,p,w in (([1],[5],[1]),([2],[5],[1]),([1],[5],[1,2]),([1,2],[10,5],[2]),([2,4],[5,10],[3]),([5,1],[100,1],[1,5]),([1,3,5],[2,10,9],[5]),([2,4,6],[5,6,7],[1,3,7]),([10],[50],[10,10]),([3,8],[20,100],[7]),([1,100],[1,1000],[50]),([2,2],[3,5],[2]))],PROFIT,[PROFIT.replace('best=max(best,jobs[index][1])','best=jobs[index][1]'),PROFIT.replace('for skill in sorted(worker)','for skill in worker')],['Uses the most recent feasible job rather than best profit when profits are nonmonotone.','Scans unsorted worker abilities with a one-way job pointer.'],profit_oracle,random_profit,*lesson('As worker ability increases, the set of feasible jobs only grows.','Sort jobs and workers; sweep once while maintaining best feasible profit.','Advance jobs with difficulty<=skill, update best, and add best for each worker.','The running maximum summarizes every feasible job, and job reuse makes worker choices independent.'),'O((jobs+workers) log n)','O(jobs)',5),
827:entry('largest_island_after_flip',[('grid','list[list[int]]')],'int',['matrices','depth-first-search'],['grid is square and contains zeros and ones.','Change at most one zero to one and return the largest four-connected island area.'],[([[[1,0],[0,1]]],'Flipping either zero joins both diagonal land cells through the new cell, giving area three.'),([[[1,1],[1,0]]],'Flipping the final zero fills the 2-by-2 island for area four.')],[[g] for g in ([[0]],[[1]],[[0,0],[0,0]],[[1,1],[1,1]],[[1,0],[1,0]],[[1,0,1],[0,0,0],[1,0,1]],[[1,1,0],[0,1,0],[0,0,1]],[[0,1,0],[1,0,1],[0,1,0]],[[1,1,1],[1,0,1],[1,1,1]],[[1,0,0],[1,1,0],[0,0,1]],[[0,0,1],[0,1,1],[1,0,0]],[[1,0,1,0],[1,0,1,1],[0,0,0,1],[1,1,0,0]])],ISLAND,[ISLAND.replace("{grid[nr][nc] for nr,nc","[grid[nr][nc] for nr,nc"),ISLAND.replace('answer=max(answer,1+sum','answer=max(answer,sum')],['Counts the same neighboring island more than once.','Forgets to include the flipped cell itself.'],island_oracle,random_island,*lesson('A flipped zero joins each distinct neighboring island once.','Label existing islands and store their areas, then evaluate every zero.','Candidate=1+sum(area[label] for distinct adjacent labels).','Labels make connectivity explicit and the set prevents double-counting one island touching from multiple sides.'),'O(n^2)','O(n^2)',8),
828:entry('unique_character_substring_sum',[('s','str')],'int',['dynamic-programming','strings'],['1 <= len(s) <= 100,000; s contains uppercase letters.','For every substring count characters occurring exactly once, then sum those counts modulo 1e9+7.'],[(['ABC'],'Substring contributions total ten.'),(['ABA'],'The contributions are one, one, one, two, two, and one, totaling eight.')],[[s] for s in ('A','AA','AB','AAA','AAB','ABB','ABCA','ABCDE','ABCABC','AAAAA','BANANA','LEETCODE')],UNIQUE,[UNIQUE.replace('(index-last)*(last-previous)','(index-previous)'),UNIQUE.replace('(length-last)*(last-previous)','(length-last)')],['Uses total span rather than the product of independent left/right boundary choices.','Counts only suffix distance for final occurrences.'],unique_oracle,random_unique,*lesson('An occurrence contributes to substrings whose left boundary follows its previous occurrence and right boundary precedes its next.','Finalize each occurrence when the next same character arrives, plus a sentinel finalization.','Add (current-last)*(last-previous) for each character occurrence.','The two factors independently count legal left and right boundaries where that occurrence is unique.'),'O(n)','O(alphabet)',8),
829:entry('consecutive_sum_count',[('n','int')],'int',['math','two-pointers'],['1 <= n <= 1,000,000,000.','Count representations of n as one or more consecutive positive integers.'],[([5],'Five equals 5 and 2+3, giving two representations.'),([9],'Nine equals 9, 4+5, and 2+3+4.')],[[n] for n in (1,2,3,4,6,8,10,15,21,100,999,1000000000)],CONSECUTIVE,[CONSECUTIVE.replace('remaining%length==0','remaining%length!=0'),CONSECUTIVE.replace('range(1,n+1)','range(2,n+1)')],['Counts nondivisible lengths instead of valid starting integers.','A stale brute-force variant omits the one-term representation.'],consecutive_oracle,random_consecutive,*lesson('A length-L sequence sums to L*start+L(L-1)/2.','Enumerate feasible lengths and test whether the remaining amount is a positive multiple of length.','While triangular offset<n, increment when (n-offset)%length==0.','The equation yields exactly one positive start per feasible length, so every representation is counted once.'),'O(sqrt(n))','O(1)',8),
830:entry('large_group_positions',[('s','str')],'list[list[int]]',['strings','two-pointers'],['s contains lowercase letters.','Return [start,end] for every maximal run of at least three equal characters.'],[(['abbxxxxzzy'],'Only xxxx is a large group, spanning indices three through six.'),(['abcdddeeeeaabbbcd'],'The large groups are ddd, eeee, and bbb.')],[[s] for s in ('a','aaa','aa','aaaa','abbb','bbba','abbba','aabbcc','aaabbb','abc','zzzyyyx','aabccccdd')],GROUPS,[GROUPS.replace('>=3','>3'),GROUPS.replace('[start,end-1]','[start,end]')],['Requires four characters and misses length-three groups.','Returns an exclusive end index instead of inclusive.'],groups_oracle,random_groups,*lesson('A maximal run ends when the next character differs or the string ends.','Track its start and emit boundaries when its length reaches three.','At each boundary, if end-start>=3 append [start,end-1], then reset start.','Every maximal run is inspected exactly once and inclusive indices follow directly from the exclusive scan endpoint.'),'O(n)','O(output)',3),
831:entry('mask_personal_information',[('s','str')],'str',['strings','simulation'],['Input is an email or a phone number with punctuation.','Lowercase email and mask its name; phone keeps last four digits and masks country/local digits in the required format.'],[(['LeetCode@LeetCode.com'],'The lowercase email name becomes l*****e and the domain remains lowercase.'),(['86-(10)12345678'],'Twelve digits use country prefix +**- and local mask ***-***-5678.')],[[s] for s in ('a@b.com','AB@CD.COM','name@example.org','1(234)567-8900','1234567890','+1 (234) 567-8900','+(501) 123-4567','12 345 678 9012','86-(10)12345678','X@y.Z','9999999999999','(000)000-0000')],MASK,[MASK.replace("name[0]+'*****'+name[-1]","name[:2]+'*****'+name[-1]"),MASK.replace("digits[-4:]","digits[:4]")],['Exposes two leading email characters.','Keeps the first four phone digits instead of the last four.'],mask_oracle,random_mask,*lesson('Email and phone formats are distinguished by @, and phones depend only on normalized digit count.','Normalize case or digits, then apply the fixed mask template.','Email: first+*****+last@domain; phone: optional country mask plus ***-***-last4.','Normalization removes irrelevant punctuation while each template reveals exactly the allowed characters.'),'O(len(s))','O(len(s))',5),
832:entry('flip_and_invert_image',[('image','list[list[int]]')],'list[list[int]]',['matrices','two-pointers'],['image is a rectangular binary matrix.','Reverse each row horizontally, then invert every bit.'],[([[[1,1,0],[1,0,1],[0,0,0]]],'Reversing rows and toggling bits produces [[1,0,0],[0,1,0],[1,1,1]].'),([[[1,1,0,0],[1,0,0,1],[0,1,1,1],[1,0,1,0]]],'Each row is independently reversed and inverted.')],[[g] for g in ([[0]],[[1]],[[0,1]],[[1,0]],[[0],[1]],[[1,1],[0,0]],[[1,0],[0,1]],[[1,1,1]],[[0,1,0]],[[1,0,1],[0,1,0]],[[0,0,1],[1,1,0]],[[1,0,0,1],[0,1,1,0]])],IMAGE,[IMAGE.replace('reversed(row)','row'),IMAGE.replace('1-value','value')],['Inverts without flipping rows.','Flips without inverting bits.'],image_oracle,random_image,*lesson('Flip and invert act independently on each output position.','Traverse each row in reverse order and toggle with XOR one.','Return [[value^1 for value in reversed(row)] for row in image].','Reversed iteration supplies the horizontal mirror and XOR maps binary zero/one exactly to its complement.'),'O(rows*columns)','O(rows*columns)',3),
}

for source_id in (808,812,813):BATCH[source_id]['comparator']='float'
for source_id in (811,816):BATCH[source_id]['comparator']='unordered'

BATCH[809]['wrong'][1]=EXPRESSIVE.replace('y>=3','y>=2')
BATCH[812]['examples'][0]=([[[0,0],[0,1],[1,0],[0,2],[2,0]]],
                           'The right triangle with legs two has area two.')
BATCH[812]['examples'][1]=([[[1,0],[0,0],[0,1]]],
                           'A unit right triangle has area one half.')
BATCH[819]['boundaries'].append(['red, red! red? blue blue',[]])
BATCH[819]['wrong'][1]='''\
def most_common_allowed_word(paragraph, banned):
    from collections import Counter
    counts=Counter(word.lower() for word in paragraph.split() if word.lower() not in set(banned))
    return counts.most_common(1)[0][0]
'''
BATCH[820]['wrong'][1]='''\
def shortest_word_encoding_length(words):
    remaining=list(words)
    for word in list(remaining):
        for index in range(1,len(word)):
            suffix=word[index:]
            if suffix in remaining:remaining.remove(suffix)
    return sum(len(word)+1 for word in remaining)
'''
BATCH[826]['boundaries'].append([[1,10],[1,100],[10,1]])
BATCH[827]['wrong'][0]='''\
def largest_island_after_flip(grid):
    size=len(grid);areas={0:0};label=2
    for row in range(size):
        for column in range(size):
            if grid[row][column]!=1:continue
            stack=[(row,column)];grid[row][column]=label;area=0
            while stack:
                r,c=stack.pop();area+=1
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<size and 0<=nc<size and grid[nr][nc]==1:grid[nr][nc]=label;stack.append((nr,nc))
            areas[label]=area;label+=1
    answer=max(areas.values())
    for row in range(size):
        for column in range(size):
            if grid[row][column]==0:
                neighbors=[grid[nr][nc] for nr,nc in ((row+1,column),(row-1,column),(row,column+1),(row,column-1)) if 0<=nr<size and 0<=nc<size]
                answer=max(answer,1+sum(areas[item] for item in neighbors))
    return answer
'''
BATCH[829]['wrong'][1]='''\
def consecutive_sum_count(n):
    answer=0;length=2
    while length*(length-1)//2<n:
        remaining=n-length*(length-1)//2
        if remaining%length==0:answer+=1
        length+=1
    return answer
'''
BATCH[832]['wrong'][1]='''\
def flip_and_invert_image(image):
    return [list(reversed(row)) for row in image]
'''
