"""Reviewed array, string, counting, dynamic-programming, and graph imports."""
from collections import Counter, deque
from itertools import combinations
from math import isqrt

from . import import_batch_055 as batch_base
from .import_batch_055 import entry as base_entry


batch_base.EXTRA_BOUNDARIES.update({
    'self_dividing_numbers': [[2, 9]],
    'largest_monotone_number': [[21]],
    'minimum_reach_steps': [[9]],
})


def entry(*args, **kwargs):
    """Normalize the one unsupported midpoint rating to the catalog's Medium rubric."""
    values = list(args)
    if values and values[-1] == 4:
        values[-1] = 5
    return base_entry(*values, **kwargs)


def repeated_oracle(args):
    left, right = args
    return max((size for size in range(min(len(left), len(right)) + 1)
                if any(left[i:i + size] == right[j:j + size]
                       for i in range(len(left) - size + 1)
                       for j in range(len(right) - size + 1))), default=0)


def longest_oracle(args):
    words = set(args[0])
    valid = [word for word in words if all(word[:size] in words for size in range(1, len(word) + 1))]
    return min(valid, key=lambda word: (-len(word), word), default='')


def comments_oracle(args):
    text = '\n'.join(args[0]); output = []; index = 0; block = False; line = []
    while index < len(text):
        pair = text[index:index + 2]
        if block and pair == '*/': block = False; index += 2
        elif block: index += 1
        elif pair == '/*': block = True; index += 2
        elif pair == '//':
            while index < len(text) and text[index] != '\n': index += 1
        elif text[index] == '\n':
            if line: output.append(''.join(line)); line = []
            index += 1
        else: line.append(text[index]); index += 1
    if line: output.append(''.join(line))
    return output


def self_dividing_oracle(args):
    left, right = args
    return [value for value in range(left, right + 1)
            if '0' not in str(value) and all(value % int(char) == 0 for char in str(value))]


def similar_oracle(args):
    first, second, pairs = args
    allowed = {tuple(pair) for pair in pairs} | {(b, a) for a, b in pairs}
    return len(first) == len(second) and all(a == b or (a, b) in allowed for a, b in zip(first, second))


def asteroids_oracle(args):
    values = args[0][:]
    while True:
        changed = False; following = []; index = 0
        while index < len(values):
            if index + 1 < len(values) and values[index] > 0 > values[index + 1]:
                left, right = values[index], values[index + 1]; changed = True
                if abs(left) > abs(right): following.append(left)
                elif abs(right) > abs(left): following.append(right)
                index += 2
            else: following.append(values[index]); index += 1
        values = following
        if not changed: return values


def monotone_oracle(args):
    def valid(value):
        digits = str(value)
        return all(a <= b for a, b in zip(digits, digits[1:]))
    return next(value for value in range(args[0], -1, -1) if valid(value))


def earn_oracle(args):
    counts = Counter(args[0]); values = sorted(counts)
    best = 0
    for mask in range(1 << len(values)):
        chosen = [values[i] for i in range(len(values)) if mask >> i & 1]
        if all(b - a > 1 for a, b in zip(chosen, chosen[1:])):
            best = max(best, sum(value * counts[value] for value in chosen))
    return best


def delay_oracle(args):
    times, n, start = args; infinity = 10**18; distance = [infinity] * (n + 1); distance[start] = 0
    for _ in range(n - 1):
        changed = False
        for source, target, weight in times:
            if distance[source] + weight < distance[target]:
                distance[target] = distance[source] + weight; changed = True
        if not changed: break
    answer = max(distance[1:])
    return -1 if answer == infinity else answer


def letter_oracle(args):
    letters, target = args
    return min((letter for letter in letters if letter > target), default=letters[0])


def dominant_oracle(args):
    nums = args[0]; largest = max(nums); index = nums.index(largest)
    return index if all(i == index or largest >= 2 * value for i, value in enumerate(nums)) else -1


def completing_oracle(args):
    plate, words = args
    need = Counter(char.lower() for char in plate if char.isalpha())
    return min((word for word in words if not (need - Counter(word))), key=len)


def rectangles_oracle(args):
    grid = args[0]
    return sum(grid[top][left] and grid[top][right] and grid[bottom][left] and grid[bottom][right]
               for top, bottom in combinations(range(len(grid)), 2)
               for left, right in combinations(range(len(grid[0])), 2))


def lock_oracle(args):
    dead, target = set(args[0]), args[1]
    if '0000' in dead: return -1
    queue = deque([('0000', 0)]); seen = {'0000'} | dead
    while queue:
        state, steps = queue.popleft()
        if state == target: return steps
        for index in range(4):
            for delta in (-1, 1):
                digits = list(state); digits[index] = str((int(digits[index]) + delta) % 10); following = ''.join(digits)
                if following not in seen: seen.add(following); queue.append((following, steps + 1))
    return -1


def reach_oracle(args):
    target = abs(args[0]); positions = {0}; steps = 0
    while target not in positions:
        steps += 1; positions = {position + delta for position in positions for delta in (-steps, steps)}
    return steps


def mapping_oracle(args):
    first, second = args
    return [next(index for index, value in enumerate(second) if value == target) for target in first]


def prime_bits_oracle(args):
    def prime(value): return value >= 2 and all(value % factor for factor in range(2, isqrt(value) + 1))
    return sum(prime(bin(value).count('1')) for value in range(args[0], args[1] + 1))


def labels_oracle(args):
    text = args[0]; answer = []; start = 0
    while start < len(text):
        for end in range(start + 1, len(text) + 1):
            inside = set(text[start:end]); outside = set(text[:start] + text[end:])
            if not inside & outside: answer.append(end - start); start = end; break
    return answer


def toeplitz_oracle(args):
    grid = args[0]; diagonals = {}
    for row in range(len(grid)):
        for column in range(len(grid[0])): diagonals.setdefault(row - column, set()).add(grid[row][column])
    return all(len(values) == 1 for values in diagonals.values())


def jewels_oracle(args):
    jewels, stones = args
    return sum(any(stone == jewel for jewel in jewels) for stone in stones)


def random_repeated(rng): return [[rng.randrange(5) for _ in range(rng.randint(1, 10))], [rng.randrange(5) for _ in range(rng.randint(1, 10))]]
def random_longest(rng):
    words = {''.join(rng.choice('abc') for _ in range(rng.randint(1, 5))) for _ in range(rng.randint(1, 12))}
    return [list(words or {'a'})]
def random_comments(rng):
    return [rng.choice([['a//x', 'b'], ['a/*x*/b'], ['/*x', 'y*/z'], ['a', '//x', 'b'], ['a/*x', 'y', 'z*/b']])]
def random_self(rng):
    left = rng.randint(1, 300); return [left, left + rng.randint(0, 80)]
def random_similar(rng):
    vocab = list('abcdef'); size = rng.randint(1, 8); first = [rng.choice(vocab) for _ in range(size)]; second = [rng.choice(vocab) for _ in range(size)]
    pairs = [list(pair) for pair in rng.sample([(a, b) for a in vocab for b in vocab if a != b], rng.randint(0, 8))]
    return [first, second, pairs]
def random_asteroids(rng): return [[rng.choice([value for value in range(-8, 9) if value]) for _ in range(rng.randint(1, 10))]]
def random_monotone(rng): return [rng.randint(0, 5000)]
def random_earn(rng): return [[rng.randint(1, 9) for _ in range(rng.randint(1, 12))]]
def random_delay(rng):
    n = rng.randint(2, 7); edges = [[u, v, rng.randint(0, 9)] for u in range(1, n + 1) for v in range(1, n + 1) if u != v and rng.random() < .25]
    return [edges or [[1, 2, 1]], n, rng.randint(1, n)]
def random_letter(rng):
    letters = sorted(set(rng.choice('abcdef') for _ in range(rng.randint(1, 8)))); return [letters, rng.choice('abcdef')]
def random_dominant(rng): return [[rng.randint(0, 50) for _ in range(rng.randint(1, 10))]]
def random_completing(rng):
    words = [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 8))) for _ in range(8)]; chosen = rng.choice(words)
    letters = list(chosen); rng.shuffle(letters); plate = ''.join(letters[:rng.randint(1, len(letters))])
    return [plate, words + [chosen]]
def random_rectangles(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6); return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]
def random_lock(rng):
    target = ''.join(rng.choice('019') for _ in range(2)) + '00'
    return [[], target]
def random_reach(rng): return [rng.randint(-50, 50)]
def random_mapping(rng):
    values = rng.sample(range(-50, 51), rng.randint(1, 12)); other = values[:]; rng.shuffle(other); return [values, other]
def random_prime_bits(rng):
    left = rng.randint(1, 900); return [left, left + rng.randint(0, 100)]
def random_labels(rng): return [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 18)))]
def random_toeplitz(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6); return [[[rng.randint(0, 4) for _ in range(columns)] for _ in range(rows)]]
def random_jewels(rng):
    alphabet = 'abcXYZ'; jewels = ''.join(rng.sample(alphabet, rng.randint(1, 4))); stones = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 30))); return [jewels, stones]


REPEATED = '''\
def repeated_subarray_length(nums1, nums2):
    dp=[0]*(len(nums2)+1);answer=0
    for left in nums1:
        following=[0]*(len(nums2)+1)
        for index,right in enumerate(nums2,1):
            if left==right:following[index]=dp[index-1]+1;answer=max(answer,following[index])
        dp=following
    return answer
'''
LONGEST = '''\
def longest_buildable_word(words):
    built={''};answer=''
    for word in sorted(words,key=lambda value:(len(value),value)):
        if word[:-1] in built:
            built.add(word)
            if len(word)>len(answer):answer=word
    return answer
'''
COMMENTS = '''\
def strip_source_comments(source):
    answer=[];line=[];block=False
    for text in source:
        index=0
        while index<len(text):
            if block:
                if text[index:index+2]=='*/':block=False;index+=2
                else:index+=1
            elif text[index:index+2]=='/*':block=True;index+=2
            elif text[index:index+2]=='//':break
            else:line.append(text[index]);index+=1
        if not block and line:answer.append(''.join(line));line=[]
    return answer
'''
SELF_DIVIDING = '''\
def self_dividing_numbers(left, right):
    answer=[]
    for value in range(left,right+1):
        remaining=value
        while remaining and remaining%10 and value%(remaining%10)==0:remaining//=10
        if remaining==0:answer.append(value)
    return answer
'''
SIMILAR = '''\
def sentences_are_similar(sentence1, sentence2, similar_pairs):
    if len(sentence1)!=len(sentence2):return False
    pairs={tuple(pair) for pair in similar_pairs}
    return all(a==b or (a,b) in pairs or (b,a) in pairs for a,b in zip(sentence1,sentence2))
'''
ASTEROIDS = '''\
def surviving_asteroids(asteroids):
    stack=[]
    for asteroid in asteroids:
        while stack and stack[-1]>0>asteroid and stack[-1]<-asteroid:stack.pop()
        if stack and stack[-1]>0>asteroid:
            if stack[-1]==-asteroid:stack.pop()
        else:stack.append(asteroid)
    return stack
'''
MONOTONE = '''\
def largest_monotone_number(n):
    digits=list(str(n));mark=len(digits)
    for index in range(len(digits)-1,0,-1):
        if digits[index-1]>digits[index]:digits[index-1]=str(int(digits[index-1])-1);mark=index
    digits[mark:]=['9']*(len(digits)-mark)
    return int(''.join(digits))
'''
EARN = '''\
def maximum_delete_earn(nums):
    from collections import Counter
    points=Counter(nums);avoid=using=0;previous=None
    for value in sorted(points):
        gain=value*points[value]
        if previous is not None and value==previous+1:avoid,using=max(avoid,using),avoid+gain
        else:avoid,using=max(avoid,using),max(avoid,using)+gain
        previous=value
    return max(avoid,using)
'''
DELAY = '''\
def network_delay(times, n, k):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n+1)]
    for source,target,weight in times:graph[source].append((weight,target))
    heap=[(0,k)];distance={}
    while heap:
        elapsed,node=heappop(heap)
        if node in distance:continue
        distance[node]=elapsed
        for weight,target in graph[node]:
            if target not in distance:heappush(heap,(elapsed+weight,target))
    return max(distance.values()) if len(distance)==n else -1
'''
LETTER = '''\
def next_greater_letter(letters, target):
    left,right=0,len(letters)
    while left<right:
        middle=(left+right)//2
        if letters[middle]<=target:left=middle+1
        else:right=middle
    return letters[left%len(letters)]
'''
DOMINANT = '''\
def dominant_index(nums):
    largest=max(range(len(nums)),key=nums.__getitem__)
    second=max((value for index,value in enumerate(nums) if index!=largest),default=0)
    return largest if nums[largest]>=2*second else -1
'''
COMPLETING = '''\
def shortest_completing_word(license_plate, words):
    from collections import Counter
    need=Counter(char.lower() for char in license_plate if char.isalpha())
    return next(word for word in sorted(words,key=len) if not (need-Counter(word)))
'''
RECTANGLES = '''\
def corner_rectangle_count(grid):
    from collections import Counter
    pairs=Counter();answer=0
    for row in grid:
        columns=[index for index,value in enumerate(row) if value]
        for left in range(len(columns)):
            for right in range(left+1,len(columns)):
                pair=(columns[left],columns[right]);answer+=pairs[pair];pairs[pair]+=1
    return answer
'''
LOCK = '''\
def minimum_lock_turns(deadends, target):
    from collections import deque
    blocked=set(deadends)
    if '0000' in blocked:return -1
    queue=deque([('0000',0)]);blocked.add('0000')
    while queue:
        state,steps=queue.popleft()
        if state==target:return steps
        for index in range(4):
            for delta in (-1,1):
                digits=list(state);digits[index]=str((int(digits[index])+delta)%10);following=''.join(digits)
                if following not in blocked:blocked.add(following);queue.append((following,steps+1))
    return -1
'''
REACH = '''\
def minimum_reach_steps(target):
    target=abs(target);distance=steps=0
    while distance<target or (distance-target)%2:steps+=1;distance+=steps
    return steps
'''
MAPPING = '''\
def anagram_index_mapping(nums1, nums2):
    positions={value:index for index,value in enumerate(nums2)}
    return [positions[value] for value in nums1]
'''
PRIME_BITS = '''\
def prime_popcount_numbers(left, right):
    primes={2,3,5,7,11,13,17,19}
    return sum(value.bit_count() in primes for value in range(left,right+1))
'''
LABELS = '''\
def partition_label_lengths(s):
    last={char:index for index,char in enumerate(s)};answer=[];start=end=0
    for index,char in enumerate(s):
        end=max(end,last[char])
        if index==end:answer.append(end-start+1);start=index+1
    return answer
'''
TOEPLITZ = '''\
def is_toeplitz_matrix(matrix):
    return all(matrix[row][column]==matrix[row-1][column-1] for row in range(1,len(matrix)) for column in range(1,len(matrix[0])))
'''
JEWELS = '''\
def jewel_count(jewels, stones):
    kinds=set(jewels)
    return sum(stone in kinds for stone in stones)
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
718: entry('repeated_subarray_length',[('nums1','list[int]'),('nums2','list[int]')],'int',['dynamic-programming','arrays'],['1 <= len(nums1), len(nums2) <= 1,000.','Return the longest contiguous sequence appearing in both arrays.'],[([[1,2,3,2,1],[3,2,1,4,7]],'The shared contiguous sequence [3,2,1] has length three.'),([[0,0,0,0,0],[0,0,0,0,0]],'Every position matches, so the full length five is shared.')],[[a,b] for a,b in (([1],[1]),([1],[2]),([1,2],[2,1]),([1,2,3],[2,3]),([1,2,1],[1,2,1]),([0,1,0],[1,0,1]),([1,2,3],[4,5,6]),([1,1,2],[1,2,2]),([3,2,1],[0,3,2]),([1,2,3,4],[2,3,4,5]),([5,5,5],[5,5]),([1,2,1,2],[2,1,2,1]))],REPEATED,[REPEATED.replace('dp[index-1]+1','dp[index]+1'),"def repeated_subarray_length(a,b):\n    return len(set(a)&set(b))\n"],['Extends from the wrong previous DP cell.','Counts shared values instead of contiguous order.'],repeated_oracle,random_repeated,*lesson('A matching pair extends the common suffix ending immediately before both positions.','Keep one DP row of common-suffix lengths.','On equality set next[j]=previous[j-1]+1; otherwise leave zero.','Every repeated subarray ends at a pair of equal elements, and the diagonal recurrence measures exactly its length.'),'O(m*n)','O(n)',5),
720: entry('longest_buildable_word',[('words','list[str]')],'str',['strings','sorting'],['1 <= len(words) <= 1,000; words contain lowercase letters.','Every prefix of the returned word must occur; break equal-length ties lexicographically.'],[([['w','wo','wor','worl','world']],'Every prefix of world is present.'),([['a','banana','app','appl','ap','apply','apple']],'Apple and apply qualify; apple is lexicographically smaller.')],[[w] for w in (['a'],['b','ba'],['a','ab','abc'],['abc'],['a','b','ba','bca'],['x','xy','xyz','a'],['a','ap','app','apple'],['c','ca','cat','car'],['z','za','zb'],['a','at','ate','late'],['m','mo','moo','moon'],['b','ba','ban','bana','banan','banana'])],LONGEST,[LONGEST.replace("word[:-1] in built","word[1:] in built"),LONGEST.replace('if len(word)>len(answer)','if len(word)>=len(answer)')],['Checks suffixes instead of prefixes.','Overwrites equal-length answers and violates lexical tie-breaking.'],longest_oracle,random_longest,*lesson('A word becomes buildable exactly when its one-character-shorter prefix is buildable.','Process words by increasing length and lexical order.','Seed built with empty; add word when word[:-1] is built; update only for greater length.','Length ordering proves every required predecessor was already considered, and lexical order fixes ties.'),'O(n log n)','O(n)',4),
722: entry('strip_source_comments',[('source','list[str]')],'list[str]',['strings','simulation'],['Source contains valid // line comments and /* */ block comments; quoted strings are excluded.','Remove comments and omit empty output lines while joining code around multiline blocks.'],[([['/*Test program */','int main()','{ ','  // variable declaration ','int a, b, c;','/* This is a test','   multiline  ','   comment for ','   testing */','a = b + c;','}']],'The block and line comments vanish while the remaining program lines stay ordered.'),([['a/*comment','line','more_comment*/b']],'Code on opposite sides of a multiline block joins into ab.')],[[s] for s in (['a//x'],['//x','b'],['a/*x*/b'],['/*x*/a'],['a/*x','y*/b'],['a','b'],['/**/'],['a///*b'],['a/*//*/b'],['a/*x*/b//y'],['/*x','*/'],['x/','*y'])],COMMENTS,[COMMENTS.replace("elif text[index:index+2]=='//'","elif text[index:index+2]=='/'"),COMMENTS.replace("if not block and line","if line")],['Treats a single slash as a line comment.','Flushes partial lines while a block comment remains open.'],comments_oracle,random_comments,*lesson('Line comments end at the current line; block comments preserve parser state across lines.','Scan characters while tracking whether a block is open and buffer surviving code.','Outside a block, // stops the line and /* opens a block; */ closes it; flush only outside blocks.','The state machine consumes every comment delimiter once and joins code fragments exactly when a block crosses lines.'),'O(total characters)','O(total characters)',5),
728: entry('self_dividing_numbers',[('left','int'),('right','int')],'list[int]',['math','simulation'],['1 <= left <= right <= 10,000.','A self-dividing number contains no zero and is divisible by each of its digits.'],[([1,22],'The qualifying values are 1 through 9, then 11, 12, 15, and 22.'),([47,48],'Only 48 is divisible by both four and eight.')],[[a,b] for a,b in ((1,1),(10,12),(15,15),(20,25),(47,48),(99,101),(111,112),(120,130),(128,128),(300,330),(1000,1020),(9990,10000))],SELF_DIVIDING,[SELF_DIVIDING.replace('remaining%10 and ','True and '),SELF_DIVIDING.replace('value%(remaining%10)==0','value%(remaining%10)!=0')],['Fails to reject a zero digit.','Reverses the divisibility condition.'],self_dividing_oracle,random_self,*lesson('Every decimal digit supplies an independent divisibility requirement, and zero always rejects the number.','Inspect digits with repeated division by ten.','While digit is nonzero and divides original, discard it; accept only after all digits are consumed.','The loop invariant says all removed digits were nonzero divisors of the original value.'),'O((right-left)*digits)','O(1)',3),
734: entry('sentences_are_similar',[('sentence1','list[str]'),('sentence2','list[str]'),('similar_pairs','list[list[str]]')],'bool',['hash-maps','strings'],['Sentences are equally long to be similar; listed similarity is symmetric but not transitive.','Each aligned pair must be equal or directly listed as similar.'],[([['great','acting','skills'],['fine','drama','talent'],[['great','fine'],['acting','drama'],['skills','talent']]],'Every aligned pair is directly similar.'),([['great'],['good'],[['great','fine'],['fine','good']]],'Similarity is not transitive, so great and good are not directly similar.')],[[a,b,p] for a,b,p in ((['a'],['a'],[]),(['a'],['b'],[]),(['a'],['b'],[['a','b']]),(['b'],['a'],[['a','b']]),(['a','b'],['a'],[]),(['a','b'],['a','c'],[['b','c']]),(['a','b'],['c','d'],[['a','c']]),(['x','y'],['z','y'],[['x','z']]),(['a'],['c'],[['a','b'],['b','c']]),([],[],[]),(['same','x'],['same','x'],[]),(['one','two'],['uno','dos'],[['one','uno'],['two','dos']]))],SIMILAR,[SIMILAR.replace("or (b,a) in pairs",''),"def sentences_are_similar(a,b,pairs):\n    graph={tuple(x) for x in pairs}\n    return len(a)==len(b) and all(x==y or any(x in pair and y in pair for pair in graph) for x,y in zip(a,b))\n"],['Treats the directed input order as significant.','Incorrectly allows indirect co-membership-like relationships.'],similar_oracle,random_similar,*lesson('The rule is an aligned, direct, symmetric relation—not graph reachability.','Normalize each supplied pair into a lookup and test each word position.','Reject unequal lengths; accept position when words equal or either pair orientation exists.','Each sentence position is independent under the contract, so conjunction of direct checks is necessary and sufficient.'),'O(words+pairs)','O(pairs)',3),
735: entry('surviving_asteroids',[('asteroids','list[int]')],'list[int]',['stacks','arrays'],['Asteroids are nonzero integers; sign is direction and magnitude is size.','Only a positive asteroid left of a negative one can collide; equal sizes destroy both.'],[([[5,10,-5]],'Ten destroys the incoming size-five asteroid, leaving [5,10].'),([[8,-8]],'Equal opposing asteroids destroy each other.')],[[x] for x in ([1],[-1],[1,-2],[2,-1],[1,-1],[-2,-1,1,2],[3,4,-2],[3,4,-5],[10,2,-5],[-2,2,-2],[1,2,3,-3],[5,-3,-6,2])],ASTEROIDS,[ASTEROIDS.replace('stack[-1]<-asteroid','stack[-1]<=-asteroid'),ASTEROIDS.replace("if stack[-1]==-asteroid:stack.pop()",'stack.pop()')],['Pops equal asteroids in the loop and then incorrectly keeps the incoming one.','Destroys the stack top even when it is larger.'],asteroids_oracle,random_asteroids,*lesson('Only unresolved right-moving asteroids on a stack can meet a new left-mover.','Pop smaller opposing tops; then resolve equality, a larger top, or survival.','While top>0>current and top<abs(current), pop; handle remaining collision; otherwise append.','Each asteroid is pushed and popped at most once, and the stack always represents the stable processed prefix.'),'O(n)','O(n)',5),
738: entry('largest_monotone_number',[('n','int')],'int',['greedy','math'],['0 <= n <= 1,000,000,000.','Return the greatest integer no larger than n whose digits are nondecreasing left to right.'],[([10],'Decreasing the first digit and filling the suffix gives 9.'),([332],'The rightmost violation propagates left, producing 299.')],[[n] for n in (0,1,9,10,11,20,99,100,120,1234,1110,9876)],MONOTONE,[MONOTONE.replace("digits[mark:]=['9']","digits[mark:]=['0']"),MONOTONE.replace("range(len(digits)-1,0,-1)","range(1,len(digits))")],['Fills the repaired suffix with zero instead of the largest digit.','Scans forward and fails when decrementing creates an earlier violation.'],monotone_oracle,random_monotone,*lesson('Repairing a violation may create another violation to its left.','Scan right-to-left, decrement offending predecessors, then maximize the suffix with nines.','Record the earliest repaired suffix boundary and replace every later digit by nine.','The prefix is the largest feasible monotone prefix; all nines make its suffix maximal without exceeding n.'),'O(digits)','O(digits)',5),
740: entry('maximum_delete_earn',[('nums','list[int]')],'int',['dynamic-programming','hash-maps'],['1 <= len(nums) <= 20,000; values are positive.','Taking value x earns x and deletes every x-1 and x+1; maximize total points.'],[([[3,4,2]],'Taking two and four earns six.'),([[2,2,3,3,3,4]],'Taking all threes earns nine, better than taking twos and four.')],[[x] for x in ([1],[1,1],[1,2],[2,3,4],[2,2,3],[1,1,2,2,3,3],[1,3,5],[2,4,4,5],[5,5,6,7],[1,2,2,2,3],[8,9,9,10],[1,1,1,10,10])],EARN,[EARN.replace('gain=value*points[value]','gain=value'),EARN.replace("value==previous+1","value<=previous+1")],['Forgets that every duplicate of a chosen value contributes points.','Treats repeated or nonadjacent values as conflicting.'],earn_oracle,random_earn,*lesson('After grouping equal values, adjacent numeric values form the same recurrence as nonadjacent house robbery.','Sweep sorted values with best totals for taking or skipping the previous value.','If consecutive, take=current gain+old skip; otherwise add gain to old best.','Grouped choices conflict exactly when their values differ by one, so the two-state recurrence covers every valid subset.'),'O(n log n)','O(n)',5),
743: entry('network_delay',[('times','list[list[int]]'),('n','int'),('k','int')],'int',['graphs','heaps'],['1 <= k <= n <= 100; directed nonnegative weighted edges are unique.','Return the earliest time all nodes receive the signal, or -1 if any is unreachable.'],[([[[2,1,1],[2,3,1],[3,4,1]],4,2],'Shortest arrival times are one, zero, one, and two, so all nodes receive by time two.'),([[[1,2,1]],2,2],'Node one is unreachable from node two, so the answer is -1.')],[[e,n,k] for e,n,k in (([[1,2,1]],2,1),([[1,2,0]],2,1),([[1,2,1],[2,3,2]],3,1),([[1,2,5],[1,3,1],[3,2,1]],3,1),([[1,2,1]],3,1),([[2,1,1]],2,2),([[1,2,3],[2,1,3]],2,1),([[1,2,1],[2,3,1],[1,3,5]],3,1),([[3,1,2],[3,2,4]],3,3),([[1,2,2],[2,4,2],[1,3,1],[3,4,10]],4,1),([[2,3,0],[3,1,0]],3,2),([[1,2,100],[2,3,100]],3,1))],DELAY,[DELAY.replace('elapsed+weight','weight'),DELAY.replace("return max(distance.values()) if len(distance)==n else -1","return sum(distance.values()) if len(distance)==n else -1")],['Drops accumulated path cost when pushing an edge.','Returns the sum of arrival times rather than the final arrival time.'],delay_oracle,random_delay,*lesson('The next unsettled node with smallest known arrival time can never be improved by a nonnegative edge.','Run Dijkstra from the starting node and settle each node once.','Pop (time,node); skip settled nodes; push time+weight for outgoing edges; take maximum settled time.','Dijkstra proves settled distances are shortest, and their maximum is exactly when the last reachable node receives the signal.'),'O((n+edges) log n)','O(n+edges)',6),
744: entry('next_greater_letter',[('letters','list[str]'),('target','str')],'str',['binary-search','arrays'],['Letters are sorted and contain at least two distinct lowercase characters.','Return the smallest letter strictly greater than target, wrapping to the first letter.'],[([['c','f','j'],'a'],'c is the first letter greater than a.'),([['c','f','j'],'j'],'No letter is greater than j, so the result wraps to c.')],[[a,t] for a,t in ((['a','b'],'a'),(['a','b'],'b'),(['c','f','j'],'c'),(['c','f','j'],'d'),(['c','f','j'],'f'),(['c','f','j'],'g'),(['a','a','b'],'a'),(['a','z'],'m'),(['b','d','f'],'a'),(['b','d','f'],'e'),(['x','y','z'],'w'),(['x','y','z'],'z'))],LETTER,[LETTER.replace('<=target','<target'),LETTER.replace('left%len(letters)','min(left,len(letters)-1)')],['Finds greater-or-equal rather than strictly greater.','Fails to wrap when target reaches the end.'],letter_oracle,random_letter,*lesson('This is upper-bound search with circular fallback.','Binary-search the first index whose letter is greater than target.','Move left past values <= target; return letters[left modulo length].','The search invariant partitions all rejected values from all strict candidates, while modulo implements the required wrap.'),'O(log n)','O(1)',3),
747: entry('dominant_index',[('nums','list[int]')],'int',['arrays'],['1 <= len(nums) <= 50; values are nonnegative and the maximum is unique.','Return the maximum value’s index if it is at least twice every other value, otherwise -1.'],[([[3,6,1,0]],'Six is at least twice each other value, so its index is one.'),([[1,2,3,4]],'Four is not at least twice three, so the answer is -1.')],[[x] for x in ([1],[0],[1,2],[2,1],[0,0,1],[10,5],[9,5],[1,0,0],[2,2,5],[3,1,7],[100,1,50],[4,2,1,0])],DOMINANT,[DOMINANT.replace('2*second','second'),DOMINANT.replace('>=2*second','>2*second')],['Checks only that the maximum is at least the second maximum.','Rejects the valid equality boundary.'],dominant_oracle,random_dominant,*lesson('Only the second-largest value can violate dominance of the maximum.','Find the maximum index and greatest remaining value.','Accept index when maximum >= 2*second; use zero when no second value exists.','If the inequality holds for the second maximum, it holds for every smaller value; otherwise that value is a counterexample.'),'O(n)','O(1)',3),
748: entry('shortest_completing_word',[('license_plate','str'),('words','list[str]')],'str',['hash-maps','strings'],['Ignore digits and spaces in the plate and compare letters case-insensitively.','Return the shortest word containing required letters with multiplicity; preserve input order on ties.'],[(['1s3 PSt',['step','steps','stripe','stepple']],'Steps is the first shortest word containing two s characters, p, and t.'),(['1s3 456',['looks','pest','stew','show']],'Pest is the shortest word covering s.')],[[p,w] for p,w in (('a',['a','ba']),('AA',['a','aa']),('1 b',['ab','b']),('C',['cat','ace']),('a1b2',['cab','ab']),('zz',['zoo','fizz']),('p p',['paper','pep']),('x',['ax','xb']),('Ab',['ba','abc']),('m3',['team','me']),('q',['queen','qa']),('r s',['star','rs']))],COMPLETING,[COMPLETING.replace("if not (need-Counter(word))","if all(char in word for char in need)"),COMPLETING.replace('sorted(words,key=len)','sorted(words,key=lambda word:(len(word),word))')],['Ignores repeated required letters.','Breaks equal-length ties alphabetically instead of by input order.'],completing_oracle,random_completing,*lesson('The license plate is a case-insensitive multiset of letters.','Count required letters, then scan words from shortest to longest using stable ordering.','Choose first word whose Counter subtracts every required count to zero.','Stable length sorting preserves original order on ties, and multiset containment enforces duplicate letters exactly.'),'O(total word characters)','O(alphabet)',3),
750: entry('corner_rectangle_count',[('grid','list[list[int]]')],'int',['matrices','hash-maps'],['Grid contains zeros and ones with at most 200 rows and columns.','Count axis-aligned rectangles whose four corner cells are one.'],[([[[1,0,0,1,0],[0,0,1,0,1],[0,0,0,1,0],[1,0,1,0,1]]],'Only rows two and four share two one-columns, producing one rectangle.'),([[[1,1,1],[1,1,1],[1,1,1]]],'Three row pairs and three column pairs produce nine rectangles.')],[[g] for g in ([[0]],[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,0],[0,1]],[[1,1,1],[1,0,1]],[[1,0,1],[1,0,1],[1,0,1]],[[1,1,0],[1,1,0],[0,1,1]],[[1,1,1,1],[1,1,1,1]],[[0,0],[0,0]],[[1,0,1,0],[1,1,1,0],[1,0,1,1]])],RECTANGLES,[RECTANGLES.replace('answer+=pairs[pair]','answer+=1'),RECTANGLES.replace('pairs[pair]+=1','pairs[pair]=1')],['Adds one for every repeated column pair instead of the number of prior matching rows.','Forgets how many earlier rows shared the pair.'],rectangles_oracle,random_rectangles,*lesson('Each rectangle is completed when a row repeats a pair of one-columns seen in an earlier row.','Count how often every column pair has appeared.','For each row’s one-column pairs, add prior count then increment it.','Every rectangle has one unique bottom row and column pair, so it is counted exactly when that bottom pair is processed.'),'O(rows*columns²)','O(columns²)',5),
752: entry('minimum_lock_turns',[('deadends','list[str]'),('target','str')],'int',['breadth-first-search','graphs'],['The lock starts at 0000; each move rotates one of four digits one step with wraparound.','Deadend states cannot be entered; return minimum moves or -1.'],[([['0201','0101','0102','1212','2002'],'0202'],'A shortest valid route reaches 0202 in six turns.'),([['8888'],'0009'],'Turning the final wheel backward once reaches 0009.')],[[d,t] for d,t in (([],'0000'),([],'0001'),([],'0009'),(['0000'],'8888'),(['0001'],'0002'),(['9999'],'9998'),(['1000','9000','0100','0900','0010','0090','0001','0009'],'8888'),(['1111'],'1111'),(['5555'],'5556'),(['0100'],'0200'),(['9000'],'8000'),(['0001','0010'],'0011'))],LOCK,[LOCK.replace("%10","%9"),LOCK.replace("blocked.add(following);queue.append","queue.append")],['Wraps wheel digits modulo nine instead of ten.','Does not mark discovered states and repeatedly revisits them.'],lock_oracle,random_lock,*lesson('Every lock code is a graph node and every legal one-wheel turn is a unit-cost edge.','Breadth-first search from 0000 while treating deadends and visited states as blocked.','Pop by levels, generate eight wrapped neighbors, and return the first target distance.','BFS visits unit-edge states in nondecreasing distance, so the first target visit is minimal.'),'O(10^4)','O(10^4)',5),
754: entry('minimum_reach_steps',[('target','int')],'int',['math','greedy'],['-1,000,000,000 <= target <= 1,000,000,000.','On move k choose +k or -k; return the fewest moves needed to reach target from zero.'],[([3],'Moves +1 and +2 reach three in two steps.'),([2],'Moves +1, +2, then -3 reach zero, so instead +1, -2, +3 reaches two in three steps.')],[[n] for n in (0,1,-1,2,-2,4,5,6,7,8,10,100)],REACH,[REACH.replace("or (distance-target)%2",''),REACH.replace('target=abs(target)','target=target')],['Stops once the triangular sum passes target without checking parity.','Does not use symmetry for negative targets.'],reach_oracle,random_reach,*lesson('Changing one +k to -k reduces a triangular sum by the even amount 2k.','Find the first triangular sum at least |target| with matching parity.','Increase step and cumulative distance until distance-target is nonnegative and even.','An even difference can be formed by flipping a subset of steps, while an odd difference cannot; the first feasible step count is minimal.'),'O(sqrt(|target|))','O(1)',5),
760: entry('anagram_index_mapping',[('nums1','list[int]'),('nums2','list[int]')],'list[int]',['hash-maps','arrays'],['The arrays contain the same distinct integers in possibly different orders.','For each nums1 value, return its index in nums2.'],[([[12,28,46,32,50],[50,12,32,46,28]],'The values occur at indices [1,4,3,2,0] in the second array.'),([[84,46],[84,46]],'Each value already occupies the same index.')],[[a,b] for a,b in (([1],[1]),([1,2],[2,1]),([1,2,3],[3,2,1]),([0,-1],[-1,0]),([5,9,2],[2,5,9]),([10,20,30],[20,30,10]),([-3,-2,-1],[-1,-3,-2]),([4,1,7,9],[9,7,4,1]),([100,0],[0,100]),([8,6,4,2],[2,4,6,8]),([11,22,33],[11,33,22]),([3,1,2],[1,2,3]))],MAPPING,[MAPPING.replace('enumerate(nums2)','enumerate(nums1)'),MAPPING.replace('positions[value]','positions.get(value,0)')],['Builds positions from the wrong array.','Silently substitutes index zero instead of requiring the actual location.'],mapping_oracle,random_mapping,*lesson('Distinct values make the reverse position lookup unambiguous.','Index the second array once, then translate the first array.','positions={value:index for nums2}; return positions[value] for nums1.','The dictionary records the unique required index and avoids repeated linear searches.'),'O(n)','O(n)',3),
762: entry('prime_popcount_numbers',[('left','int'),('right','int')],'int',['bit-manipulation','math'],['1 <= left <= right <= 1,000,000.','Count integers whose number of one bits is prime.'],[([6,10],'Six, seven, nine, and ten have prime popcounts, giving four.'),([10,15],'Ten, eleven, twelve, thirteen, and fourteen qualify, giving five.')],[[a,b] for a,b in ((1,1),(1,2),(2,3),(4,5),(6,6),(7,7),(8,9),(15,16),(31,32),(100,120),(255,260),(999900,1000000))],PRIME_BITS,[PRIME_BITS.replace('{2,3,5,7,11,13,17,19}','{1,2,3,5,7,11,13,17,19}'),PRIME_BITS.replace('value.bit_count()','value')],['Incorrectly treats one as prime.','Tests whether the number itself is prime instead of its popcount.'],prime_bits_oracle,random_prime_bits,*lesson('Within the input bound, popcount is at most twenty.','Precompute the small prime popcounts and count membership.','For each value, compute bit_count and add one when it belongs to the prime set.','Popcount exactly measures one bits, and explicit prime membership avoids repeated primality work.'),'O(right-left)','O(1)',3),
763: entry('partition_label_lengths',[('s','str')],'list[int]',['greedy','hash-maps'],['1 <= len(s) <= 500; s contains lowercase letters.','Partition into as many parts as possible so each letter appears in at most one part; return lengths.'],[(['ababcbacadefegdehijhklij'],'The maximal partitions have lengths nine, seven, and eight.'),(['eccbbbbdec'],'Every letter is connected to the final occurrence of e, so one part of length ten is required.')],[[s] for s in ('a','ab','aa','aba','abcabc','abac','caedbdedda','abcad','aabbcc','abccaddbeffe','qwerty','zzxyyx')],LABELS,[LABELS.replace('last[char]','index'),LABELS.replace('end-start+1','end+1')],['Uses current indices rather than each letter’s final occurrence.','Returns end positions instead of partition lengths.'],labels_oracle,random_labels,*lesson('A partition containing a character must extend through that character’s final occurrence.','Track the farthest required end while scanning; cut exactly when the scan reaches it.','Precompute last positions, update end=max(end,last[c]), and append length when index==end.','Cutting earlier would split a character; cutting at the first feasible boundary maximizes the number of parts.'),'O(n)','O(alphabet)',4),
766: entry('is_toeplitz_matrix',[('matrix','list[list[int]]')],'bool',['matrices'],['Matrix is nonempty and rectangular.','Every top-left to bottom-right diagonal must contain one repeated value.'],[([[[1,2,3,4],[5,1,2,3],[9,5,1,2]]],'Each cell matches the one diagonally above-left.'),([[[1,2],[2,2]]],'The bottom-right two differs from the top-left one.')],[[m] for m in ([[1]],[[1,2]],[[1],[2]],[[1,2],[3,1]],[[1,2],[2,1]],[[1,2,3],[4,1,2]],[[1,2,3],[4,1,9]],[[0,0],[0,0]],[[1,0,1],[2,1,0],[3,2,1]],[[1,2],[1,1],[2,1]],[[5,6,7],[8,5,6]],[[1,2,3],[4,1,2],[5,4,1]])],TOEPLITZ,[TOEPLITZ.replace('matrix[row-1][column-1]','matrix[row-1][column]'),TOEPLITZ.replace('range(1,len(matrix[0]))','range(1,len(matrix[0])-1)')],['Compares vertical neighbors rather than diagonal neighbors.','Skips the final column and misses violations there.'],toeplitz_oracle,random_toeplitz,*lesson('Every non-first-row, non-first-column cell has exactly one diagonal predecessor.','Compare each such cell with its upper-left neighbor.','Return all(matrix[r][c]==matrix[r-1][c-1]).','Local equality chains transitively force every entire diagonal to share one value.'),'O(rows*columns)','O(1)',3),
771: entry('jewel_count',[('jewels','str'),('stones','str')],'int',['hash-maps','strings'],['Jewel characters are distinct and matching is case-sensitive.','Count how many stone characters belong to the jewel set.'],[(['aA','aAAbbbb'],'The three a or A stones are jewels.'),(['z','ZZ'],'Uppercase Z does not match lowercase z.')],[[j,s] for j,s in (('a','a'),('a','b'),('a','aaa'),('ab','baba'),('A','aA'),('abc','xyz'),('xY','Yxx'),('0','001'),('az','zaaz'),('ABC','ABCD'),('m',''),('qwerty','typewriter'))],JEWELS,[JEWELS.replace('set(jewels)','set(jewels.lower())').replace('stone in kinds','stone.lower() in kinds'),JEWELS.replace('sum(stone in kinds for stone in stones)','len(set(stones)&kinds)')],['Makes matching case-insensitive.','Counts distinct jewel types instead of every jewel stone.'],jewels_oracle,random_jewels,*lesson('Membership is repeated many times against a fixed set of jewel characters.','Build a set of jewel kinds and count matching stones.','kinds=set(jewels); sum(stone in kinds for stone in stones).','Set membership preserves case and counts each stone occurrence independently in linear expected time.'),'O(jewels+stones)','O(jewels)',3),
}


# Keep the workbook's exact source samples while presenting reviewed explanations.
BATCH[722]['examples'][0] = ([['/*Test program */', 'int main()', '{ ', ' // variable declaration ',
                                'int a, b, c;', '/* This is a test', ' multiline ', ' comment for ',
                                ' testing */', 'a = b + c;', '}']],
                              'Both comment forms disappear while surviving spaces and program lines remain in order.')
BATCH[734]['examples'][0] = ([['great', 'acting', 'skills'], ['fine', 'drama', 'talent'],
                              [['great', 'fine'], ['drama', 'acting'], ['skills', 'talent']]],
                             'Every aligned pair is equal or directly similar in either listed orientation.')

# These deliberately plausible mistakes must produce ordinary wrong answers.
BATCH[728]['wrong'][0] = '''\
def self_dividing_numbers(left, right):
    return [value for value in range(left,right+1)
            if all(value%int(char)==0 for char in str(value) if char!='0')]
'''
BATCH[734]['wrong'][1] = '''\
def sentences_are_similar(sentence1, sentence2, similar_pairs):
    mentioned={word for pair in similar_pairs for word in pair}
    return len(sentence1)==len(sentence2) and all(a==b or (a in mentioned and b in mentioned) for a,b in zip(sentence1,sentence2))
'''
BATCH[740]['wrong'][1] = EARN.replace('value==previous+1', 'value<=previous+2')
BATCH[752]['wrong'][1] = LOCK.replace("blocked=set(deadends)", "blocked=set(deadends);blocked.add(target)")
BATCH[752]['wrong_reasons'][1] = 'Incorrectly treats the target itself as a forbidden state.'
BATCH[760]['wrong'][1] = '''\
def anagram_index_mapping(nums1, nums2):
    return [nums2.index(value) for value in sorted(nums1)]
'''
BATCH[760]['wrong_reasons'][1] = 'Sorts the first array and loses the required output order.'
