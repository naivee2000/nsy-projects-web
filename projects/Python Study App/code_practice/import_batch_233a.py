"""Card matching, mirror paths, fixed-size flips, balanced factors, and disjoint bits."""
from functools import lru_cache
from itertools import combinations
from math import prod
from .import_batch_055 import entry


def cards_oracle(args):
    cards,x=args;n=len(cards)
    @lru_cache(None)
    def solve(mask):
        best=0
        for i in range(n):
            if not mask>>i&1 or x not in cards[i]:continue
            for j in range(i+1,n):
                if mask>>j&1 and x in cards[j] and sum(a!=b for a,b in zip(cards[i],cards[j]))==1:
                    best=max(best,1+solve(mask^(1<<i)^(1<<j)))
        return best
    return solve((1<<n)-1)

def random_cards(rng):
    letters='abcd';return [[''.join(rng.choice(letters) for _ in range(2)) for _ in range(rng.randint(2,12))],rng.choice(letters)]

def mirror_oracle(args):
    grid=args[0];rows=len(grid);cols=len(grid[0])
    @lru_cache(None)
    def paths(r,c):
        if (r,c)==(rows-1,cols-1):return 1
        answer=0
        for direction in (0,1):
            nr=r+(direction==1);nc=c+(direction==0);moving=direction
            while nr<rows and nc<cols and grid[nr][nc]:
                moving^=1;nr+=moving==1;nc+=moving==0
            if nr<rows and nc<cols:answer+=paths(nr,nc)
        return answer%(10**9+7)
    return paths(0,0)

def random_mirror(rng):
    rows=rng.randint(2,6);cols=rng.randint(2,6);grid=[[rng.randrange(2) for _ in range(cols)] for _ in range(rows)];grid[0][0]=grid[-1][-1]=0
    return [grid]

def flips_oracle(args):
    s,k=args;n=len(s);start=s.count('0');distance=[-1]*(n+1);distance[start]=0;queue=[start]
    for current in queue:
        if current==0:return distance[current]
        for zeros_flipped in range(max(0,k-(n-current)),min(current,k)+1):
            nxt=current+k-2*zeros_flipped
            if distance[nxt]<0:distance[nxt]=distance[current]+1;queue.append(nxt)
    return -1

def random_flips(rng):
    n=rng.randint(1,14);return [''.join(rng.choice('01') for _ in range(n)),rng.randint(1,n)]

def factor_oracle(args):
    n,k=args;best=None
    def search(remaining,slots,minimum,path):
        nonlocal best
        if slots==1:
            if remaining>=minimum:
                candidate=path+[remaining]
                if best is None or (candidate[-1]-candidate[0],candidate)<(best[-1]-best[0],best):best=candidate
            return
        for value in range(minimum,remaining+1):
            if remaining%value==0:search(remaining//value,slots-1,value,path+[value])
    search(n,k,1,[]);return best

def random_factor(rng):
    k=rng.randint(2,5);factors=[rng.randint(1,5) for _ in range(k)];n=prod(factors)
    if n<4:n*=4
    return [n,k]

def bits_oracle(args):
    nums=args[0];answer=0
    for i in range(len(nums)):
        for j in range(i):
            if nums[i]&nums[j]==0:answer=max(answer,nums[i]*nums[j])
    return answer

def random_bits(rng):return [[rng.randint(1,255) for _ in range(rng.randint(2,20))]]


CARDS='''def maximum_card_game_points(cards,x):
    from collections import Counter
    left=Counter();right=Counter();centers=0
    for card in cards:
        if card==x+x:centers+=1
        elif card[0]==x:left[card[1]]+=1
        elif card[1]==x:right[card[0]]+=1
    def internal(counts):
        total=sum(counts.values())
        return min(total//2,total-max(counts.values(),default=0))
    pairs=internal(left)+internal(right);side_cards=sum(left.values())+sum(right.values())
    leftovers=side_cards-2*pairs;direct=min(centers,leftovers);remaining=centers-direct
    return pairs+direct+min(pairs,remaining//2)
'''

MIRRORS='''def count_twisted_mirror_paths(grid):
    mod=10**9+7;rows=len(grid);cols=len(grid[0]);right=[[0]*cols for _ in range(rows)];down=[[0]*cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            ways=1 if r==0 and c==0 else (right[r][c]+down[r][c])%mod
            if (r,c)==(rows-1,cols-1):return ways
            if grid[r][c]:
                if r+1<rows:down[r+1][c]=(down[r+1][c]+right[r][c])%mod
                if c+1<cols:right[r][c+1]=(right[r][c+1]+down[r][c])%mod
            else:
                if c+1<cols:right[r][c+1]=(right[r][c+1]+ways)%mod
                if r+1<rows:down[r+1][c]=(down[r+1][c]+ways)%mod
    return 0
'''

FLIPS='''def minimum_fixed_flips_to_ones(s,k):
    n=len(s);start=s.count('0');parents=[]
    for parity in range(2):
        size=(n-parity)//2+1;parents.append(list(range(size+1)))
    def find(parity,index):
        parent=parents[parity]
        while parent[index]!=index:parent[index]=parent[parent[index]];index=parent[index]
        return index
    def remove(value):
        parity=value&1;index=(value-parity)//2;parents[parity][index]=find(parity,index+1)
    remove(start);queue=[start];distance={start:0}
    for current in queue:
        if current==0:return distance[current]
        minimum=max(0,k-(n-current));maximum=min(current,k);low=current+k-2*maximum;high=current+k-2*minimum;parity=low&1
        index=find(parity,(low-parity)//2);last=(high-parity)//2
        while index<=last:
            value=parity+2*index;distance[value]=distance[current]+1;queue.append(value);parents[parity][index]=find(parity,index+1);index=find(parity,index)
    return -1
'''

FACTORS='''def balanced_factor_decomposition(n,k):
    best=None;best_range=10**30
    def search(remaining,slots,minimum,path):
        nonlocal best,best_range
        if slots==1:
            if remaining>=minimum:
                candidate=path+[remaining];spread=candidate[-1]-candidate[0]
                if spread<best_range:best_range=spread;best=candidate
            return
        limit=int(remaining**(1/slots))
        while (limit+1)**slots<=remaining:limit+=1
        while limit**slots>remaining:limit-=1
        for factor in range(minimum,limit+1):
            if remaining%factor==0:search(remaining//factor,slots-1,factor,path+[factor])
    search(n,k,1,[])
    return best
'''

BITS='''def maximum_disjoint_bit_product(nums):
    width=max(nums).bit_length();size=1<<width;best=[0]*size
    for value in nums:best[value]=max(best[value],value)
    for bit in range(width):
        for mask in range(size):
            if mask>>bit&1:best[mask]=max(best[mask],best[mask^(1<<bit)])
    full=size-1;answer=0
    for value in nums:answer=max(answer,value*best[full^value])
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

C_CASES=[[a,x] for a,x in ((['aa','aa'],'a'),(['ab','ac'],'a'),(['ab','ba'],'a'),(['aa','ab','ca'],'a'),(['xa','xb','xc','xd'],'x'),(['ax','bx','cx','dx'],'x'),(['xx','xa','xb'],'x'),(['xx','xx','xa','ax'],'x'),(['ab','cd','ef'],'a'),(['aa','ab','ac','ad','ba'],'a'),(['bb','ab','ba','bc','cb'],'b'),(['aa','ab','ba','ac','ca','aa'],'a'))]
M_CASES=[[grid] for grid in ([[0,0,0],[0,0,0]],[[0,1],[0,0]],[[0,0],[1,0]],[[0,1,1],[1,1,0]],[[0,0,0],[1,0,0]],[[0,1,0],[1,0,0],[0,0,0]],[[0,1,0],[0,1,0],[0,0,0]],[[0,0,1],[1,1,0],[0,0,0]],[[0,1],[1,0]],[[0,0,0,0],[1,1,1,0]],[[0,1,1,0],[0,1,0,0],[1,0,1,0],[0,0,0,0]],[[0,0,1],[0,1,1],[0,0,0]])]
F_CASES=[[s,k] for s,k in (('1',1),('0',1),('00',1),('00',2),('01',2),('1111',3),('0000',3),('0101',2),('101',2),('00111',2),('010101',4),('0001110',5))]
D_CASES=[[n,k] for n,k in ((4,2),(6,2),(8,3),(12,2),(12,3),(16,4),(18,3),(24,4),(36,2),(48,3),(72,4),(96,5))]
B_CASES=[[x] for x in ([1,1],[1,2],[3,4],[5,6,8],[8,16,32],[7,8,3],[1,2,4,8],[15,16,7],[64,8,32],[3,5,6,9],[255,256,511],[10,12,17,33])]

BATCH={
3664:entry('maximum_card_game_points',[('cards','list[str]'),('x','str')],'int',['strings','hash maps','matching'],['Two to 100,000 two-letter cards using letters a through j.','Both selected cards contain x and differ in exactly one position.','Remove cards in pairs to maximize the score.'],[([['aa','ab','ba','ac'],'a'],'Pair ab-ac and aa-ba for two points.'),([['aa','ab','ba'],'a'],'Only one compatible pair can be removed.')],C_CASES,CARDS,[CARDS.replace('remaining//2','remaining'),CARDS.replace('side_cards-2*pairs','side_cards-pairs')],['Lets one sacrificed internal pair serve more than two center cards.','Counts cards already used by internal pairs as leftovers.'],cards_oracle,random_cards,lesson('Cards with x only on the left and only on the right form separate complete multipartite matching groups; xx cards connect to both.','First maximize different-letter pairs within each side, then match xx cards to leftovers or free two cards by sacrificing a pair.','Compute each side’s min(total/2,total-largest) matching, consume natural leftovers, then exchange one pair for two center matches when useful.','The multipartite bound is attainable, and each remaining center either uses a leftover or requires breaking exactly one existing pair for two available cards.'),'O(n)','O(1) alphabet counts',6),
3665:entry('count_twisted_mirror_paths',[('grid','list[list[int]]')],'int',['matrices','dynamic programming'],['Both dimensions are between two and 500; start and finish are empty.','Entering a mirror turns rightward motion down and downward motion right, chaining immediately.','Count valid paths modulo 1,000,000,007.'],[([[[0,1,0],[0,0,1],[1,0,0]]],'Five choice sequences reach the finish after applying mirror turns.'),([[[0,0],[0,0]]],'The ordinary right-down and down-right paths both remain valid.')],M_CASES,MIRRORS,[MIRRORS.replace('down[r+1][c]+right[r][c]','down[r+1][c]+down[r][c]'),MIRRORS.replace('if grid[r][c]:','if False:')],['Keeps downward arrivals moving down instead of turning rightward arrivals downward.','Treats every mirror as an ordinary cell with a free direction choice.'],mirror_oracle,random_mirror,lesson('At a mirror, the outgoing direction depends on the direction used to enter, so retain two arrival counts.','Scan cells topologically with separate right-arrival and down-arrival DP tables.','Empty cells send their total both ways; mirrors send right arrivals down and down arrivals right.','Every move increases a coordinate, so row-major propagation counts each choice sequence once and chained mirrors follow automatically.'),'O(m*n)','O(m*n)',5),
3666:entry('minimum_fixed_flips_to_ones',[('s','str'),('k','int')],'int',['strings','breadth first search','disjoint sets'],['The binary string has length up to 100,000.','Every operation flips exactly k distinct positions.','Return the minimum operations or negative one when unreachable.'],[(['110',1],'Flip the sole zero in one operation.'),(['0101',3],'Two carefully chosen three-index flips reach all ones.')],F_CASES,FLIPS,[FLIPS.replace('maximum=min(current,k)','maximum=min(current,k-1)'),FLIPS.replace('minimum=max(0,k-(n-current))','minimum=max(0,k-(n-current)+1)')],['Never permits flipping k zeros even when all selected positions are zero.','Requires one too many zero positions in every operation.'],flips_oracle,random_flips,lesson('Only the current number of zeros matters; flipping a zeros changes the count to current+k-2a.','BFS zero counts, visiting each reachable parity interval efficiently with next-unvisited disjoint sets.','Derive the legal low/high next counts, enumerate unvisited counts of that parity, and remove each once.','BFS gives minimum operations, and the interval derives from every feasible choice of zero versus one indices, so no transition is missed.'),'O(n alpha(n))','O(n)',8),
3669:entry('balanced_factor_decomposition',[('n','int'),('k','int')],'list[int]',['math','backtracking','number theory'],['Four <= n <= 100,000 and two <= k <= five.','Return exactly k positive integers with product n.','Minimize maximum minus minimum; output order does not matter.'],[([100,2],'Ten and ten multiply to one hundred with zero spread.'),([44,3],'Two, two, and eleven give the minimum spread nine.')],D_CASES,FACTORS,[FACTORS.replace('if spread<best_range','if best is None'),FACTORS.replace('if remaining>=minimum','if remaining==minimum')],['Keeps the first valid decomposition instead of comparing spreads.','Accepts only a final factor equal to the preceding factor and misses nonuniform optima.'],factor_oracle,random_factor,lesson('An unordered decomposition has one nondecreasing representation.','Backtrack nondecreasing divisors and keep the tuple with smallest final-first spread.','At each slot try divisors no larger than the remaining product’s slots-th root, then place the final cofactor.','Every nondecreasing factorization follows exactly one branch; the root bound cannot exclude its next factor, and direct comparison selects the optimum.'),'O(number of divisor decompositions)','O(k)',6),
3670:entry('maximum_disjoint_bit_product',[('nums','list[int]')],'int',['arrays','bit manipulation','subset dynamic programming'],['Two to 100,000 positive values up to one million.','Choose distinct indices whose values have bitwise AND zero.','Return the maximum product, or zero if no pair qualifies.'],[([[1,2,3,4,5,6,7]],'Three and four share no bits and produce the maximum product twelve.'),([[5,6,4]],'Every pair shares a set bit, so the answer is zero.')],B_CASES,BITS,[BITS.replace('full^value','value'),BITS.replace('best[mask^(1<<bit)]','best[mask]')],['Looks for a partner inside the same mask rather than its complement.','Never propagates maxima from submasks into their supersets.'],bits_oracle,random_bits,lesson('A partner for value v must be a submask of the complement of v.','Store the largest present value per mask and run subset-max DP.','Propagate maxima from each mask with one bit removed, then multiply every value by the best complement submask.','After SOS DP, best[mask] is the largest input contained in mask, so the complement query considers exactly all disjoint-bit partners.'),'O(B*2^B+n)','O(2^B)',6),
}
BATCH[3669]['comparator']='unordered'
