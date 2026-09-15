"""Permutation ranks, board paths, playlists, and exact repeating decimals."""
from fractions import Fraction
from itertools import permutations,product
from .import_batch_055 import entry

def perm_o(a):
    pattern=a[0];n=len(pattern)
    return sum(all((order[i]>order[i+1])==(pattern[i]=='D') for i in range(n)) for order in permutations(range(n+1)))%(10**9+7)
def rperm(r):return [''.join(r.choice('ID') for _ in range(r.randint(1,7)))]

def _destination(board,label):
    n=len(board);row_from_bottom=(label-1)//n;column=(label-1)%n
    if row_from_bottom%2:column=n-1-column
    value=board[n-1-row_from_bottom][column]
    return value if value!=-1 else label
def snakes_o(a):
    board=a[0];n=len(board);distance=[n*n+1]*(n*n+1);distance[1]=0
    for _ in range(n*n):
        changed=False
        for label in range(1,n*n+1):
            for rolled in range(label+1,min(n*n,label+6)+1):
                target=_destination(board,rolled)
                if distance[target]>distance[label]+1:distance[target]=distance[label]+1;changed=True
        if not changed:break
    return distance[n*n] if distance[n*n]<=n*n else -1
def rsnakes(r):
    n=r.randint(2,5);board=[[-1]*n for _ in range(n)]
    for label in range(2,n*n):
        if r.random()<.12:
            row=(label-1)//n;col=(label-1)%n
            if row%2:col=n-1-col
            board[n-1-row][col]=r.randint(1,n*n)
    return [board]

def playlists_o(a):
    n,goal,k=a;answer=0
    for sequence in product(range(n),repeat=goal):
        if len(set(sequence))<n:continue
        if all(sequence[i] not in sequence[max(0,i-k):i] for i in range(goal)):answer+=1
    return answer%(10**9+7)
def rplaylists(r):
    n=r.randint(1,4);return [n,r.randint(n,6),r.randint(0,n-1)]

def _decimal_parts(text):
    whole,fraction=(text.split('.')+[''])[:2] if '.' in text else (text,'')
    if '(' in fraction:plain,repeat=fraction.split('(');repeat=repeat[:-1]
    else:plain,repeat=fraction,''
    return int(whole),plain,repeat
def rational_o(a):
    def value(text):
        whole,plain,repeat=_decimal_parts(text);m=len(plain);base=Fraction(int(plain or 0),10**m)
        if repeat:
            combined=int((plain+repeat) or 0);before=int(plain or 0)
            base=Fraction(combined-before,10**m*(10**len(repeat)-1))
        return whole+base
    return value(a[0])==value(a[1])
def rrational(r):
    def make():
        whole=str(r.randint(0,5));plain=''.join(str(r.randrange(10)) for _ in range(r.randint(0,2)))
        repeat=''.join(str(r.randrange(10)) for _ in range(r.randint(0,2)))
        return whole+('.'+plain+('('+repeat+')' if repeat else '') if plain or repeat else '')
    return [make(),make()]

PERM='''def valid_di_permutation_count(s):
    mod=10**9+7;dp=[1]
    for char in s:
        n=len(dp);next_row=[0]*(n+1)
        if char=='I':
            total=0
            for rank in range(n+1):
                if rank:total+=dp[rank-1]
                next_row[rank]=total%mod
        else:
            total=0
            for rank in range(n,-1,-1):
                if rank<n:total+=dp[rank]
                next_row[rank]=total%mod
        dp=next_row
    return sum(dp)%mod
'''
SNAKES='''def snakes_and_ladders_moves(board):
    n=len(board)
    def destination(label):
        row=(label-1)//n;column=(label-1)%n
        if row%2:column=n-1-column
        value=board[n-1-row][column]
        return value if value!=-1 else label
    queue=[(1,0)];seen={1}
    for label,distance in queue:
        if label==n*n:return distance
        for rolled in range(label+1,min(n*n,label+6)+1):
            nxt=destination(rolled)
            if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
    return -1
'''
PLAYLISTS='''def music_playlist_count(n,goal,k):
    mod=10**9+7;dp=[[0]*(n+1) for _ in range(goal+1)];dp[0][0]=1
    for length in range(goal):
        for used in range(n+1):
            if used<n:dp[length+1][used+1]=(dp[length+1][used+1]+dp[length][used]*(n-used))%mod
            if used>k:dp[length+1][used]=(dp[length+1][used]+dp[length][used]*(used-k))%mod
    return dp[goal][n]
'''
RATIONAL='''from fractions import Fraction
def equal_rational_numbers(s,t):
    def value(text):
        whole,_,tail=text.partition('.');answer=Fraction(int(whole),1)
        if not tail:return answer
        if '(' in tail:plain,repeat=tail.split('(');repeat=repeat[:-1]
        else:plain,repeat=tail,''
        if plain:answer+=Fraction(int(plain),10**len(plain))
        if repeat:answer+=Fraction(int(repeat),10**len(plain)*(10**len(repeat)-1))
        return answer
    return value(s)==value(t)
'''

BATCH={
903:entry('valid_di_permutation_count',[('s','str')],'int',['dynamic programming','prefix sums'],['s is a nonempty string of I and D.','Permute integers zero through len(s); I requires an increase and D a decrease at that position.','Return the number of valid permutations modulo 1000000007.'],[(['DID'],'Exactly five permutations satisfy decrease, increase, decrease.'),(['I'],'Only zero,one is increasing.')],[[s] for s in ['I','D','ID','DI','DID','III','DDD','IID','DDI','IDID','DIDI','IIDDI','IDDDI','DIDID']],PERM,[PERM.replace("if char=='I'","if char=='D'"),PERM.replace('return sum(dp)%mod','return dp[-1]%mod')],['Interprets every increase as a decrease and vice versa.','Returns only one final-rank state instead of summing all valid final ranks.'],perm_o,rperm,['Track counts by the rank of the newest value among values used so far.','For I, sum previous smaller ranks; for D, sum previous equal-or-larger ranks.','Compute these transitions with prefix or suffix sums.','Rank compression preserves every comparison pattern, and each insertion rank maps uniquely to one longer permutation.'],'O(n^2)','O(n)',8),
909:entry('snakes_and_ladders_moves',[('board','list[list[int]]')],'int',['matrices','breadth-first search'],['Square numbers follow alternating left-to-right and right-to-left rows from the bottom.','Each move rolls one through six, then follows at most one snake or ladder at the landing square.','Return the minimum moves to reach n squared, or -1.'],[([[[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]],'Ladders shorten the minimum route to four rolls.'),([[[-1,-1],[-1,3]]],'One roll reaches label two, whose ladder reaches three; a second reaches four.')],[[b] for b in [[[-1,-1],[-1,-1]],[[-1,-1],[-1,3]],[[-1,4],[-1,3]],[[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]],[[-1,-1,-1],[-1,9,-1],[-1,-1,-1]],[[-1,-1,-1],[-1,1,-1],[-1,-1,-1]],[[-1]*4 for _ in range(4)],[[-1,-1,-1,-1],[-1,-1,15,-1],[-1,-1,-1,-1],[-1,8,-1,-1]],[[-1,-1],[-1,1]],[[-1,-1,-1],[-1,2,-1],[-1,-1,-1]],[[-1,-1,-1,-1],[-1,5,-1,-1],[-1,-1,14,-1],[-1,-1,-1,-1]],[[-1,-1,-1],[-1,-1,8],[-1,-1,-1]],[[-1,-1],[-1,4]],[[-1,-1,-1],[-1,7,-1],[-1,5,-1]]]],SNAKES,[SNAKES.replace('range(label+1','range(label+2'),SNAKES.replace('return distance','return distance+1')],['Never considers rolling exactly one.','Adds an extra move when the target state is dequeued.'],snakes_o,rsnakes,['Convert a square label to its board row and alternating-direction column.','Breadth-first search labels; each state has up to six landings followed by one optional jump.','Mark the post-jump label visited.','All rolls cost one, so the first visit to the final label uses the fewest rolls.'],'O(n^2)','O(n^2)',5),
920:entry('music_playlist_count',[('n','int'),('goal','int'),('k','int')],'int',['dynamic programming','combinatorics'],['A playlist has goal positions chosen from n distinct songs and must use every song.','A song may repeat only after at least k other songs have played.','Return the number of playlists modulo 1000000007.'],[([3,3,1],'All six permutations use every song once and satisfy the repeat rule.'),([2,3,0],'After both songs appear, either may repeat, giving six valid playlists.')],[[*x] for x in [(1,1,0),(1,2,0),(2,2,0),(2,3,0),(2,3,1),(3,3,1),(3,4,1),(3,5,2),(4,4,0),(4,5,1),(4,6,2),(3,6,0),(2,4,1),(4,5,3)]],PLAYLISTS,[PLAYLISTS.replace('(n-used)','used'),PLAYLISTS.replace('(used-k)','used')],['Counts already-used songs as choices for introducing a new song.','Allows replaying any used song without excluding the previous k songs.'],playlists_o,rplaylists,['Track playlist length and number of distinct songs already used.','Append a new song in n-used ways, or replay one of used-k eligible songs.','Accumulate both transitions modulo the limit.','The last position is uniquely new or repeated, so the transitions partition all valid playlists.'],'O(goal*n)','O(goal*n)',8),
972:entry('equal_rational_numbers',[('s','str'),('t','str')],'bool',['strings','math'],['Each input is a nonnegative decimal with an optional parenthesized repeating suffix.','A missing decimal or repeating part is allowed.','Return whether the two strings represent exactly the same rational number.'],[(['0.(52)','0.5(25)'],'Both repeating expansions equal fifty-two over ninety-nine.'),(['0.1666(6)','0.166(66)'],'Both representations repeat digit six after equivalent finite prefixes.')],[[*x] for x in [('0.(52)','0.5(25)'),('0.1666(6)','0.166(66)'),('0.9(9)','1.'),('1','1.0'),('0.1','0.10'),('0.(3)','0.3'),('2.5','2.50'),('1.(0)','1'),('3.(142857)','3.(142857)'),('0.0(9)','0.1'),('4.12(3)','4.123(3)'),('5','4.(9)'),('0.(01)','0.0(10)'),('2.34','2.3(4)')]],RATIONAL,[RATIONAL.replace('(10**len(repeat)-1)','10**len(repeat)'),RATIONAL.replace('if repeat:answer+=','if False:answer+=')],['Treats a repeating block as an ordinary finite block.','Ignores the repeating portion entirely.'],rational_o,rrational,['Parse integer, finite fractional, and repeating pieces separately.','A repeating r-digit block contributes block/(10^m*(10^r-1)) after m finite digits.','Build exact Fraction values and compare them.','The geometric-series denominator represents the infinite repetition without floating-point rounding.'],'O(len(s)+len(t))','O(len(s)+len(t))',8),
}
BATCH[903]['wrong'][0]=PERM.replace('return sum(dp)%mod','return 0')
BATCH[903]['wrong_reasons'][0]='Discards every computed permutation count and always returns zero.'
