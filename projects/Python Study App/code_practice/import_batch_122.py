"""First slice of workbook batch 122."""

from functools import lru_cache
from itertools import product
from math import gcd

from .import_batch_055 import entry


def merge_oracle(args):
    answer = []
    total = 0
    for value in args[0][1:]:
        if value == 0:
            answer.append(total)
            total = 0
        else:
            total += value
    return answer


def random_merge(rng):
    values = [0]
    for _ in range(rng.randint(1, 8)):
        values.extend(rng.randint(1, 20) for _ in range(rng.randint(1, 5)))
        values.append(0)
    return [values]


def limited_oracle(args):
    s, limit = args
    counts = [s.count(chr(97 + index)) for index in range(26)]

    @lru_cache(None)
    def search(state, last, run):
        best = ""
        values = list(state)
        for index in range(26):
            if values[index] == 0 or (index == last and run == limit):
                continue
            values[index] -= 1
            suffix = search(tuple(values), index, run + 1 if index == last else 1)
            values[index] += 1
            best = max(best, chr(97 + index) + suffix)
        return best

    return search(tuple(counts), -1, 0)


def random_limited(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 9))), rng.randint(1, 4)]


def pairs_oracle(args):
    nums, k = args
    return sum(nums[i] * nums[j] % k == 0 for i in range(len(nums)) for j in range(i + 1, len(nums)))


def random_pairs(rng):
    return [[rng.randint(1, 60) for _ in range(rng.randint(1, 30))], rng.randint(1, 30)]


def wall_rows(width, bricks):
    masks = []

    def build(position, mask):
        if position == width:
            masks.append(mask)
            return
        for brick in bricks:
            end = position + brick
            if end <= width:
                build(end, mask | ((1 << end) if end < width else 0))

    build(0, 0)
    return masks


def wall_oracle(args):
    height, width, bricks = args
    rows = wall_rows(width, bricks)
    count = 0
    for chosen in product(rows, repeat=height):
        if all(chosen[index] & chosen[index - 1] == 0 for index in range(1, height)):
            count += 1
    return count % 1_000_000_007


def random_wall(rng):
    width = rng.randint(1, 6)
    bricks = rng.sample(range(1, width + 1), rng.randint(1, width))
    if not wall_rows(width, bricks):
        bricks.append(width)
    return [rng.randint(1, 3), width, sorted(set(bricks))]


def prefix_oracle(args):
    words, prefix = args
    return sum(word[: len(prefix)] == prefix for word in words)


def random_prefix(rng):
    words = ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 8))) for _ in range(rng.randint(1, 20))]
    return [words, "".join(rng.choice("abcd") for _ in range(rng.randint(1, 4)))]


MERGE = '''\
def merge_nodes_between_zeros(head):
    dummy=ListNode(0);tail=dummy;node=head.next;total=0
    while node:
        if node.val==0:
            tail.next=ListNode(total);tail=tail.next;total=0
        else:total+=node.val
        node=node.next
    return dummy.next
'''

LIMITED = '''\
def largest_repeat_limited_string(s,repeat_limit):
    from collections import Counter
    counts=Counter(s);answer=[]
    while counts:
        largest=max(counts);take=min(counts[largest],repeat_limit)
        answer.append(largest*take);counts[largest]-=take
        if counts[largest]==0:del counts[largest];continue
        smaller=[char for char in counts if char<largest]
        if not smaller:break
        breaker=max(smaller);answer.append(breaker);counts[breaker]-=1
        if counts[breaker]==0:del counts[breaker]
    return ''.join(answer)
'''

PAIRS = '''\
def count_product_divisible_pairs(nums,k):
    from collections import Counter
    from math import gcd
    counts=Counter();answer=0
    for value in nums:
        factor=gcd(value,k)
        answer+=sum(amount for other,amount in counts.items() if factor*other%k==0)
        counts[factor]+=1
    return answer
'''

WALL = '''\
def count_sturdy_brick_walls(height,width,bricks):
    modulo=1_000_000_007;rows=[]
    def build(position,mask):
        if position==width:rows.append(mask);return
        for brick in bricks:
            end=position+brick
            if end<=width:build(end,mask|((1<<end) if end<width else 0))
    build(0,0)
    compatible=[[j for j,other in enumerate(rows) if mask&other==0] for mask in rows]
    ways=[1]*len(rows)
    for _ in range(1,height):
        ways=[sum(ways[previous] for previous in compatible[current])%modulo for current in range(len(rows))]
    return sum(ways)%modulo
'''

PREFIX = '''\
def count_words_with_prefix(words,pref):
    return sum(word.startswith(pref) for word in words)
'''


BATCH = {
    2181: entry('merge_nodes_between_zeros',[('head','ListNode')],'ListNode | None',['linked lists','simulation'],['The linked list begins and ends with zero, with no consecutive zero nodes.','Sum each nonempty group strictly between consecutive zeros.','Return a new list containing one sum per group and no zero separator nodes.'],[([[0,3,1,0,4,5,2,0]],'The groups 3+1 and 4+5+2 become the list [4,11].'),([[0,1,0,3,0,2,2,0]],'The three groups sum to 1, 3, and 4.')],[[x] for x in [[0,1,0],[0,5,5,0],[0,1,0,2,0],[0,3,1,0,4,5,2,0],[0,1,0,3,0,2,2,0],[0,9,8,7,0],[0,1,2,3,4,0],[0,10,0,20,0,30,0],[0,2,2,0,2,2,0],[0,100,1,0],[0,6,0,7,8,0],[0,4,3,2,1,0],[0,1,1,1,0,2,2,0],[0,5,0,1,2,3,0]]],MERGE,[MERGE.replace('total=0\n        else','total=0\n            tail.next=ListNode(0);tail=tail.next\n        else'),MERGE.replace('total+=node.val','total=node.val')],['Adds an extra zero result node after every completed group.','Keeps only the final value of each group instead of its sum.'],merge_oracle,random_merge,['Zero nodes are delimiters, so keep a running group total.','Skip the initial zero; accumulate positive values and emit a node whenever the next zero appears.','Maintain a dummy output tail, append ListNode(total) at each separator, reset total, and return dummy.next.','Each input value belongs to exactly one delimiter-bounded group and contributes once to exactly one output node.'],'O(n)','O(groups)',5),
    2182: entry('largest_repeat_limited_string',[('s','str'),('repeat_limit','int')],'str',['strings','greedy','counting'],['Use each available lowercase character at most as many times as it occurs; unused characters are allowed.','No character may occur more than repeat_limit times consecutively.','Return the lexicographically largest valid string.'],[(['cczazcc',3],'Use the two z characters first, then three c characters, a as a breaker, and the final c: zzcccac.'),(['aababab',2],'The lexicographically largest construction is bbabaa.')],[[s,k] for s,k in [('a',1),('aa',1),('aa',2),('ab',1),('zzza',2),('cczazcc',3),('aababab',2),('abcabc',1),('bbbaaac',2),('zzzzy',3),('aaaaab',2),('dcba',1),('ccbbbba',2),('xyzzzz',1)]],LIMITED,[LIMITED.replace('take=min(counts[largest],repeat_limit)','take=counts[largest]'),LIMITED.replace('breaker=max(smaller)','breaker=min(smaller)')],['Uses the entire largest-character count at once and can violate the repeat limit.','Chooses the smallest available breaker, making the result lexicographically smaller.'],limited_oracle,random_limited,['Always prefer the largest character that can legally extend the answer.','Take up to repeat_limit copies of the largest remaining character; if copies remain, insert the largest smaller breaker.','Maintain character counts, repeatedly append the largest run, then one best breaker when required.','Any smaller choice while a larger legal character exists makes the string lexicographically worse; the largest breaker preserves the best possible next position.'],'O(n*alphabet)','O(alphabet)',6),
    2183: entry('count_product_divisible_pairs',[('nums','list[int]'),('k','int')],'int',['arrays','greatest common divisors','counting'],['Count pairs of indices i<j whose value product is divisible by k.','Array values and k are positive integers.','Return the number of qualifying pairs, which may exceed 32-bit range.'],[([[1,2,3,4,5],2],'Every pair containing an even value qualifies, producing seven pairs.'),([[1,2,3,4],5],'No product contains factor five, so return zero.')],[[a,k] for a,k in [([1],1),([1,1],1),([1,2],2),([1,2,3,4,5],2),([1,2,3,4],5),([2,4,6],4),([3,6,9],6),([5,10,15,20],10),([2,3,5,7],30),([6,10,15],30),([1,1,1,1],2),([12,18,24],6),([7,14,21,28],7),([4,8,16,32],16)]],PAIRS,[PAIRS.replace('factor*other%k==0','factor*other==k'),PAIRS.replace('factor*other%k==0','(factor+other)%k==0')],['Requires gcd factors to multiply to exactly k and misses qualifying products with extra factors.','Tests the sum of gcd factors instead of their product.'],pairs_oracle,random_pairs,['Only the factors a value shares with k affect whether a pair product covers k.','Group previous values by gcd(value,k), then test the small set of gcd categories.','For each value, sum prior category counts where current_gcd*other_gcd is divisible by k, then record it.','Replacing values by their gcd with k preserves exactly the prime factors relevant to divisibility by k, and each prior pair is counted once.'],'O(n*d(k))','O(d(k))',8),
    2184: entry('count_sturdy_brick_walls',[('height','int'),('width','int'),('bricks','list[int]')],'int',['dynamic programming','bit masks','backtracking'],['Each row exactly fills width using unlimited bricks from the distinct positive widths list.','Adjacent rows may not share an internal vertical seam; the two outer wall edges do not count.','Return the number of height-row walls modulo 1,000,000,007.'],[([2,3,[1,2]],'The compatible row sequences [1,2] over [2,1] and the reverse give two sturdy walls.'),([1,2,[1,2]],'A one-row wall may use [2] or [1,1], so return two.')],[[h,w,b] for h,w,b in [(1,1,[1]),(1,2,[1,2]),(2,2,[1,2]),(2,3,[1,2]),(3,3,[1,2]),(2,4,[1,2]),(2,5,[2,3]),(3,5,[1,2,3]),(2,6,[2,3]),(4,4,[1,3]),(3,6,[1,2,3]),(2,7,[2,5]),(3,4,[2]),(2,8,[1,3,4])]],WALL,[WALL.replace('mask&other==0','mask==other'),WALL.replace('ways=[1]*len(rows)','ways=[0]*len(rows)')],['Treats identical seam masks as compatible and rejects many genuinely disjoint rows.','Initializes every possible first row with zero ways.'],wall_oracle,random_wall,['A row matters to the next row only through its internal seam positions.','Enumerate every row seam mask, precompute pairs with no shared set bit, then use height-layer DP.','Start one way per row; for each higher layer sum prior ways from compatible masks and apply the modulus.','Every sturdy wall is a sequence of row masks with pairwise-adjacent compatibility, exactly the transitions counted by the DP.'],'O(R^2+height*R^2)','O(R^2)',7),
    2185: entry('count_words_with_prefix',[('words','list[str]'),('pref','str')],'int',['arrays','strings'],['words and pref contain lowercase English letters.','Count a word exactly when its first len(pref) characters equal pref.','A word shorter than pref does not match.'],[([['pay','attention','practice','attend'],'at'],'attention and attend begin with at, so return two.'),([['leetcode','win','loops','success'],'code'],'No word begins with code, so return zero.')],[[w,p] for w,p in [(['a'],'a'),(['a'],'aa'),(['ab','ac'],'a'),(['pay','attention','practice','attend'],'at'),(['leetcode','win','loops','success'],'code'),(['apple','app','ape'],'app'),(['x','xy','xyz'],'x'),(['same','same'],'same'),(['abc','xbc','ab'],'ab'),(['prefix','prelude','prevent'],'pre'),(['cat','dog'],'c'),(['aaaa','aaab','baaa'],'aaa'),(['hello'],'h'),(['zoo','zoom','zone'],'zo')]],PREFIX,[PREFIX.replace('word.startswith(pref)','word==pref'),PREFIX.replace('word.startswith(pref)','pref in word')],['Counts only words exactly equal to the prefix.','Counts the prefix anywhere in a word instead of only at its start.'],prefix_oracle,random_prefix,['This is a direct prefix predicate per word.','Use startswith so short words and mismatches are handled correctly.','Sum the boolean result of word.startswith(pref) across words.','The predicate is true exactly for the words defined by the problem, and each word contributes at most one to the count.'],'O(total characters checked)','O(1)',3),
}

BATCH[2181]['params'][0] = ('head', 'ListNode', 'listnode')
BATCH[2181]['adapter'] = 'listnode'
