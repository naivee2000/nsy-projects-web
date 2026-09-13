"""Keyboard membership, number representations, rankings, interval DP and flow."""
from collections import deque
from functools import cache
from itertools import product
from math import isqrt
from string import ascii_letters,ascii_lowercase

from .import_batch_003 import entry

KEY_ROWS=('qwertyuiop','asdfghjkl','zxcvbnm')


def keyboard_oracle(args):
    return [word for word in args[0] if any(all(c.lower() in row for c in word) for row in KEY_ROWS)]


def base_oracle(args):
    value=abs(args[0]);power=1
    while power*7<=value:power*=7
    digits=[]
    while power:
        digits.append(str(value//power));value%=power;power//=7
    return ('-' if args[0]<0 else '')+''.join(digits)


def rank_label(rank):
    return {1:'Gold Medal',2:'Silver Medal',3:'Bronze Medal'}.get(rank,str(rank))


def ranks_oracle(args):
    scores=args[0]
    return [rank_label(1+sum(other>value for other in scores)) for value in scores]


def perfect_oracle(args):
    n=args[0]
    return sum(d for d in range(1,n) if n%d==0)==n


def divisor_sum_certificate(n):
    """Choose a prime exponent independently for each divisor; include n itself."""
    remaining=n;prime=2;total=1
    while prime*prime<=remaining:
        power=1;series=1
        while remaining%prime==0:
            remaining//=prime;power*=prime;series+=power
        total*=series;prime+=1
    if remaining>1:total*=remaining+1
    return total


def palindrome_oracle(args):
    s=args[0];best=0
    for mask in range(1,1<<len(s)):
        if mask.bit_count()<=best:continue
        word=''.join(c for i,c in enumerate(s) if mask>>i&1)
        if word==word[::-1]:best=len(word)
    return best


def parallel_successors(state):
    choices=[]
    for i,count in enumerate(state):
        choices.append([0]+([-1] if count and i else [])+([1] if count and i+1<len(state) else []))
    for actions in product(*choices):
        if not any(actions):continue
        next_state=list(state)
        for i,step in enumerate(actions):
            if step:next_state[i]-=1;next_state[i+step]+=1
        yield tuple(next_state)


@cache
def washing_bfs(state):
    n=len(state);total=sum(state)
    if total%n:return -1
    target=(total//n,)*n;queue=deque([(state,0)]);seen={state}
    while queue:
        state,distance=queue.popleft()
        if state==target:return distance
        for successor in parallel_successors(state):
            if successor not in seen:
                seen.add(successor);queue.append((successor,distance+1))


def washing_oracle(args):return washing_bfs(tuple(args[0]))


def random_keyboard(rng):
    words=[]
    for _ in range(rng.randint(1,20)):
        alphabet=rng.choice(KEY_ROWS) if rng.random()<.5 else ascii_lowercase
        word=''.join(rng.choice(alphabet) for _ in range(rng.randint(1,20)))
        words.append(''.join(c.upper() if rng.random()<.5 else c for c in word))
    return [words]


def random_base(rng):return [rng.randint(-10**7,10**7)]
def random_ranks(rng):return [rng.sample(range(1000),rng.randint(1,30))]
def random_perfect(rng):return [rng.choice([6,28,496,8128]) if rng.random()<.35 else rng.randint(1,4000)]
def random_palindrome(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,12)))]
def random_washing(rng):
    n=rng.randint(1,4)
    if rng.random()<.2:return [[rng.randrange(4) for _ in range(n)]]
    values=[0]*n
    for _ in range(n*rng.randrange(3)):values[rng.randrange(n)]+=1
    return [values]


KEYBOARD='''\
def keyboard_row_words(words):
    row_of={char:index for index,row in enumerate(('qwertyuiop','asdfghjkl','zxcvbnm')) for char in row}
    return [word for word in words if len({row_of[c.lower()] for c in word})==1]
'''
BASE='''\
def to_base_seven(num):
    if num==0:return '0'
    value=abs(num);digits=[]
    while value:
        value,digit=divmod(value,7);digits.append(str(digit))
    return ('-' if num<0 else '')+''.join(digits[::-1])
'''
RANKS='''\
def relative_ranks(score):
    result=['']*len(score)
    for rank,index in enumerate(sorted(range(len(score)),key=lambda i:score[i],reverse=True),1):
        result[index]=('Gold Medal','Silver Medal','Bronze Medal')[rank-1] if rank<=3 else str(rank)
    return result
'''
PERFECT='''\
def is_perfect_number(num):
    from math import isqrt
    if num<=1:return False
    total=1
    for divisor in range(2,isqrt(num)+1):
        if num%divisor==0:
            total+=divisor
            partner=num//divisor
            if partner!=divisor:total+=partner
    return total==num
'''
PALINDROME='''\
def longest_palindromic_subsequence(s):
    n=len(s);dp=[0]*n
    for left in range(n-1,-1,-1):
        diagonal=0;dp[left]=1
        for right in range(left+1,n):
            old=dp[right]
            if s[left]==s[right]:dp[right]=diagonal+2
            else:dp[right]=max(dp[right],dp[right-1])
            diagonal=old
    return dp[-1]
'''
WASHING='''\
def minimum_washing_moves(machines):
    total=sum(machines);n=len(machines)
    if total%n:return -1
    average=total//n;balance=best=0
    for count in machines:
        surplus=count-average;balance+=surplus
        best=max(best,abs(balance),surplus)
    return best
'''
SUBSTRING='''\
def longest_palindromic_subsequence(s):
    best=0
    for center in range(len(s)):
        for left,right in ((center,center),(center,center+1)):
            while left>=0 and right<len(s) and s[left]==s[right]:
                best=max(best,right-left+1);left-=1;right+=1
    return best
'''

BATCH={
500:entry('keyboard_row_words',[('words','list[str]')],'list[str]',['strings','hash-maps'],
    ['1 <= words.length <= 20; 1 <= word length <= 100; only English letters, with either case.',
     'Keyboard rows are qwertyuiop, asdfghjkl, and zxcvbnm. ALL letters in a word must belong to one row, ignoring case.',
     'Return the matching original spellings, preserving duplicate input occurrences. Output order is ignored.'],
    [([['Hello','Alaska','Dad','Peace']],'Alaska and Dad use only the middle row after case folding. Hello and Peace mix rows; return ["Alaska","Dad"].'),
     ([['TYPE','type','TYPE','omk']],'The first three words use the top row and all three occurrences remain. Preserve their spelling and repeated TYPE; omk mixes rows.')],
    [[a] for a in (['a'],['A'],['q'],['Z'],['omk'],['adsdf','sfd'],['Qwerty','ASDF','zXc'],
        ['az'],['qp'],['am'],['MOM'],['Dad','Dad'],['yYuU'],['pL'],['cvbn','hello'])],
    KEYBOARD,[KEYBOARD.replace('row_of[c.lower()]','row_of.get(c,-1)'),
              KEYBOARD.replace('return [word for word in words','return [word.lower() for word in words')],
    ['Treats uppercase letters as an unrelated row instead of case-folding them.', 'Changes the returned spelling instead of preserving the matching input words.'],
    keyboard_oracle,random_keyboard,
    ['Map each letter to its keyboard row, without caring about case.',
     'A word qualifies exactly when the set of row numbers used by its letters has size one.',
     'For each original word, inspect lowercase letters but append the original word if all row numbers agree.',
     'Do not deduplicate matching words or lowercase the result. Selection happens independently for every input occurrence.'],
    'Row membership is a property of every letter, not just the first and last. '
    'Case folding is used only for checking; output retains the original spelling and '
    'multiplicity. This personal judge ignores result ordering because this is a word-selection '
    'task. The reference retains input order. The independent oracle tries each literal '
    'row and checks every character for membership.',
    'O(C), C=total input characters','O(1) auxiliary, excluding output',difficulty=3,
    stress=[([['QwErTyUiOp'*10]*20],['QwErTyUiOp'*10]*20),
            ([['q'*99+'a']*20],[]),([['z'*100,'A'*100,'p'*100]],['z'*100,'A'*100,'p'*100])]),
504:entry('to_base_seven',[('num','int')],'str',['math','strings'],
    ['-10,000,000 <= num <= 10,000,000.',
     'Return ordinary base-7 digits 0 through 6, most significant first. Zero is "0"; negatives have one leading minus sign and no leading zeros.'],
    [([100],'100 = 2*49 + 0*7 + 2, so return "202". The middle zero is a real place value.'),
     ([-7],'The magnitude 7 is "10" in base 7. Attach the sign to return "-10", not a decimal string or reversed digits.')],
    [[n] for n in (0,1,-1,6,-6,7,8,-8,48,49,50,343,-49,344,2401)],
    BASE,[BASE.replace('digits[::-1]','digits'),BASE.replace("('-' if num<0 else '')", "''")],
    ['Emits least-significant digits first.', 'Loses the sign of negative input.'],base_oracle,random_base,
    ['Division by seven separates the remaining prefix from the final digit.',
     'Repeatedly collect remainders from the nonnegative magnitude, then reverse them.',
     'Handle zero explicitly; repeatedly divmod(abs(num),7), reverse digits, and prepend minus only for negative num.',
     'Using the magnitude avoids Python negative-division behavior. Internal zero digits must remain in their positions.'],
    'After dividing by seven, the remainder is the lowest base-7 digit. Repetition '
    'therefore discovers digits in reverse order. Separate sign handling and the zero '
    'case give a canonical representation. The independent oracle extracts leading '
    'digits using descending powers of seven, rather than collecting remainders.',
    'O(log(|num|+1))','O(log(|num|+1))',difficulty=3,
    stress=[([n],base_oracle([n])) for n in (-10**7,10**7,-7**8,7**8,7**8-1,7**8+1)]),
506:entry('relative_ranks',[('score','list[int]')],'list[str]',['arrays','sorting'],
    ['1 <= score.length <= 10,000; scores are UNIQUE integers from 0 to 1,000,000.',
     'Higher score means better placement. Places 1,2,3 are Gold Medal, Silver Medal, Bronze Medal; later places are decimal strings.',
     'Return each label at its ORIGINAL athlete index, not in sorted score order.'],
    [([[5,4,3,2,1]],'These athletes are already in descending score order, so the labels are Gold, Silver, Bronze, "4", "5".'),
     ([[10,3,8,9,4]],'Placements in original order are 1,5,3,2,4. The score 9 gets Silver Medal at index 3, not at output index 1.')],
    [[a] for a in ([0],[1],[1,0],[0,1],[2,1,0],[0,1,2],[2,0,1],[3,0,2,1],
        [1,2,3,4],[4,1,3,2],[1000000,0,5],[9,7,5,3,1,0],[0,1000000],[10,20,30,40,50,60])],
    RANKS,[RANKS.replace('result[index]=','result[rank-1]='),RANKS.replace('reverse=True','reverse=False')],
    ['Returns labels in ranking order instead of original athlete order.', 'Awards the best placements to the lowest scores.'],
    ranks_oracle,random_ranks,
    ['Sort athlete indices, not just scores, so you can restore original positions.',
     'Walk indices by descending score and translate one-based placements to labels.',
     'For each ranked index, write its medal or numeric rank string into answer[index].',
     'Scores are unique, so there is no tie rule. Numeric placements must be strings, and the output order remains the input order.'],
    'Sorting indices separates rank order from output order. The original index is '
    'where each label belongs, regardless of the order in which ranks are assigned. '
    'The independent oracle counts how many scores are strictly larger for each athlete.',
    'O(n log n)','O(n)',difficulty=3,
    stress=[([list(range(10000))],[rank_label(10000-i) for i in range(10000)]),
            ([list(range(10000,0,-1))],[rank_label(i+1) for i in range(10000)]),
            ([[(i*7919)%10000 for i in range(10000)]],[rank_label(10000-(i*7919)%10000) for i in range(10000)])]),
507:entry('is_perfect_number',[('num','int')],'bool',['math'],
    ['1 <= num <= 100,000,000.',
     'Sum all positive divisors STRICTLY smaller than num. Return whether this sum equals num exactly; an abundant number is not perfect.'],
    [([28],'The proper divisors are 1,2,4,7,14. Their sum is 28, so return true; 28 itself is excluded.'),
     ([12],'The proper divisors sum to 1+2+3+4+6=16. Return false: being greater than 12 does not count as equality.')],
    [[n] for n in (1,2,3,4,6,7,8,9,16,18,25,36,49,496,8128,100)],
    PERFECT,[PERFECT.replace('total=1','total=1+num'),PERFECT.replace('return total==num','return total>=num')],
    ['Includes the number itself among its proper divisors.', 'Accepts abundant numbers rather than requiring exact equality.'],
    perfect_oracle,random_perfect,
    ['Divisors come in pairs d and num//d.',
     'Inspect d only through the integer square root and add each partner once.',
     'Reject 1; start the sum at 1; for every divisor from 2 through isqrt(num), add it and its distinct partner; compare with num.',
     'Do not add num itself, and do not count the square-root divisor twice for a square.'],
    'Every non-unit proper divisor pair has one member at most sqrt(num). This '
    'lets us enumerate all pairs without scanning up to num. A square-root pair '
    'contributes only once. The small oracle literally tests every positive integer '
    'below num; a separate prime-factor divisor-sum certificate checks large fixtures.',
    'O(sqrt(num))','O(1)',difficulty=3,
    stress=[([n],divisor_sum_certificate(n)==2*n) for n in (33550336,10**8,99999999,99980001,2**26,33550335)]),
516:entry('longest_palindromic_subsequence',[('s','str')],'int',['strings','dynamic-programming','recursion'],
    ['1 <= len(s) <= 1000; only lowercase English letters.',
     'A subsequence may skip characters but cannot reorder them. Return its maximum palindromic LENGTH, not a substring or a rearranged palindrome.'],
    [(['bbbab'],'Skip the a to obtain "bbbb", a palindrome of length 4. The selected characters need not be contiguous.'),
     (['abcab'],'Return 3, for example "aba" or "bcb". Although these letters can be rearranged into a length-5 palindrome, reordering is forbidden.')],
    [[s] for s in ('a','aa','ab','aba','abba','abc','cbbd','abcd','aaaa','abca','agbdba','character','aabbaa','abcabc','abcdc')],
    PALINDROME,[SUBSTRING,
       "def longest_palindromic_subsequence(s):\n    from collections import Counter\n    counts=Counter(s).values()\n    return sum(c//2*2 for c in counts)+int(any(c%2 for c in counts))\n"],
    ['Finds only contiguous palindromic substrings.', 'Rearranges a letter multiset rather than preserving subsequence order.'],
    palindrome_oracle,random_palindrome,
    ['Consider a substring interval while selecting a subsequence inside it.',
     'Matching endpoints can surround an optimal inner palindrome; otherwise skip either endpoint.',
     'Process left endpoints backward. Before updating dp[right], save its old value; matching ends use old diagonal+2, otherwise max(below,left).',
     'A one-dimensional table preserves the interval recurrence in O(n) space. Save the previous diagonal before overwriting it, and initialize every single character to length one.'],
    'For equal endpoints, an optimal inner subsequence can be surrounded by the '
    'two equal characters. Otherwise at least one endpoint is absent, so take the '
    'larger result after dropping either end. Bottom-up evaluation implements this '
    'recursive interval relation without a length-1000 recursion stack. One row '
    'plus the old diagonal is sufficient. The independent oracle enumerates every '
    'index subset and checks its literal selected string for palindrome equality.',
    'O(n^2)','O(n)',difficulty=5,
    stress=[(['a'*1000],1000),(['a'*500+'b'*500],500),(['ab'*500],999),
            (['a'*499+'b'+'a'*500],999)]),
517:entry('minimum_washing_moves',[('machines','list[int]')],'int',['arrays','greedy','prefix-sums'],
    ['1 <= machines.length <= 10,000; each load is an integer from 0 to 100,000.',
     'In one simultaneous move, any nonempty set of machines may each send ONE dress to ONE adjacent machine. A machine cannot send to both neighbors in one move.',
     'A machine may receive from both neighbors and may send a dress it already held while receiving. An initially empty machine cannot forward a newly received dress in that same move.',
     'Return the minimum moves to equalize every load; return -1 if the total is not divisible by the number of machines. Already equal loads need zero moves.'],
    [([[1,0,5]],'Three simultaneous rounds suffice: [1,0,5] → [1,1,4] → [2,1,3] → [2,2,2]. The last machine must send its three excess dresses in separate rounds.'),
     ([[3,0,3]],'Return 1: both ends send one dress to the middle simultaneously, producing [2,2,2]. Receiving two dresses at once is allowed; sending two is not.')],
    [[a] for a in ([0],[5],[0,0],[1,1],[0,2],[2,0],[0,3,0],[0,2,0],[0,0,3],[3,0,0],
        [1,2,3],[4,0,0,0],[0,4,0,0],[0,0,4,0],[2,0,2,0],[0,2,0,2],[1,0,2],[0,0,0])],
    WASHING,[WASHING.replace('max(best,abs(balance),surplus)','max(best,abs(balance))'),
             WASHING.replace('max(best,abs(balance),surplus)','max(best,abs(balance),abs(surplus))')],
    ['Checks edge flow but ignores a machine that must send excess dresses in both directions.', 'Treats a receiving deficit like an outgoing bottleneck, disallowing parallel receipt from both sides.'],
    washing_oracle,random_washing,
    ['The target load must be the integer average; every prefix has a net surplus or deficit.',
     'Each edge must carry the absolute prefix imbalance. Also, a machine can send at most one of its own surplus dresses per round.',
     'Accumulate balance += load-average and update answer with abs(balance) and load-average. Reject indivisible totals first.',
     'Do not take the absolute value of the local surplus: receiving from two sides can happen together, but sending to two sides needs separate rounds.'],
    'Conservation fixes the net flow across each edge to the prefix imbalance, '
    'giving a lower bound of its absolute value. If a machine supplies both sides, '
    'its outgoing requirements add to load-average, another lower bound because '
    'it sends at most one dress per round. Otherwise flows can pass through in '
    'parallel while receiving. On a line, these directed flows can be pipelined, '
    'meeting the maximum of the edge and combined-outgoing bottlenecks; no '
    'per-round simulation is needed. The independent oracle instead performs '
    'BFS over load vectors and enumerates every simultaneous legal send choice '
    'from the pre-move state. It shares no prefix-bound calculation with the reference.',
    'O(n)','O(1)',difficulty=8,
    stress=[([[100000]+[0]*9999],99990),([[0]*4999+[100000]+[0]*5000],99990),
            ([[100000]*10000],0),([[0,100000]*5000],50000),
            ([[100000]*5000+[0]*5000],250000000),([[100000]*9999+[99999]],-1)])
}
BATCH[500]['comparator']='unordered'
BATCH[517]['prerequisites']=['greedy','prefix-sums']
for spec in BATCH.values():spec['statement']=' '.join(spec['constraints'][1:])
