"""Grid routes, corner word squares, binary costs, merge DP, and sheet painting."""
from functools import lru_cache
from itertools import permutations
from math import isqrt
from heapq import heappop,heappush
from .import_batch_055 import entry


MOD=1000000007

def routes_oracle(args):
    grid,d=args;n=len(grid);m=len(grid[0])
    @lru_cache(None)
    def paths(row,col,used_horizontal):
        answer=int(row==0)
        if not used_horizontal:
            for nxt in range(m):
                if nxt!=col and grid[row][nxt]=='.' and abs(nxt-col)<=d:answer+=paths(row,nxt,True)
        if row:
            for nxt in range(m):
                if grid[row-1][nxt]=='.' and 1+(nxt-col)**2<=d*d:answer+=paths(row-1,nxt,False)
        return answer
    return sum(paths(n-1,col,False) for col in range(m) if grid[n-1][col]=='.')%MOD

def random_routes(rng):
    n=rng.randint(1,4);m=rng.randint(1,5)
    return [[''.join(rng.choice('.#') for _ in range(m)) for _ in range(n)],rng.randint(1,5)]

def squares_oracle(args):
    answer=[]
    for top,left,right,bottom in permutations(args[0],4):
        if top[0]==left[0] and top[3]==right[0] and bottom[0]==left[3] and bottom[3]==right[3]:answer.append([top,left,right,bottom])
    return sorted(answer)

def random_squares(rng):
    words=set()
    while len(words)<rng.randint(4,8):words.add(''.join(rng.choice('abc') for _ in range(4)))
    return [list(words)]

def binary_cost_oracle(args):
    s,t,flip,swap,cross=args;start=(s,t);queue=[(0,start)];distance={start:0};n=len(s)
    while queue:
        cost,state=heappop(queue)
        if cost!=distance[state]:continue
        a,b=state
        if a==b:return cost
        candidates=[]
        for i in range(n):
            candidates.append((a[:i]+('1' if a[i]=='0' else '0')+a[i+1:],b,flip))
            candidates.append((a,b[:i]+('1' if b[i]=='0' else '0')+b[i+1:],flip))
            aa=list(a);bb=list(b);aa[i],bb[i]=bb[i],aa[i];candidates.append((''.join(aa),''.join(bb),cross))
        for i in range(n):
            for j in range(i+1,n):
                aa=list(a);aa[i],aa[j]=aa[j],aa[i];candidates.append((''.join(aa),b,swap))
                bb=list(b);bb[i],bb[j]=bb[j],bb[i];candidates.append((a,''.join(bb),swap))
        for aa,bb,price in candidates:
            nxt=(aa,bb);new=cost+price
            if new<distance.get(nxt,10**30):distance[nxt]=new;heappush(queue,(new,nxt))

def random_binary_cost(rng):
    n=rng.randint(1,5);return [''.join(rng.choice('01') for _ in range(n)),''.join(rng.choice('01') for _ in range(n)),rng.randint(1,10),rng.randint(1,10),rng.randint(1,10)]

def merge_two(a,b):return tuple(sorted(a+b))
def merge_cost_oracle(args):
    start=tuple(sorted(tuple(item) for item in args[0]))
    @lru_cache(None)
    def solve(state):
        if len(state)==1:return 0
        answer=10**30
        for i in range(len(state)):
            for j in range(i+1,len(state)):
                a,b=state[i],state[j];merged=merge_two(a,b);median_a=a[(len(a)-1)//2];median_b=b[(len(b)-1)//2]
                nxt=tuple(sorted([state[k] for k in range(len(state)) if k not in (i,j)]+[merged]))
                answer=min(answer,len(a)+len(b)+abs(median_a-median_b)+solve(nxt))
        return answer
    return solve(start)

def random_merge(rng):
    lists=[]
    for _ in range(rng.randint(2,6)):lists.append(sorted(rng.randint(-10,10) for _ in range(rng.randint(1,5))))
    return [lists]

def paint_oracle(args):
    n,limit=args
    return sum(1 for first in range(len(limit)) for second in range(len(limit)) if first!=second for split in range(1,n) if split<=limit[first] and n-split<=limit[second])%MOD
def random_paint(rng):return [rng.randint(2,30),[rng.randint(1,30) for _ in range(rng.randint(2,12))]]


ROUTES='''def count_grid_climbing_routes(grid,d):
    from math import isqrt
    mod=1000000007;n=len(grid);m=len(grid[0])
    def window(values,radius):
        prefix=[0]
        for value in values:prefix.append((prefix[-1]+value)%mod)
        return [(prefix[min(m,i+radius+1)]-prefix[max(0,i-radius)])%mod for i in range(m)]
    first=[1 if grid[-1][col]=='.' else 0 for col in range(m)]
    vertical=isqrt(d*d-1)
    for row in range(n-1,-1,-1):
        nearby=window(first,d)
        second=[(nearby[col]-first[col])%mod if grid[row][col]=='.' else 0 for col in range(m)]
        total=[(first[col]+second[col])%mod for col in range(m)]
        if row==0:return sum(total)%mod
        upward=window(total,vertical)
        first=[upward[col] if grid[row-1][col]=='.' else 0 for col in range(m)]
'''

SQUARES='''def word_squares_corners(words):
    answer=[]
    for top in words:
        for left in words:
            if left==top or left[0]!=top[0]:continue
            for right in words:
                if right in (top,left) or right[0]!=top[3]:continue
                for bottom in words:
                    if bottom in (top,left,right):continue
                    if bottom[0]==left[3] and bottom[3]==right[3]:answer.append([top,left,right,bottom])
    return sorted(answer)
'''

BINARY='''def minimum_binary_strings_equal_cost(s,t,flip_cost,swap_cost,cross_cost):
    counts=[0,0]
    for left,right in zip(s,t):
        if left!=right:counts[int(left)]+=1
    low=min(counts);high=max(counts);answer=(low+high)*flip_cost
    answer=min(answer,low*swap_cost+(high-low)*flip_cost)
    paired=(low+high)//2
    answer=min(answer,(paired-low)*cross_cost+paired*swap_cost+(low+high-2*paired)*flip_cost)
    return answer
'''

MERGE='''def minimum_sorted_lists_merge_cost(lists):
    from bisect import bisect_right
    count=len(lists);size=1<<count;length=[0]*size;median=[0]*size;merged=[() for _ in range(size)]
    def combine(a,b):
        answer=[];i=j=0
        while i<len(a) and j<len(b):
            if a[i]<=b[j]:answer.append(a[i]);i+=1
            else:answer.append(b[j]);j+=1
        answer.extend(a[i:]);answer.extend(b[j:]);return tuple(answer)
    for mask in range(1,size):
        bit=mask&-mask;index=bit.bit_length()-1;rest=mask^bit
        merged[mask]=combine(merged[rest],tuple(lists[index]));length[mask]=len(merged[mask]);median[mask]=merged[mask][(length[mask]-1)//2]
    dp=[10**30]*size
    for mask in range(1,size):
        if mask&(mask-1)==0:dp[mask]=0;continue
        anchor=mask&-mask;part=(mask-1)&mask
        while part:
            other=mask^part
            if part&anchor and other:dp[mask]=min(dp[mask],dp[part]+dp[other]+length[mask]+abs(median[part]-median[other]))
            part=(part-1)&mask
    return dp[-1]
'''

PAINT='''def count_two_color_sheet_paintings(n,limit):
    from bisect import bisect_left
    caps=sorted(min(value,n-1) for value in limit);prefix=[0]
    for value in caps:prefix.append(prefix[-1]+value)
    answer=0;count=len(caps)
    for value in caps:
        index=bisect_left(caps,n-value);eligible=count-index
        answer+=eligible*(value-n+1)+(prefix[count]-prefix[index])
        if 2*value>=n:answer-=2*value-n+1
    return answer%1000000007
'''

def lesson(a,b,c,d):return [a,b,c,d]

R_CASES=[[g,d] for g,d in ((['#'],1),(['.'],1),(['..'],1),(['..','#.'],1),(['..','#.'],2),(['...'],2),(['.#.','...'],1),(['...','...'],1),(['...','...'],2),(['.#','..','..'],2),(['....','.#..','..#.'],2),(['#..','...','..#'],3),(['..#..','.#...','...#.'],2),(['....','####','....'],4))]
Q_CASES=[[[*w]] for w in (['able','area','echo','also'],['code','cafe','eden','edge'],['aaaa','aaab','aaba','abaa'],['abca','axxb','byyc','czzc'],['abcd','aqqb','drrc','bssc'],['aaaa','baaa','abaa','aaba'],['abcz','axxy','ywwq','zppq'],['mnop','mxxq','pyyr','qzzr'],['test','team','moon','time'],['aaaa','bbbb','cccc','dddd'],['abca','addb','ceef','bggf'],['xyza','xppa','aqqa','arra'],['noon','name','echo','nest','memo'],['abcd','abce','dbbf','ecfg','fghi'])]
E_CASES=[[s,t,a,b,c] for s,t,a,b,c in (('0','0',1,1,1),('0','1',3,2,1),('01000','10111',10,2,2),('001','110',2,100,100),('1010','1010',5,5,5),('01','10',10,3,7),('00','11',8,5,1),('000','111',4,3,2),('0101','1010',7,2,9),('0011','1100',9,8,1),('10101','00110',6,4,3),('11100','00011',2,10,1),('010101','101010',20,3,4),('000111','111000',5,7,2))]
M_CASES=[[[*map(list,v)]] for v in (([1],[3]),([1],[1]),([1,3,5],[2,4],[6,7,8]),([1,1,5],[1,4,7,8]),([1,2],[3,4],[5,6]),([-5,-1],[0],[2,9]),([1],[2],[3],[4]),([1,10],[2,9],[3,8],[4,7]),([0,0],[0,0],[0]),([-10,-5,-1],[-8,-2],[4,6]),([1,2,100],[3,4],[5],[6,7]),([-3],[-2,-1],[0,1,2],[8]),([1,1,1],[2,2],[3,3,3],[4]),([-20,-10],[0,10],[20,30],[40,50]))]
P_CASES=[[n,a] for n,a in ((2,[1,1]),(3,[1,2]),(3,[2,2]),(4,[3,1,2]),(5,[1,1]),(5,[4,4]),(6,[2,3,4]),(7,[6,1,5]),(10,[10,10,10]),(10,[3,7,9,2]),(20,[5,15,20]),(30,[30,1,29,15]),(100,[50,50,100]),(12,[1,2,3,4,5,6]))]

BATCH={
3797:entry('count_grid_climbing_routes',[('grid','list[str]'),('d','int')],'int',['matrices','dynamic programming','prefix sums'],['grid has at most 750 rows and columns; dots are available and hashes blocked.','A move stays on its row or goes one row up, with Euclidean distance at most d.','At most one consecutive same-row move is allowed; routes start on the bottom and end on the top.'],[([['..','#.'],1],'From the sole bottom hold, climb directly or first use the other top-row hold, giving two routes.'),([['..'],1],'Either cell alone is a route, and each ordered move between the two cells is another, giving four.')],R_CASES,ROUTES,[ROUTES.replace('(nearby[col]-first[col])%mod','nearby[col]%mod'),ROUTES.replace('vertical=isqrt(d*d-1)','vertical=d')],['Allows a same-row move that stays on the same cell.','Uses horizontal reach d for an upward move, ignoring its mandatory vertical distance one.'],routes_oracle,random_routes,lesson('Within each row, distinguish arriving/starting at a first hold from taking the optional second hold.','Prefix-sum windows count horizontal destinations within d; subtract the same cell because a move must change cells.','Combine one- and two-hold routes, then move upward using horizontal radius floor(sqrt(d²-1)).','These two states enforce at most one horizontal move per row, and every legal route has a unique sequence of first and optional second holds.'),'O(nm)','O(m)',8),
3799:entry('word_squares_corners',[('words','list[str]')],'list[list[str]]',['strings','backtracking','enumeration'],['words contains 4 to 15 distinct lowercase strings of length four.','Choose four distinct words as top, left, right, and bottom.','All four corner characters must agree and results are lexicographically sorted.'],[([['able','area','echo','also']],'The two valid ordered quadruples satisfy all four corner equalities.'),([['code','cafe','eden','edge']],'No four distinct words satisfy every required corner.')],Q_CASES,SQUARES,[SQUARES.replace('if left==top or left[0]!=top[0]:continue','if left[0]!=top[0]:continue'),SQUARES.replace('return sorted(answer)','return answer')],['Allows the same word to serve as both top and left.','Returns discovery order rather than the required lexicographic order.'],squares_oracle,random_squares,lesson('Only the four corner characters constrain the square.','Choose top and left sharing their first character, then right beginning with top’s last character.','Choose a distinct bottom whose first and last characters match the lower ends of left and right, then sort results.','The nested choices enumerate every ordered role assignment exactly once, and the four tests are precisely the definition.'),'O(w⁴)','O(r)',5),
3800:entry('minimum_binary_strings_equal_cost',[('s','str'),('t','str'),('flip_cost','int'),('swap_cost','int'),('cross_cost','int')],'int',['strings','greedy'],['s and t are equal-length binary strings of length up to 100,000.','A flip changes one bit; a swap exchanges two positions within one string; a cross swap exchanges s[i] and t[i].','All costs are positive; return the minimum cost to make the strings equal.'],[(['01000','10111',10,2,2],'Pairing opposite mismatch types with swaps, converting a pair with a cross swap, and flipping the leftover costs sixteen.'),(['001','110',2,100,100],'Three independent flips cost six and beat either swap operation.')],E_CASES,BINARY,[BINARY.replace('answer=min(answer,low*swap_cost+(high-low)*flip_cost)','').replace('answer=min(answer,(paired-low)*cross_cost+paired*swap_cost+(low+high-2*paired)*flip_cost)',''),BINARY.replace('answer=min(answer,(paired-low)*cross_cost+paired*swap_cost+(low+high-2*paired)*flip_cost)','')],['Uses flips only and ignores both kinds of swap.','Ignores cross swaps that convert excess mismatches into pairable types.'],binary_cost_oracle,random_binary_cost,lesson('Mismatches have two types: s=0,t=1 or s=1,t=0; positions within a type are otherwise interchangeable.','A normal swap fixes one mismatch of each type, while a cross swap converts one type into the other and a flip fixes one mismatch.','Compare all flips, pair opposite types then flip excess, and cross-convert enough excess to maximize swap pairs.','Any operation sequence reduces to counts of these three actions; within each linear region the cheapest count occurs at one of these boundary plans.'),'O(n)','O(1)',6),
3801:entry('minimum_sorted_lists_merge_cost',[('lists','list[list[int]]')],'int',['arrays','bitmask dynamic programming','binary search'],['2≤len(lists)≤12; every list is nonempty and sorted.','Merge cost is combined length plus the absolute difference of the two left-middle medians.','Repeatedly merge until one sorted list remains with minimum total cost.'],[([[[1,3,5],[2,4],[6,7,8]]],'Merging the first two costs six, then merging with the third costs twelve, totaling eighteen.'),([[[1],[3]]],'The sole merge costs length two plus median difference two, totaling four.')],M_CASES,MERGE,[MERGE.replace('+abs(median[part]-median[other])',''),MERGE.replace('(length[mask]-1)//2','length[mask]//2')],['Ignores the median-difference component of every merge.','Uses the right middle value for even-length merged lists.'],merge_cost_oracle,random_merge,lesson('Every intermediate merged list corresponds only to a subset of original lists, regardless of merge order.','Precompute the sorted union, length, and left-middle median for every subset.','Subset DP splits each mask into two nonempty parts and adds their optimal costs plus the final merge cost.','The last merge of any merge tree partitions its leaves into two subsets, so considering every partition proves optimal substructure.'),'O(3^k+2^kN)','O(2^kN)',8),
3802:entry('count_two_color_sheet_paintings',[('n','int'),('limit','list[int]')],'int',['arrays','sorting','binary search'],['2≤n≤10^9 and there are up to 100,000 colors.','Use exactly two distinct colors, each on one nonempty contiguous segment.','Color i may cover at most limit[i] sheets; return ordered paintings modulo 1,000,000,007.'],[([4,[3,1,2]],'Across ordered color pairs, six split positions satisfy both capacity limits.'),([3,[2,2]],'Either color may come first and either split position works, giving four.')],P_CASES,PAINT,[PAINT.replace('if 2*value>=n:answer-=2*value-n+1',''),PAINT.replace('return answer%1000000007','return answer//2%1000000007')],['Allows the same color to occupy both segments.','Treats the ordered left/right color roles as an unordered pair.'],paint_oracle,random_paint,lesson('Cap every color at n-1 because both segments must be nonempty.','For ordered capacities a and b, valid splits count max(0,a+b-n+1).','Sort capacities; for each a, binary-search the suffix with b≥n-a and sum the linear expression using prefix sums, then remove the same-color term.','Every painting has a unique ordered color pair and split, so summing this exact count covers each valid painting once.'),'O(m log m)','O(m)',8),
}
