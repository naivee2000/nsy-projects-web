"""Four deferred Hard problems with independent bounded exhaustive oracles."""
from functools import lru_cache,reduce
from itertools import combinations
from math import gcd
from operator import xor
from .import_batch_055 import entry

def zeros(x):
    answer=0
    while x:x//=5;answer+=x
    return answer
def preimage_oracle(a):return sum(zeros(x)==a[0] for x in range(5*a[0]+5))
def random_preimage(r):return [r.randint(0,200)]
def xor_oracle(a):
    nums=tuple(a[0])
    @lru_cache(None)
    def win(state):
        if reduce(xor,state,0)==0:return True
        for i in range(len(state)):
            nxt=state[:i]+state[i+1:]
            if reduce(xor,nxt,0)!=0 and not win(nxt):return True
        return False
    return win(nums)
def random_xor(r):return [[r.randint(0,7) for _ in range(r.randint(1,9))]]
def magical_oracle(a):
    n,x,y=a;value=0;seen=0
    while seen<n:
        value+=1
        if value%x==0 or value%y==0:seen+=1
    return value%(10**9+7)
def random_magical(r):return [r.randint(1,100),r.randint(2,20),r.randint(2,20)]
def widths_oracle(a):
    nums=a[0];return sum(max(nums[i] for i in group)-min(nums[i] for i in group) for size in range(1,len(nums)+1) for group in combinations(range(len(nums)),size))%(10**9+7)
def random_widths(r):return [[r.randint(0,20) for _ in range(r.randint(1,9))]]

PREIMAGE='''def factorial_zero_preimage_size(k):
    def zeros(value):
        answer=0
        while value:value//=5;answer+=value
        return answer
    def lower(target):
        left,right=0,5*target+5
        while left<right:
            middle=(left+right)//2
            if zeros(middle)>=target:right=middle
            else:left=middle+1
        return left
    return lower(k+1)-lower(k)
'''
XOR_GAME='''def alice_wins_xor_game(nums):
    from functools import reduce
    from operator import xor
    return len(nums)%2==0 or reduce(xor,nums,0)==0
'''
MAGICAL='''def nth_magical_number(n,a,b):
    from math import gcd
    common=a//gcd(a,b)*b;left,right=1,n*min(a,b)
    while left<right:
        middle=(left+right)//2
        if middle//a+middle//b-middle//common>=n:right=middle
        else:left=middle+1
    return left%(10**9+7)
'''
WIDTHS='''def sum_subsequence_widths(nums):
    nums=sorted(nums);mod=10**9+7;answer=0;power=1
    for i,value in enumerate(nums):
        answer=(answer+(value-nums[-1-i])*power)%mod;power=power*2%mod
    return answer
'''

BATCH={
793:entry('factorial_zero_preimage_size',[('k','int')],'int',['math','binary search'],['Let f(x) be the number of trailing zeros in x factorial.','Count nonnegative integers x satisfying f(x)=k.','Return the preimage size, which is either zero or five.'],[([0],'Values zero through four have no factorial trailing zeros, so return five.'),([5],'No factorial has exactly five trailing zeros, so return zero.')],[[k] for k in [0,1,2,3,4,5,6,7,10,20,24,25,50,100]],PREIMAGE,[PREIMAGE.replace('lower(k+1)-lower(k)','lower(k)-lower(k+1)'),PREIMAGE.replace('>=target','>target')],['Subtracts the two lower bounds in reverse order.','Searches for values strictly above the target rather than at least the target.'],preimage_oracle,random_preimage,['Trailing-zero count is monotone in x.','Binary-search the first x with f(x)>=target.','The values with f(x)=k lie between lower(k) and lower(k+1).','Subtracting those boundary indices gives the exact count without enumerating large factorials.'],'O(log k*log k)','O(1)',8),
810:entry('alice_wins_xor_game',[('nums','list[int]')],'bool',['game theory','bit manipulation'],['Players alternately erase one number, with Alice first.','A mover loses if the remaining XOR becomes zero; a player starting a turn with XOR zero wins.','Return whether Alice wins under optimal play.'],[([[1,1,2]],'The nonzero XOR and odd length force Alice into a losing position.'),([[1,1]],'The starting XOR is zero, so Alice wins immediately.')],[[x] for x in [[1],[0],[1,1],[1,1,2],[1,2],[1,2,3],[2,2,2],[0,1,1],[3,4,5,6],[7,7,7,7],[1,1,1,1,1],[2,3,1,0],[4,4,5],[1,2,4,8]]],XOR_GAME,[XOR_GAME.replace('len(nums)%2==0','len(nums)%2==1'),XOR_GAME.replace('==0','!=0')],['Treats odd rather than even length as automatically winning.','Reverses the starting-zero winning condition.'],xor_oracle,random_xor,['A zero starting XOR wins by rule.','With nonzero XOR, every even-length position is winning and every odd-length position is losing under optimal play.','Check zero XOR or even length.','The XOR symmetry ensures an even position has a safe deletion, while an odd nonzero position cannot avoid handing over that structure.'],'O(n)','O(1)',8),
878:entry('nth_magical_number',[('n','int'),('a','int'),('b','int')],'int',['math','binary search'],['A magical number is divisible by a or b.','Find the nth positive magical number in increasing order.','Return it modulo 1,000,000,007.'],[([1,2,3],'The first value divisible by two or three is two.'),([4,2,3],'The sequence begins 2,3,4,6, so return six.')],[[n,a,b] for n,a,b in [(1,2,3),(4,2,3),(5,2,4),(10,3,5),(1,7,11),(20,4,6),(50,2,9),(100,13,17),(3,6,8),(12,5,5),(25,7,14),(7,8,9),(99,19,20),(1000,2,3)]],MAGICAL,[MAGICAL.replace('-middle//common','+middle//common'),MAGICAL.replace('>=n','>n')],['Double-counts common multiples instead of subtracting them.','Searches for a count strictly greater than n and skips exact boundaries.'],magical_oracle,random_magical,['Count magical values no greater than x by inclusion-exclusion using lcm(a,b).','This count is monotone, so binary-search its first value reaching n.','Use n*min(a,b) as a safe upper bound.','The lower-bound result is exactly the nth ordered magical number.'],'O(log(n*min(a,b)))','O(1)',8),
891:entry('sum_subsequence_widths',[('nums','list[int]')],'int',['arrays','combinatorics','sorting'],['The width of a nonempty subsequence is maximum minus minimum.','Sum widths over all index subsequences.','Return the result modulo 1,000,000,007.'],[([[2,1,3]],'Singleton widths are zero and the four larger subsequences contribute 1+1+2+2=6.'),([[5,5]],'Every subsequence has equal minimum and maximum, so return zero.')],[[x] for x in [[1],[2,1,3],[5,5],[1,2],[2,1],[1,2,3,4],[4,3,2,1],[0,10],[1,1,2],[2,2,3,3],[5,1,9],[7,7,7],[0,1,2,8],[10,20,30]]],WIDTHS,[WIDTHS.replace('value-nums[-1-i]','value+nums[-1-i]'),WIDTHS.replace('power=power*2','power=power*3')],['Adds maximum and minimum contributions instead of subtracting them.','Uses powers of three rather than the binary include/exclude count.'],widths_oracle,random_widths,['Sort so each value’s rank determines how often it is a maximum or minimum.','At rank i, its signed coefficient is 2^i-2^(n-1-i).','The symmetric loop accumulates both roles with one growing power.','Every subsequence contributes its maximum once and its minimum once with opposite sign.'],'O(n log n)','O(n)',8),
}
