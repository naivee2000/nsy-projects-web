"""Ordered jumps, rook rays, and stepping-number generation."""
from .import_batch_055 import entry

def jumps_o(a):
    arr=a[0];n=len(arr);odd=[False]*n;even=[False]*n;odd[-1]=even[-1]=True
    for i in range(n-2,-1,-1):
        higher=[j for j in range(i+1,n) if arr[j]>=arr[i]]
        if higher:
            target=min(arr[j] for j in higher);j=min(j for j in higher if arr[j]==target);odd[i]=even[j]
        lower=[j for j in range(i+1,n) if arr[j]<=arr[i]]
        if lower:
            target=max(arr[j] for j in lower);j=min(j for j in lower if arr[j]==target);even[i]=odd[j]
    return sum(odd)
def rjumps(r):return [[r.randint(0,20) for _ in range(r.randint(1,20))]]

def rook_o(a):
    board=a[0]
    for i,row in enumerate(board):
        for j,value in enumerate(row):
            if value=='R':rook=(i,j)
    answer=0
    for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
        i,j=rook
        while 0<=i+di<8 and 0<=j+dj<8:
            i+=di;j+=dj
            if board[i][j]=='B':break
            if board[i][j]=='p':answer+=1;break
    return answer
def rrook(r):
    board=[['.']*8 for _ in range(8)];i,j=r.randrange(8),r.randrange(8);board[i][j]='R'
    for _ in range(r.randint(0,12)):
        x,y=r.randrange(8),r.randrange(8)
        if board[x][y]=='.':board[x][y]=r.choice('Bp')
    return [[''.join(row) for row in board]]

def stepping_o(a):
    low,high=a
    return [value for value in range(low,high+1) if value<10 or all(abs(int(x)-int(y))==1 for x,y in zip(str(value),str(value)[1:]))]
def rstepping(r):
    low=r.randint(0,5000);return [low,r.randint(low,min(10000,low+2000))]

JUMPS='''def good_odd_even_starts(arr):
    n=len(arr)
    def next_indices(order):
        answer=[None]*n;stack=[]
        for index in order:
            while stack and index>stack[-1]:answer[stack.pop()]=index
            stack.append(index)
        return answer
    higher=next_indices(sorted(range(n),key=lambda i:(arr[i],i)))
    lower=next_indices(sorted(range(n),key=lambda i:(-arr[i],i)))
    odd=[False]*n;even=[False]*n;odd[-1]=even[-1]=True
    for i in range(n-2,-1,-1):
        if higher[i] is not None:odd[i]=even[higher[i]]
        if lower[i] is not None:even[i]=odd[lower[i]]
    return sum(odd)
'''
ROOK='''def rook_capture_count(board):
    for row in range(8):
        for column in range(8):
            if board[row][column]=='R':start=(row,column)
    answer=0
    for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
        row,column=start
        while 0<=row+dr<8 and 0<=column+dc<8:
            row+=dr;column+=dc
            if board[row][column]=='B':break
            if board[row][column]=='p':answer+=1;break
    return answer
'''
STEPPING='''def stepping_numbers_in_range(low,high):
    answer=[]
    if low==0:answer.append(0)
    queue=list(range(1,10))
    for value in queue:
        if value>high:continue
        if value>=low:answer.append(value)
        last=value%10
        for digit in {last-1,last+1}:
            nxt=value*10+digit
            if 0<=digit<=9 and nxt<=high:queue.append(nxt)
    return answer
'''

BATCH={
975:entry('good_odd_even_starts',[('arr','list[int]')],'int',['arrays','monotonic stacks','dynamic programming'],['On an odd jump, choose the smallest later value at least the current value, breaking ties by index.','On an even jump, choose the largest later value at most the current value, again breaking ties by index.','Return how many starting indices eventually reach the final index when jumps alternate odd then even.'],[([[10,13,12,14,15]],'Only starts at indices one, three, and four reach the end.'),([[2,3,1,1,4]],'Starts zero, one, and four are good.')],[[x] for x in [[1],[1,2],[2,1],[10,13,12,14,15],[2,3,1,1,4],[5,1,3,4,2],[1,1,1],[3,2,1,0],[0,1,2,3],[2,2,1,2],[4,1,4,1,4],[1,3,2,3,1],[5,4,6,3,7],[2,8,5,6,3,4,1,7]]],JUMPS,[JUMPS.replace('(arr[i],i)','(arr[i],-i)'),JUMPS.replace('odd[i]=even[higher[i]]','odd[i]=odd[higher[i]]')],['Breaks equal-value ties toward the largest later index.','Follows another odd jump instead of alternating to an even jump.'],jumps_o,rjumps,['Precompute odd and even destinations using value-sorted indices and a monotonic index stack.','Equal values are sorted by increasing index to enforce the nearest-index tie rule.','Work backward: odd-good depends on even-good at its destination, and vice versa.','Every jump destination is deterministic; backward DP therefore marks exactly the starts whose alternating chain reaches the end.'],'O(n log n)','O(n)',8),
999:entry('rook_capture_count',[('board','list[str]')],'int',['matrices','simulation'],['board is eight by eight and contains exactly one white rook R.','White bishops B block the rook; black pawns p are capturable.','Count the first visible pawn, if any, along each of the rook’s four rays.'],[([['........','........','........','...p....','...R...p','........','........','........']],'The rook sees one pawn above and one to the right.'),([['........','........','....B...','...pB...','...R...p','........','........','........']],'The bishop blocks the upward pawn, leaving only the pawn to the right.')],[[b] for b in [['R.......','........','........','........','........','........','........','........'],['........','........','........','...p....','...R...p','........','........','........'],['........','........','....B...','...pB...','...R...p','........','........','........'],['........','........','........','........','....R...','........','........','........'],['....p...','........','........','........','....R...','........','........','....p...'],['........','........','........','p..R...p','........','........','........','........'],['........','...B....','...p....','...R....','........','........','........','........'],['........','........','...Rpp..','........','........','........','........','........'],['........','........','pp.R....','........','........','........','........','........'],['.......p','........','........','.......R','........','........','........','.......B'],['........','........','........','B.pR....','........','........','........','........'],['........','....p...','....B...','....R...','........','........','........','........'],['........','........','........','R.Bp....','........','........','........','........'],['........','........','........','....R...','....p...','....B...','....p...','........']]],ROOK,[ROOK.replace("if board[row][column]=='B':break","if board[row][column]=='B':continue"),ROOK.replace("if board[row][column]=='p':answer+=1;break","if board[row][column]=='p':answer+=1")],['Looks through bishops instead of stopping the ray.','Counts every pawn on a ray instead of only the first visible one.'],rook_o,rrook,['Locate the rook once.','Walk outward independently in each cardinal direction.','Stop at a bishop or board edge; count and stop at the first pawn.','Chess sliding attacks follow exactly these unobstructed rays, and each direction contributes at most one capture.'],'O(1)','O(1)',3),
1215:entry('stepping_numbers_in_range',[('low','int'),('high','int')],'list[int]',['breadth-first search','math'],['Zero is a stepping number, and low and high are inclusive nonnegative bounds.','A positive number is stepping when every pair of adjacent digits differs by exactly one.','Return all stepping numbers in the interval; output order does not matter.'],[([0,21],'The interval contains zero through nine, ten, twelve, and twenty-one.'),([10,15],'Only ten and twelve have adjacent digits differing by one.')],[[*x] for x in [(0,0),(0,9),(0,21),(10,15),(10,12),(11,11),(12,12),(20,30),(90,110),(100,130),(200,250),(1,1),(500,1000),(1000,1500)]],STEPPING,[STEPPING.replace("{last-1,last+1}","{last-2,last+2}"),STEPPING.replace('if low==0:answer.append(0)','if low<=1:answer.append(0)')],['Extends numbers with digits differing by two instead of one.','Includes zero even when the lower bound is one.'],stepping_o,rstepping,['Generate positive stepping numbers from one-digit seeds.','Append only last digit minus one and plus one when they remain decimal digits.','Record values inside the bounds and expand only values no greater than high; handle zero separately.','Every positive stepping number has one unique prefix chain from its first digit, so BFS generates all and only valid values.'],'O(number generated)','O(number generated)',5),
}
BATCH[1215]['comparator']='unordered'
