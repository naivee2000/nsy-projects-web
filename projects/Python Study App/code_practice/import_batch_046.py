"""Exact base search, ordered permutations, recursive games and subsequences."""
from itertools import permutations, groupby
from math import isqrt

from .import_batch_003 import entry


def base_oracle(args):
    number=int(args[0])
    for base in range(2,number):
        remaining=number
        while remaining and remaining%base==1:
            remaining//=base
        if not remaining:
            return str(base)


def root_base_oracle(number):
    """Exact power-root certificates; the floating estimate never decides a result."""
    candidates=[number-1]
    for exponent in range(2,number.bit_length()):
        root=max(1,int(number**(1/exponent)))
        while (root+1)**exponent<=number: root+=1
        while root**exponent>number: root-=1
        assert root**exponent<=number<(root+1)**exponent
        if root>=2 and sum(root**i for i in range(exponent+1))==number:
            candidates.append(root)
    return str(min(candidates))


def permutation_oracle(args):
    pattern=args[0]
    for candidate in permutations(range(1,len(pattern)+2)):
        if all((a<b)==(symbol=='I') for a,b,symbol in zip(candidate,candidate[1:],pattern)):
            return list(candidate)


def game_oracle(args):
    nums=args[0]
    def play(left,right,first):
        if left>right:return 0
        if first:
            return max(nums[left]+play(left+1,right,False),nums[right]+play(left,right-1,False))
        return min(-nums[left]+play(left+1,right,True),-nums[right]+play(left,right-1,True))
    return play(0,len(nums)-1,True)>=0


def flip_oracle(args):
    nums=args[0]
    best=0
    for index in [None]+[i for i,v in enumerate(nums) if v==0]:
        changed=nums[:] if index is None else nums[:index]+[1]+nums[index+1:]
        best=max(best,max((len(list(group)) for value,group in groupby(changed) if value==1),default=0))
    return best


def subsequences_oracle(args):
    nums=args[0]
    sequences=set()
    for mask in range(1<<len(nums)):
        if mask.bit_count()<2:continue
        sequence=tuple(value for i,value in enumerate(nums) if mask>>i&1)
        if all(a<=b for a,b in zip(sequence,sequence[1:])):sequences.add(sequence)
    return [list(s) for s in sorted(sequences)]


def rectangle_oracle(args):
    area=args[0]
    return min(([length,area//length] for length in range(1,area+1)
                if area%length==0 and length>=area//length),key=lambda pair:pair[0]-pair[1])


def random_base(rng):return [str(rng.randint(3,2000))]
def random_permutation(rng):return [''.join(rng.choice('ID') for _ in range(rng.randint(1,6)))]
def random_game(rng):return [[rng.choice([0,1,2,9,10**7]) for _ in range(rng.randint(1,9))]]
def random_flip(rng):return [[rng.randrange(2) for _ in range(rng.randint(1,18))]]
def random_subsequences(rng):return [[rng.randint(-3,3) for _ in range(rng.randint(1,9))]]
def random_rectangle(rng):return [rng.randint(1,2000)]

BASE='''\
def smallest_good_base(n):
    number=int(n)
    for digits in range(number.bit_length(),2,-1):
        low=2
        high=1<<((number.bit_length()+digits-2)//(digits-1))
        while low<=high:
            base=(low+high)//2
            total=1
            for _ in range(digits-1):
                total=total*base+1
                if total>number:
                    break
            if total==number:
                return str(base)
            if total<number:
                low=base+1
            else:
                high=base-1
    return str(number-1)
'''
PERMUTATION='''\
def smallest_pattern_permutation(s):
    result=[]
    pending=[]
    for i in range(len(s)+1):
        pending.append(i+1)
        if i==len(s) or s[i]=='I':
            result.extend(reversed(pending))
            pending=[]
    return result
'''
GAME='''\
def predict_winner(nums):
    from functools import cache
    @cache
    def margin(left,right):
        if left==right:
            return nums[left]
        return max(nums[left]-margin(left+1,right),nums[right]-margin(left,right-1))
    return margin(0,len(nums)-1)>=0
'''
GREEDY_GAME='''\
def predict_winner(nums):
    scores=[0,0]
    left,right,turn=0,len(nums)-1,0
    while left<=right:
        if nums[left]>=nums[right]:
            scores[turn]+=nums[left]
            left+=1
        else:
            scores[turn]+=nums[right]
            right-=1
        turn^=1
    return scores[0]>=scores[1]
'''
FLIP='''\
def longest_ones_one_flip(nums):
    before_zero=current=best=0
    for value in nums:
        if value==1:
            current+=1
        else:
            before_zero=current+1
            current=0
        best=max(best,before_zero+current)
    return best
'''
SUBSEQUENCES='''\
def nondecreasing_subsequences(nums):
    result=[]
    path=[]
    def visit(start):
        if len(path)>=2:
            result.append(path[:])
        used=set()
        for i in range(start,len(nums)):
            value=nums[i]
            if value in used or (path and value<path[-1]):
                continue
            used.add(value)
            path.append(value)
            visit(i+1)
            path.pop()
    visit(0)
    return result
'''
RECTANGLE='''\
def construct_rectangle(area):
    from math import isqrt
    width=isqrt(area)
    while area%width:
        width-=1
    return [area//width,width]
'''

BATCH={
483:entry('smallest_good_base',[('n','str')],'str',['math','binary-search'],
    ['n is a decimal string with no leading zeros, representing an integer in 3..10^18.',
     'A good integer base is at least 2 and writes n using only digit 1. Return the SMALLEST such base as a decimal string.',
     'Two ones are allowed: base n-1 always writes n as 11. Larger numbers must not be rounded through floating-point arithmetic.'],
    [(['13'],'13 = 1+3+9, so base 3 writes 111. Base 12 also writes 11, but is not the smallest.'),
     (['4681'],'4681 = 1+8+64+512+4096, so base 8 writes 11111; checking only two or three digits would miss it.')],
    [[str(n)] for n in (3,4,5,6,7,8,9,10,15,21,31,40)],
    BASE,['def smallest_good_base(n):\n    return str(int(n)-1)\n',
      'def smallest_good_base(n):\n    from math import isqrt\n    value=int(n)\n    base=isqrt(value)\n    return str(base if base*base+base+1==value else value-1)\n'],
    ['Returns the always-valid two-digit base without minimizing it.', 'Checks only three-digit representations and misses longer strings of ones.'],
    base_oracle,random_base,
    ['For a fixed number of ones, the represented integer grows strictly with the base.',
     'Try digit counts from longest to shortest and binary-search the base for each count using exact integers.',
     'Evaluate 1+b+...+b^(digits-1) by total=total*b+1, stopping once total exceeds n. Fall back to n-1.',
     'A longer valid representation uses a smaller base. Power-of-two bounds give a safe integer search interval without a floating root.'],
    'Search digit counts in descending order, then use monotonicity of the geometric sum to locate a base. '
    'There is at most one base for each count. Exact Horner evaluation avoids overflow rounding and permits early stopping. '
    'The two-digit base n-1 guarantees an answer. The small-input oracle tries every base and inspects every remainder; '
    'large cases are independently checked with exact power-root certificates.',
    'O(log^3 n) integer operations','O(log n) bits',difficulty=8,
    stress=[(['1000000000000000000'],'999999999999999999'),([str(2**59-1)],'2'),([str((3**37-1)//2)],'3')]),
484:entry('smallest_pattern_permutation',[('s','str')],'list[int]',['arrays','strings','stacks','greedy'],
    ['1 <= s.length <= 100,000; every character is I or D.',
     'Use each integer from 1 through len(s)+1 exactly once. I requires a strict increase and D a strict decrease between adjacent entries.',
     'Return the lexicographically smallest valid permutation, not just any permutation satisfying the comparisons.'],
    [(['I'],'The two numbers must increase, so the only answer is [1,2].'),
     (['DI'],'Both [2,1,3] and [3,1,2] satisfy decrease then increase. [2,1,3] wins at the first differing position.')],
    [[s] for s in ('D','II','DD','ID','III','DDD','IID','IDI','DII','DID','DDI','IDD','IDDI','DDII')],
    PERMUTATION,["def smallest_pattern_permutation(s):\n    lo,hi=1,len(s)+1\n    answer=[]\n    for ch in s:\n        if ch=='I':\n            answer.append(lo)\n            lo+=1\n        else:\n            answer.append(hi)\n            hi-=1\n    return answer+[lo]\n",
      "def smallest_pattern_permutation(s):\n    result=list(range(1,len(s)+2))\n    for i,ch in enumerate(s):\n        if ch=='D':\n            result[i],result[i+1]=result[i+1],result[i]\n    return result\n"],
    ['Constructs an arbitrary valid comparison pattern without lexicographic minimization.', 'Swaps isolated neighboring pairs instead of reversing an entire decreasing run.'],
    permutation_oracle,random_permutation,
    ['A run of D symbols forces a whole block to descend.', 'Assign the smallest remaining consecutive numbers to that block, in reverse order.',
     'Push increasing numbers onto a stack and flush it in reverse at each I or at the end.',
     'Using a larger number at the start of a block cannot improve the lexicographic order; using a smaller one leaves too few smaller values for the forced descent.'],
    'Each maximal descending run consumes the next smallest available block, reversed. The stack delays output '
    'until that block ends. Every number is pushed and emitted once. Brute-force permutation enumeration independently '
    'selects the first lexicographically valid answer for small patterns.',
    'O(n)','O(n)',difficulty=5,
    stress=[(['I'*100000],list(range(1,100002))),(['D'*100000],list(range(100001,0,-1))),
      (['DI'*50000],[v for i in range(1,100001,2) for v in (i+1,i)]+[100001])]),
486:entry('predict_winner',[('nums','list[int]')],'bool',['arrays','dynamic-programming','recursion'],
    ['1 <= nums.length <= 20; 0 <= nums[i] <= 10,000,000.',
     'Players alternate taking one value from either end, adding it to their own score. Both choose optimally.',
     'Return whether player 1 can finish with at least player 2\'s score. A tie counts as a win for player 1.'],
    [([[1,5,2]],'Player 1 gets the two end values, totaling 3, while player 2 can secure 5. Player 1 cannot win.'),
     ([[1,5,233,7]],'Choosing 1 first lets player 1 take 233 next, whichever end player 2 chooses. Greedily taking 7 would lose.')],
    [[a] for a in ([0],[1],[0,0],[1,1],[1,2],[2,1],[1,1,1],[1,2,1],[3,1,3],[0,9,0],
      [2,4,55,6,8],[1,20,4,5,6],[10,1,1,10,1],[0,0,0,0,0])],
    GAME,[GAME.replace('>=0','>0'),GREEDY_GAME],
    ['Rejects ties even though they count as first-player wins.', 'Both players greedily take the larger end instead of considering the opponent\'s next choices.'],
    game_oracle,random_game,
    ['Think about the score margin the current player can force on an interval.', 'After choosing an end, the opponent owns the next interval, so subtract their optimal margin.',
     'Cache margin(l,r)=max(nums[l]-margin(l+1,r), nums[r]-margin(l,r-1)); one remaining value is the base case.',
     'Player 1 succeeds exactly when the starting margin is nonnegative. Memoization collapses repeated game-tree intervals to O(n^2) states.'],
    'The recursive margin is measured from the player whose turn it is, so changing turns reverses the sign. '
    'Caching intervals explores both strategic choices without exponential repetition. The independent oracle '
    'enumerates a literal alternating game tree, maximizing player-1 score on their turns and minimizing it on player-2 turns.',
    'O(n^2)','O(n^2)',difficulty=5,
    stress=[([[10**7]*20],True),([[0,10**7]*9+[0]],False),([[10**7]+[0]*18],True)]),
487:entry('longest_ones_one_flip',[('nums','list[int]')],'int',['arrays','sliding-window'],
    ['1 <= nums.length <= 100,000; every value is 0 or 1.',
     'Flip at most one zero, then return the longest consecutive run of ones. An all-one array needs no flip.',
     'The follow-up asks for constant extra memory even when values arrive as a stream; retaining the full prefix is unnecessary.'],
    [([[1,0,1,1,0]],'Flip the first zero to connect the neighboring runs into four ones. Flipping the final zero gives only three.'),
     ([[1,1,0,0,1,1]],'One flip cannot bridge two adjacent zeros. The longest possible run is 3, not the total number of ones plus one.')],
    [[a] for a in ([0],[1],[0,0],[1,1],[0,1],[1,0],[1,0,1],[0,1,0],[1,0,0,1],
      [1,1,0,1],[0,0,1,0,0],[0,1,1,1,0],[1,0,1,0,1],[1,1,0,0,0,1,1])],
    FLIP,['def longest_ones_one_flip(nums):\n    best=run=0\n    for value in nums:\n        run=run+1 if value else 0\n        best=max(best,run)\n    return best\n',
      'def longest_ones_one_flip(nums):\n    return min(len(nums),nums.count(1)+1)\n'],
    ['Never uses the permitted zero flip.', 'Counts separated ones together, ignoring the consecutive-run requirement.'],
    flip_oracle,random_flip,
    ['Only the runs immediately beside one chosen zero can be joined.', 'Keep the current run and the run before the most recent zero, including that zero as one flipped position.',
     'On a one, extend current. On a zero, set before_zero=current+1 and reset current. Update best with before_zero+current.',
     'A second zero replaces the previous bridge. Three counters suffice, and an all-one stream never adds a nonexistent flipped position.'],
    'The two adjacent runs identify the longest valid suffix crossing the most recent zero. Older zeros '
    'cannot participate in that suffix, so their state can be discarded. This supports a one-pass iterator '
    'with constant extra memory. The independent oracle flips each possible zero in a copy and measures literal one-runs.',
    'O(n)','O(1)',difficulty=5,
    stress=[([[1]*100000],100000),([[0]*100000],1),([[1]*49999+[0]+[1]*50000],100000),([[1,0]*50000],3)]),
491:entry('nondecreasing_subsequences',[('nums','list[int]')],'list[list[int]]',['arrays','backtracking','recursion'],
    ['1 <= nums.length <= 15; -100 <= nums[i] <= 100.',
     'Return every distinct non-decreasing subsequence of length at least two. Preserve original index order; equal adjacent values are allowed.',
     'Return each value sequence once even if different index choices produce it. Outer result order is arbitrary, but order inside each sequence is significant.'],
    [([[4,6,7,7]],'Include [7,7] and [4,6,7,7] because equality is allowed. [4,7] appears once, not once for each choice of 7.'),
     ([[4,4,3,2,1]],'Only [4,4] is non-decreasing with at least two entries. Sorting the input would invent subsequences that were never available.')],
    [[a] for a in ([1],[1,2],[2,1],[1,1],[0,0,0],[-1,0,-1,1],[1,2,1,2],[3,2,2,3],
      [-100,100],[-100,-100],[2,3,1,2],[1,2,3,4],[4,3,2,1],[0,1,0,1,0])],
    SUBSEQUENCES,[SUBSEQUENCES.replace('value<path[-1]','value<=path[-1]'),SUBSEQUENCES.replace('value in used or ','')],
    ['Requires strict increase and loses valid repeated values.', 'Repeats the same value sequence for multiple equivalent index choices.'],
    subsequences_oracle,random_subsequences,
    ['Build subsequences in original index order rather than sorting the input.', 'At each recursion level, try a given next value only once; equal values can still appear at deeper levels.',
     'Backtrack from a start index, skip values below the path tail or already used at this depth, and record paths of length at least two.',
     'The depth-local set removes duplicate prefixes without banning repeated values in a single sequence. A global set of used values would be too aggressive.'],
    'Every branch appends a later index whose value does not decrease. Equal-valued choices at the same depth '
    'generate identical or subsumed continuations, so exploring only the earliest avoids duplicate outputs. '
    'The oracle enumerates all index masks, filters by length and order, and deduplicates completed tuples independently.',
    'O(n*2^n)','O(n) auxiliary plus output',difficulty=5,
    stress=[([list(range(15))],subsequences_oracle([list(range(15))])),([[100]*15],[[100]*n for n in range(2,16)]),
            ([list(range(15,0,-1))],[])]),
492:entry('construct_rectangle',[('area','int')],'list[int]',['math'],
    ['1 <= area <= 10,000,000. Return positive integer dimensions [L,W] with L*W == area and L >= W.',
     'Among all such factor pairs, minimize L-W. Returning any rectangle with the correct area is not sufficient.'],
    [([4],'[4,1] has the right area but gap 3. [2,2] has gap 0 and is optimal; [1,4] violates L >= W.'),
     ([37],'37 is prime, so the only correctly oriented factor pair is [37,1]. A near-square pair would have the wrong area.')],
    [[a] for a in (1,2,3,6,8,9,10,12,16,18,25,36,48,100)],
    RECTANGLE,[RECTANGLE.replace('[area//width,width]','[width,area//width]'),'def construct_rectangle(area):\n    return [area,1]\n'],
    ['Returns width before length, reversing nonsquare answers.', 'Uses the most elongated factor pair rather than minimizing the gap.'],
    rectangle_oracle,random_rectangle,
    ['The shorter factor cannot exceed the square root of the area.', 'The largest divisor at or below the square root gives the smallest gap.',
     'Start width=isqrt(area), decrement until it divides area, then return [area//width,width].',
     'Integer square root avoids rounding. Smaller candidate widths force larger lengths and therefore larger gaps.'],
    'For factor pairs with W <= sqrt(area), increasing W decreases L=area/W and narrows the gap. '
    'The first divisor encountered below the integer square root is therefore optimal. The small-input '
    'oracle enumerates every positive candidate length and minimizes the gap among all feasible pairs.',
    'O(sqrt(area))','O(1)',difficulty=3,
    stress=[([10**7],[3200,3125]),([3162**2],[3162,3162])]),
}
BATCH[483]['prerequisites']=['math','binary-search']
BATCH[491]['comparator']='unordered'
