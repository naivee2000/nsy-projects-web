"""Palindrome removal, closed islands, word subsets, region ancestry, and noncrossing matchings."""
from functools import lru_cache
from itertools import combinations
from math import comb
from .import_batch_055 import entry

def removal_o(a):
    start=tuple(a[0])
    @lru_cache(None)
    def solve(values):
        if not values:return 0
        best=len(values)
        for left in range(len(values)):
            for right in range(left+1,len(values)+1):
                block=values[left:right]
                if block==block[::-1]:best=min(best,1+solve(values[:left]+values[right:]))
        return best
    return solve(start)
def rremoval(r):return [[r.randint(1,4) for _ in range(r.randint(1,8))]]

def closed_o(a):
    grid=a[0];rows=len(grid);cols=len(grid[0]);seen=set();answer=0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] or (i,j) in seen:continue
            component={(i,j)};seen.add((i,j));todo=[(i,j)];touches=False
            while todo:
                x,y=todo.pop();touches|=x in (0,rows-1) or y in (0,cols-1)
                for p,q in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0<=p<rows and 0<=q<cols and not grid[p][q] and (p,q) not in seen:seen.add((p,q));component.add((p,q));todo.append((p,q))
            answer+=not touches
    return answer
def rclosed(r):
    rows,cols=r.randint(2,7),r.randint(2,7);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]

def score_o(a):
    words,letters,scores=a;available={c:letters.count(c) for c in set(letters)};best=0
    for mask in range(1<<len(words)):
        text=''.join(words[i] for i in range(len(words)) if mask>>i&1)
        if all(text.count(c)<=available.get(c,0) for c in set(text)):best=max(best,sum(scores[ord(c)-97] for c in text))
    return best
def rscore(r):
    words=[''.join(r.choice('abcde') for _ in range(r.randint(1,5))) for _ in range(r.randint(1,9))];letters=[r.choice('abcde') for _ in range(r.randint(1,15))];scores=[r.randint(0,5) for _ in range(26)];return [words,letters,scores]

def region_o(a):
    regions,left,right=a;parent={child:group[0] for group in regions for child in group[1:]};ancestors=[]
    while left in parent:ancestors.append(left);left=parent[left]
    ancestors.append(left);wanted=set(ancestors)
    while right not in wanted:right=parent[right]
    return right
def rregion(r):
    n=r.randint(3,12);names=[f'r{i}' for i in range(n)];groups=[]
    for child in range(1,n):groups.append([names[r.randrange(child)],names[child]])
    return [groups,r.choice(names),r.choice(names)]

def hand_o(a):
    people=a[0];pairs=people//2
    if people>12:return comb(2*pairs,pairs)//(pairs+1)
    def match(remaining,pairs_so_far):
        if not remaining:return 1
        first=remaining[0];answer=0
        for i in range(1,len(remaining)):
            second=remaining[i]
            if any((a<first<b<second) or (first<a<second<b) for a,b in pairs_so_far):continue
            answer+=match(remaining[1:i]+remaining[i+1:],pairs_so_far+[(first,second)])
        return answer
    return match(tuple(range(people)),[])
def rhand(r):return [2*r.randint(1,5)]

REMOVAL='''def minimum_palindrome_removals(arr):
    n=len(arr);dp=[[0]*n for _ in range(n)]
    for left in range(n-1,-1,-1):
        dp[left][left]=1
        for right in range(left+1,n):
            dp[left][right]=1+dp[left+1][right]
            if arr[left]==arr[left+1]:dp[left][right]=min(dp[left][right],1+(dp[left+2][right] if left+2<=right else 0))
            for middle in range(left+2,right+1):
                if arr[left]==arr[middle]:dp[left][right]=min(dp[left][right],dp[left+1][middle-1]+(dp[middle+1][right] if middle<right else 0))
    return dp[0][n-1]
'''
CLOSED='''def count_closed_islands(grid):
    rows,cols=len(grid),len(grid[0])
    def flood(row,col):
        if not (0<=row<rows and 0<=col<cols):return False
        if grid[row][col]:return True
        grid[row][col]=1
        return flood(row+1,col) & flood(row-1,col) & flood(row,col+1) & flood(row,col-1)
    return sum(flood(i,j) for i in range(rows) for j in range(cols) if grid[i][j]==0)
'''
SCORE='''def maximum_word_score(words,letters,score):
    available=[0]*26
    for char in letters:available[ord(char)-97]+=1
    best=0
    def visit(index,total):
        nonlocal best
        if index==len(words):best=max(best,total);return
        visit(index+1,total);used=[];gain=0
        for char in words[index]:
            place=ord(char)-97;available[place]-=1;used.append(place);gain+=score[place]
        if all(available[place]>=0 for place in used):visit(index+1,total+gain)
        for place in used:available[place]+=1
    visit(0,0);return best
'''
REGION='''def smallest_common_region(regions,region1,region2):
    parent={child:group[0] for group in regions for child in group[1:]};ancestors=set()
    while region1 in parent:ancestors.add(region1);region1=parent[region1]
    ancestors.add(region1)
    while region2 not in ancestors:region2=parent[region2]
    return region2
'''
HAND='''def noncrossing_handshake_count(numPeople):
    mod=10**9+7;pairs=numPeople//2;dp=[0]*(pairs+1);dp[0]=1
    for size in range(1,pairs+1):
        for left in range(size):dp[size]=(dp[size]+dp[left]*dp[size-1-left])%mod
    return dp[pairs]
'''

BATCH={
1246:entry('minimum_palindrome_removals',[('arr','list[int]')],'int',['dynamic programming','intervals'],['In one move remove any nonempty contiguous palindromic subarray.','The remaining left and right parts join after removal.','Return the minimum moves needed to remove the whole nonempty array.'],[([[1,2]],'Each unequal singleton must be removed separately.'),([[1,3,4,1,5]],'Remove four, then the joined palindrome one-three-one, then five.')],[[x] for x in [[1],[1,2],[1,1],[1,3,4,1,5],[1,2,1],[1,2,2,1],[1,2,3,2,1],[1,1,2],[1,2,1,2],[1,2,3],[2,1,2,3,2],[1,1,1,1],[1,2,3,1],[4,3,4,3,4]]],REMOVAL,[REMOVAL.replace('dp[left][left]=1','dp[left][left]=0'),REMOVAL.replace('arr[left]==arr[middle]','arr[left]!=arr[middle]')],['Treats a singleton as requiring zero moves.','Merges intervals around unequal endpoint values.'],removal_o,rremoval,['Use interval DP for the minimum moves to erase each subarray.','Removing the left item alone costs one plus the rest; matching it with a later equal value can merge their removal.','Try every equal later position and combine the middle and suffix costs.','Every optimal first item is removed alone or together with some equal later item, so these transitions are exhaustive.'],'O(n^3)','O(n^2)',8),
1254:entry('count_closed_islands',[('grid','list[list[int]]')],'int',['matrices','recursion'],['Zero is land and one is water.','A land component is closed when it is surrounded by water and never touches the grid boundary.','Return the number of four-connected closed land components.'],[([[[1,1,1,1,1,1,1,0],[1,0,0,0,0,1,1,0],[1,0,1,0,1,1,1,0],[1,0,0,0,0,1,0,1],[1,1,1,1,1,1,1,0]]],'Two interior land components do not touch the boundary.'),([[[0,0,1,0,0],[0,1,0,1,0],[0,1,1,1,0]]],'Every land component reaches an outer edge, so none is closed.')],[[g] for g in [[[1]],[[0]],[[1,1],[1,1]],[[1,1,1],[1,0,1],[1,1,1]],[[0,0,1,0,0],[0,1,0,1,0],[0,1,1,1,0]],[[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,1,1,1]],[[1,1,1],[1,0,0],[1,1,1]],[[1,0,1],[1,0,1],[1,1,1]],[[1,1,1,1,1],[1,0,1,0,1],[1,1,1,1,1]],[[1,1,1],[1,0,1],[1,0,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,1]],[[1,1,1],[1,0,1],[1,1,0]],[[1,1,1,1,1],[1,0,0,0,1],[1,1,1,0,1],[1,0,1,1,1],[1,1,1,1,1]]]],CLOSED,[CLOSED.replace('return False','return True',1),CLOSED.replace("grid[row][col]=1","grid[row][col]=0")],['Treats leaving the grid as enclosed instead of open.','Never marks visited land, causing repeated recursion.'],closed_o,rclosed,['Flood each unvisited land component.','Crossing the grid boundary makes that component open; water contributes no opening.','Combine all four recursive directions while still evaluating every branch.','A component is closed exactly when none of its reachable land paths exits the grid.'],'O(rows*cols)','O(rows*cols)',5),
1255:entry('maximum_word_score',[('words','list[str]'),('letters','list[str]'),('score','list[int]')],'int',['backtracking','frequency counting'],['Choose each word at most once.','Selected words together may not use any letter more often than supplied letters.','Return the maximum sum of per-letter scores.'],[([['dog','cat','dad','good'],list('aacdddgoo'),[1,0,9,5,0,0,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0]],'Choosing dad and good yields the greatest feasible score.'),([['xxxz','ax','bx','cx'],list('zabcxxx'),[4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,10]],'The best feasible combination uses the available high-scoring letters.')],[[w,l,s] for w,l,s in [(['a'],['a'],[1]*26),(['a'],[],[1]*26),(['ab','bc'],list('abc'),[1]*26),(['aa','a'],list('aa'),[1]*26),(['cat','dog'],list('catdog'),[1]*26),(['z'],['z'],[0]*25+[10]),(['abc','de','ad'],list('abcde'),[2]*26),(['hello','world'],list('helloworld'),[1]*26),(['x','xx'],list('xx'),[1]*23+[5,0,0]),(['ab','cd','ef'],list('abcdef'),list(range(26))),(['aaa','bbb'],list('aaabbb'),[1]*26),(['ace','bed'],list('abcde'),[1]*26),(['q','qq','qqq'],list('qqq'),[1]*16+[3]+[1]*9),(['no','on'],list('on'),[1]*26)]],SCORE,[SCORE.replace('visit(index+1,total);used=[]','used=[]'),SCORE.replace('available[place]-=1','available[place]+=1')],['Never explores excluding the current word.','Adds required letters to availability instead of consuming them.'],score_o,rscore,['Count available letters by alphabet index.','Backtrack over words, branching on exclusion and feasible inclusion.','Temporarily consume a word’s letters and restore them after its inclusion branch.','The two branches enumerate every subset exactly once, and feasibility checks enforce the shared inventory.'],'O(2^words*word length)','O(words+alphabet)',8),
1257:entry('smallest_common_region',[('regions','list[list[str]]'),('region1','str'),('region2','str')],'str',['trees','hash maps'],['Each group lists a parent region followed by its direct child regions.','All named regions form one rooted hierarchy.','Return the lowest region containing both requested regions, allowing either requested region itself.'],[([[['Earth','North America','South America'],['North America','United States','Canada'],['United States','New York','Boston'],['Canada','Ontario','Quebec'],['South America','Brazil']], 'Quebec','New York'],'North America is the lowest ancestor shared by Quebec and New York.'),([[['Earth','North America','South America'],['North America','United States','Canada']], 'Canada','North America'],'North America contains itself and Canada, so it is their smallest common region.')],[[r,a,b] for r,a,b in [([['A','B','C']],'B','C'),([['A','B','C']],'A','C'),([['A','B'],['B','C']],'B','C'),([['A','B'],['B','C']],'A','C'),([['A','B','C'],['B','D','E']],'D','E'),([['A','B','C'],['B','D'],['C','E']],'D','E'),([['Earth','NA','SA'],['NA','US','CA'],['US','NY','MA']],'NY','CA'),([['R','A'],['A','B'],['B','C']],'C','C'),([['R','A','B'],['A','C'],['B','D']],'C','D'),([['X','Y','Z'],['Y','P','Q']],'P','Z'),([['A','B'],['B','C'],['C','D']],'B','D'),([['Top','L','R'],['L','LL'],['R','RR']],'LL','RR'),([['A','B','C','D']],'B','D'),([['A','B'],['B','C','D'],['D','E']],'C','E')]],REGION,[REGION.replace('ancestors.add(region1)','ancestors=set()',1),REGION.replace('region2=parent[region2]','region2=parent.get(region2,region1)')],['Clears the first region’s ancestor set before searching.','Falls back to the first region when climbing the second path, which can return a non-ancestor.'],region_o,rregion,['Map every child region to its direct parent.','Collect the first region and all its ancestors.','Climb from the second region until entering that set.','The first shared ancestor encountered upward from region2 is necessarily the lowest common one.'],'O(number of regions)','O(number of regions)',5),
1259:entry('noncrossing_handshake_count',[('numPeople','int')],'int',['dynamic programming','combinatorics'],['An even number of people sit around a circle and each person shakes exactly one hand.','Handshake chords may not cross inside the circle.','Return the number of pairings modulo 1000000007.'],[([2],'The only two people form one handshake.'),([4],'The four people have two noncrossing perfect matchings.')],[[n] for n in [2,4,6,8,10,12,14,16,18,20,22,24,26,28]],HAND,[HAND.replace('range(size)','range(size-1)'),HAND.replace('dp[0]=1','dp[0]=0')],['Omits the split where the first person pairs with the final valid partner.','Erases the empty-subproblem base case required by every pairing.'],hand_o,rhand,['Pair one fixed person and consider how many pairs lie on each side of that chord.','The two sides are independent smaller noncrossing matching problems.','Sum their product over every possible split.','Every noncrossing matching has one unique partner for the fixed person, yielding the Catalan recurrence.'],'O(pairs^2)','O(pairs)',8),
}
BATCH[1254]['wrong'][1]=CLOSED.replace("return sum(flood(i,j) for i in range(rows) for j in range(cols) if grid[i][j]==0)","return 0")
BATCH[1254]['wrong_reasons'][1]='Returns zero without examining any land components.'
BATCH[1257]['wrong'][1]=REGION.replace('return region2','return region1')
BATCH[1257]['wrong_reasons'][1]='Returns the first region’s rootward endpoint instead of the first shared ancestor found from the second region.'
