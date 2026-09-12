"""Decimal arithmetic, reverse grid search, packing, edit distance and bit prefixes."""
from collections import Counter, deque
from functools import lru_cache
from heapq import heappop, heappush
from .import_batch_003 import entry


def add_oracle(args):
    # Small generated inputs only; the reference must not use whole-input conversion.
    return str(int(args[0])+int(args[1]))


def partition_oracle(args):
    nums = args[0]
    total = sum(nums)
    return total%2==0 and any(sum(value for i,value in enumerate(nums) if mask>>i&1)*2==total
                              for mask in range(1<<len(nums)))


def oceans_oracle(args):
    grid = args[0]
    rows,cols = len(grid),len(grid[0])
    result = []
    for start in ((r,c) for r in range(rows) for c in range(cols)):
        queue,seen = deque([start]),{start}
        pacific = atlantic = False
        while queue:
            r,c = queue.popleft()
            pacific |= r==0 or c==0
            atlantic |= r==rows-1 or c==cols-1
            for a,b in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0<=a<rows and 0<=b<cols and (a,b) not in seen and grid[a][b]<=grid[r][c]:
                    seen.add((a,b))
                    queue.append((a,b))
        if pacific and atlantic:
            result.append(list(start))
    return result


def screen_oracle(args):
    sentence,rows,cols = args
    words = 0
    for _ in range(rows):
        used = 0
        while used+len(sentence[words%len(sentence)])<=cols:
            used += len(sentence[words%len(sentence)])+1
            words += 1
    return words//len(sentence)


def ship_components(board):
    unseen = {(r,c) for r,row in enumerate(board) for c,value in enumerate(row) if value=='X'}
    components = []
    while unseen:
        root = unseen.pop()
        stack,component = [root],{root}
        while stack:
            r,c = stack.pop()
            for neighbor in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components


def ships_oracle(args):
    return len(ship_components(args[0]))


def char_type(char):
    return 1 if 'a'<=char<='z' else 2 if 'A'<=char<='Z' else 4 if '0'<=char<='9' else 0


@lru_cache(maxsize=256)
def password_distance(password):
    """Exact edit-distance search to a finite automaton of valid passwords.

    New characters need only three representatives per required class. Choose
    one different from both neighboring output characters; this cannot create
    a triple, even between two retained runs. Original characters also have
    zero-cost keep transitions. This covers arbitrary ASCII input letters.
    Replacing/inserting punctuation cannot improve length, type, or repetition
    constraints over a different letter/digit, so it need not be generated.
    """
    n = len(password)
    start = (0,0,0,'',0)  # consumed input, output length, type mask, last, repeat
    def bound(state):
        i,length,mask,_,_ = state
        remaining = n-i
        # Deliberately omit missing types: remaining input may supply them free.
        return max(0,6-length-remaining,length+remaining-20)
    best = {start:0}
    queue = [(bound(start),0,0,start)]
    while queue:
        _,cost,_,state = heappop(queue)
        if best.get(state)!=cost:
            continue
        i,length,mask,last,repeat = state
        if i==n and 6<=length<=20 and mask==7:
            return cost
        following = []
        if i<n:
            following.append(((i+1,length,mask,last,repeat),cost+1))
        if length<20:
            choices = [(char,1,False) for char in 'abcABC012']
            if i<n:
                choices += [(password[i],0,True)] + [(char,1,True) for char in 'abcABC012']
            for char,extra,consume in choices:
                run = repeat+1 if char==last else 1
                if run<=2:
                    following.append(((i+int(consume),length+1,mask|char_type(char),char,run),cost+extra))
        for nxt,value in following:
            if value<best.get(nxt,float('inf')):
                best[nxt] = value
                heappush(queue,(value+bound(nxt),value,-nxt[0],nxt))
    raise AssertionError('Every input has a finite repair')


def password_oracle(args):
    return password_distance(args[0])


def xor_oracle(args):
    nums = args[0]
    return max(a^b for a in nums for b in nums)


WORDS = ('zero','one','two','three','four','five','six','seven','eight','nine')


def digits_oracle(args):
    counts = Counter(args[0])
    letters = sorted(counts)
    bags = [Counter(word) for word in WORDS]
    @lru_cache(None)
    def search(index,remaining):
        if index==10:
            return '' if not any(remaining) else None
        vector = tuple(bags[index][letter] for letter in letters)
        if any(letter not in counts for letter in bags[index]):
            return search(index+1,remaining)
        limit = min(value//need for value,need in zip(remaining,vector) if need)
        for amount in range(limit+1):
            rest = tuple(value-amount*need for value,need in zip(remaining,vector))
            suffix = search(index+1,rest)
            if suffix is not None:
                return str(index)*amount+suffix
        return None
    answer = search(0,tuple(counts[letter] for letter in letters))
    if answer is None:
        raise ValueError('Invalid digit-letter fixture')
    return answer


def replacement_oracle(args):
    text,k = args
    best = 0
    for start in range(len(text)):
        counts = Counter()
        for end in range(start,len(text)):
            counts[text[end]] += 1
            if end-start+1-max(counts.values())<=k:
                best = max(best,end-start+1)
    return best


def random_add(rng):
    return [str(rng.randrange(10**rng.randint(1,80))) for _ in range(2)]


def random_partition(rng):
    return [[rng.randint(1,20) for _ in range(rng.randint(1,12))]]


def random_oceans(rng):
    rows,cols = rng.randint(1,6),rng.randint(1,6)
    return [[[rng.randint(0,9) for _ in range(cols)] for _ in range(rows)]]


def random_screen(rng):
    return [[''.join(rng.choice('ab') for _ in range(rng.randint(1,6)))
             for _ in range(rng.randint(1,6))],rng.randint(1,8),rng.randint(1,20)]


def random_ships(rng):
    rows,cols = rng.randint(1,8),rng.randint(1,8)
    board = [['.']*cols for _ in range(rows)]
    for _ in range(rows*cols):
        r,c = rng.randrange(rows),rng.randrange(cols)
        dr,dc = rng.choice([(0,1),(1,0)])
        cells = [(r+i*dr,c+i*dc) for i in range(rng.randint(1,5))]
        if not all(a<rows and b<cols and board[a][b]=='.' for a,b in cells):
            continue
        if any(0<=x<rows and 0<=y<cols and board[x][y]=='X'
               for a,b in cells for x,y in ((a-1,b),(a+1,b),(a,b-1),(a,b+1))):
            continue
        for a,b in cells:
            board[a][b]='X'
    return [board]


def random_password(rng):
    return [''.join(rng.choice('aA0!') for _ in range(rng.randint(1,8)))]


def random_xor(rng):
    return [[rng.randrange(2**rng.randint(1,31)) for _ in range(rng.randint(1,30))]]


def random_digits(rng):
    text = ''.join(WORDS[rng.randrange(10)] for _ in range(rng.randint(1,7)))
    return [''.join(rng.sample(text,len(text)))]


def random_replacement(rng):
    text = ''.join(rng.choice('ABCD') for _ in range(rng.randint(1,20)))
    return [text,rng.randint(0,len(text))]


ADD = '''\
def add_decimal_strings(num1, num2):
    i,j,carry = len(num1)-1,len(num2)-1,0
    digits = []
    while i>=0 or j>=0 or carry:
        a = ord(num1[i])-ord('0') if i>=0 else 0
        b = ord(num2[j])-ord('0') if j>=0 else 0
        total = a+b+carry
        digits.append(chr(ord('0')+total%10))
        carry = total//10
        i,j = i-1,j-1
    return ''.join(reversed(digits))
'''

PARTITION = '''\
def equal_subset_partition(nums):
    total = sum(nums)
    if total%2:
        return False
    target = total//2
    reachable = [False]*(target+1)
    reachable[0] = True
    for value in nums:
        for subtotal in range(target,value-1,-1):
            reachable[subtotal] |= reachable[subtotal-value]
    return reachable[target]
'''

OCEANS = '''\
def pacific_atlantic_cells(heights):
    rows,cols = len(heights),len(heights[0])
    def climb(starts):
        seen = set(starts)
        stack = list(seen)
        while stack:
            row,col = stack.pop()
            for r,c in ((row-1,col),(row+1,col),(row,col-1),(row,col+1)):
                if 0<=r<rows and 0<=c<cols and (r,c) not in seen and heights[r][c]>=heights[row][col]:
                    seen.add((r,c))
                    stack.append((r,c))
        return seen
    pacific = climb([(0,c) for c in range(cols)]+[(r,0) for r in range(rows)])
    atlantic = climb([(rows-1,c) for c in range(cols)]+[(r,cols-1) for r in range(rows)])
    return [[r,c] for r in range(rows) for c in range(cols) if (r,c) in pacific and (r,c) in atlantic]
'''

SCREEN = '''\
def sentence_screen_count(sentence, rows, cols):
    count = len(sentence)
    cycle_width = sum(len(word)+1 for word in sentence)
    cycles,remaining = divmod(cols+1,cycle_width)
    transitions = []
    for start in range(count):
        used,extra = 0,0
        while used+len(sentence[(start+extra)%count])+1<=remaining:
            used += len(sentence[(start+extra)%count])+1
            extra += 1
        words = cycles*count+extra
        transitions.append(((start+words)%count,(start+words)//count))
    index,total = 0,0
    for _ in range(rows):
        index,completed = transitions[index]
        total += completed
    return total
'''

SHIPS = '''\
def count_battleships(board):
    total = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col]=='X' and (row==0 or board[row-1][col]!='X') and (col==0 or board[row][col-1]!='X'):
                total += 1
    return total
'''

PASSWORD = '''\
def strong_password_edits(password):
    missing = int(not any('a'<=c<='z' for c in password))
    missing += int(not any('A'<=c<='Z' for c in password))
    missing += int(not any('0'<=c<='9' for c in password))
    replacements = zero = one = 0
    start = 0
    while start<len(password):
        end = start+1
        while end<len(password) and password[end]==password[start]:
            end += 1
        length = end-start
        replacements += length//3
        if length>=3:
            zero += int(length%3==0)
            one += int(length%3==1)
        start = end
    if len(password)<6:
        return max(6-len(password),missing)
    if len(password)<=20:
        return max(replacements,missing)
    deletions = len(password)-20
    remaining = deletions
    used = min(remaining,zero)
    replacements -= used
    remaining -= used
    used = min(remaining,2*one)
    replacements -= used//2
    remaining -= used
    replacements = max(0,replacements-remaining//3)
    return deletions+max(replacements,missing)
'''

XOR = '''\
def maximum_pair_xor(nums):
    answer = 0
    for bit in range(30,-1,-1):
        prefixes = {value>>bit for value in nums}
        candidate = (answer<<1)|1
        answer <<= 1
        if any((prefix^candidate) in prefixes for prefix in prefixes):
            answer = candidate
    return answer
'''

DIGITS = '''\
def reconstruct_digits(s):
    from collections import Counter
    letters = Counter(s)
    counts = [0]*10
    counts[0] = letters['z']
    counts[2] = letters['w']
    counts[4] = letters['u']
    counts[6] = letters['x']
    counts[8] = letters['g']
    counts[3] = letters['h']-counts[8]
    counts[5] = letters['f']-counts[4]
    counts[7] = letters['s']-counts[6]
    counts[1] = letters['o']-counts[0]-counts[2]-counts[4]
    counts[9] = letters['i']-counts[5]-counts[6]-counts[8]
    return ''.join(str(digit)*counts[digit] for digit in range(10))
'''

REPLACEMENT = '''\
def longest_replaced_run(s, k):
    counts = [0]*26
    left = largest = best = 0
    for right,char in enumerate(s):
        index = ord(char)-ord('A')
        counts[index] += 1
        largest = max(largest,counts[index])
        if right-left+1-largest>k:
            counts[ord(s[left])-ord('A')] -= 1
            left += 1
        best = max(best,right-left+1)
    return best
'''


BATCH = {
415: entry('add_decimal_strings',[('num1','str'),('num2','str')],'str',
    ['strings','math'],
    ['1 <= each input length <= 10,000; decimal digits only.',
     'No leading zeros except the string "0". Return the exact decimal sum as a string.',
     'Do not convert a whole input to an integer or use a large-integer library; operate on digits.'],
    [(['11','123'],'Align the rightmost digits: 1+3=4, 1+2=3, and the remaining 1 gives 134.'),
     (['999','1'],'Carry passes through every 9, producing an extra leading digit: 1000.')],
    [[a,b] for a,b in [('0','0'),('0','7'),('7','0'),('1','2'),('9','9'),('95','17'),
      ('100','900'),('12345','5'),('5','12345'),('1010','9090'),('9999','9999'),('456','77')]],
    ADD,[ADD.replace('a+b+carry','a+b'),ADD.replace('i>=0 or j>=0 or carry','i>=0 and j>=0')],
    ['Ignores incoming carry from the lower digit.', 'Stops at the shorter input and loses remaining digits/final carry.'],
    add_oracle,random_add,
    ['Decimal addition needs only one digit from each input and a carry.',
     'Traverse right to left, treating exhausted inputs as zero.',
     'Append total%10 and retain total//10 while either input or carry remains; reverse the collected digits.',
     'Processing each position once gives linear time. The output may have one more digit than either input.'],
    'Use character codes to read a single digit. Add both digits and the previous carry, emit the '
    'ones place, and carry the tens place. Missing high digits act as zero. The final carry needs '
    'its own iteration. Reverse the collected characters once; repeated front insertion would be quadratic.',
    'O(max(m,n))','O(max(m,n))',difficulty=3,
    stress=[(['9'*10000,'1'],'1'+'0'*10000),(['5'*10000,'4'*10000],'9'*10000)]),
416: entry('equal_subset_partition',[('nums','list[int]')],'bool',
    ['arrays','dynamic-programming'],
    ['1 <= nums.length <= 200; 1 <= nums[i] <= 100.',
     'Assign every occurrence to one of two subsets with equal sums; input order is irrelevant.',
     'Each occurrence may be used only once. Return existence, not the subsets or their count.'],
    [([[1,5,11,5]],'[1,5,5] and [11] both sum to 11; the two copies of 5 are separate available items.'),
     ([[1,2,5]],'The total is even, but no subset sums to 4, so an even total alone is insufficient.')],
    [[v] for v in ([1],[2],[1,1],[1,2],[2,2],[1,2,3,5],[2,2,3,5],[1,1,3,5],
      [3,3,3,3],[1,2,3,4],[100,100],[1,1,1,1,1,1])],
    PARTITION,[PARTITION.replace('range(target,value-1,-1)','range(value,target+1)'),
               'def equal_subset_partition(nums):\n    return sum(nums)%2==0\n'],
    ['Updates sums upward, accidentally allowing reuse of the same occurrence.', 'Assumes every even total can be partitioned.'],
    partition_oracle,random_partition,
    ['If the total is odd, two equal integer sums are impossible.',
     'For an even total, ask whether a subset reaches half of it.',
     'Start reachable[0]=True. For each item update sums from target downward, using reachable[subtotal-value].',
     'Descending updates keep the current item from being reused. Time O(n*target), space O(target).'],
    'After processing a prefix, reachable[t] means some subset of that prefix sums to t. Updating '
    'from high sums down ensures the predecessor state still excludes the current item, preserving '
    'the 0/1 choice. If half the total is reachable, all unchosen items form the equal-sum complement.',
    'O(n * target)','O(target)',difficulty=5,
    stress=[([[100]*200],True),([[100]*199+[98]],False)]),
417: entry('pacific_atlantic_cells',[('heights','list[list[int]]')],'list[list[int]]',
    ['matrices','graphs','depth-first-search','recursion'],
    ['1 <= rows, columns <= 200; rectangular grid; 0 <= heights[r][c] <= 100,000.',
     'Water moves north/south/east/west to equal or lower heights. Diagonal movement is not allowed.',
     'Pacific touches top/left; Atlantic touches bottom/right. Return each zero-based [row,column] reaching both once, in any outer order.'],
    [([[[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]],
      'Seven cells reach both oceans. For example [2,2] flows up through [1,2] to the Pacific and right through [2,3] to the Atlantic.'),
     ([[[1,1],[1,1]]],'Equal-height movement is allowed, so all four cells can cross the plateau to both oceans.')],
    [[g] for g in ([[0]],[[100000]],[[1,2,3]],[[3],[2],[1]],[[1,2],[3,4]],
      [[4,3],[2,1]],[[1,2,1],[2,1,2],[1,2,1]],[[3,3,3],[3,0,3],[3,3,3]],
      [[0,0,0],[0,5,0],[0,0,0]],[[1,2,3],[2,3,4]],[[4,3],[3,2],[2,1]],
      [[1,9,1,1],[1,9,9,1],[1,1,9,1]])],
    OCEANS,[OCEANS.replace('heights[r][c]>=heights[row][col]','heights[r][c]>heights[row][col]'),
            OCEANS.replace('heights[r][c]>=heights[row][col]','heights[r][c]<=heights[row][col]')],
    ['Disallows equal-height connections when reversing the flow.', 'Walks downhill from the oceans instead of reversing the flow uphill.'],
    oceans_oracle,random_oceans,
    ['Searching downhill separately from every cell repeats much of the same work.',
     'Reverse the flow: start at each ocean and climb to equal or higher neighboring cells.',
     'Flood top/left borders, flood bottom/right borders, and return the intersection of visited cells.',
     'Each reverse search visits a cell at most once. Recursive DFS and an explicit DFS stack express the same reachability; a stack avoids depth overflow on large grids.'],
    'An edge u→v in water flow exists when v is no higher than u. Reversing it lets the ocean search '
    'climb to every cell that can drain into it. Seed all touching borders, track visits separately, '
    'and intersect the results. Equality is essential for plateaus. Use an explicit DFS stack for '
    '40,000-cell grids, and scan coordinates once to collect the answer without sorting.',
    'O(rows * columns)','O(rows * columns)',difficulty=6,
    stress=[([[[7]*200 for _ in range(200)]],[[r,c] for r in range(200) for c in range(200)]),
            ([[[r+c for c in range(200)] for r in range(200)]],[[r,c] for r in range(200) for c in range(200) if r==199 or c==199])]),
418: entry('sentence_screen_count',[('sentence','list[str]'),('rows','int'),('cols','int')],'int',
    ['strings','dynamic-programming'],
    ['1 <= sentence.length <= 100; each word has 1–10 lowercase English letters.',
     '1 <= rows, cols <= 20,000. Words keep their cyclic sentence order and cannot split across lines.',
     'Use one space between words on the same line; no leading or required trailing space. Count complete sentence repetitions only.'],
    [([['hello','world'],2,8],'The first row fits hello and the second fits world: one complete sentence.'),
     ([['a','bcd','e'],3,6],'Rows fit a bcd | e a | bcd e. Six words complete the three-word sentence twice.')],
    [[w,r,c] for w,r,c in [(['a'],1,1),(['a'],1,2),(['a'],2,3),(['ab'],3,1),
      (['ab'],2,2),(['a','b'],1,3),(['a','b'],1,2),(['a','bb'],3,3),
      (['i','had','apple','pie'],4,5),(['a','b','c'],4,1),(['abcdef','a'],4,5),(['ab','cd'],3,7)]],
    SCREEN,[SCREEN.replace('divmod(cols+1,cycle_width)','divmod(cols,cycle_width)'),
            SCREEN.replace('index,completed = transitions[index]','index,completed = transitions[0]')],
    ['Requires a trailing space after the last word, wasting an otherwise usable column.',
     'Restarts from the first word on every row instead of continuing sentence order.'],
    screen_oracle,random_screen,
    ['Only the next word index needs to carry across row boundaries.',
     'Precompute how many complete sentences and what next index one row produces from each starting word.',
     'Treat each word as length+1 and give the row cols+1 space; take whole cycles, then scan the remaining partial cycle.',
     'The extra virtual column cancels only the final trailing space. Whole-cycle arithmetic makes preprocessing O(n^2), then rows take O(rows).'],
    'Add a virtual trailing space to every placed word and one virtual column to the row. A whole '
    'cyclic sentence costs the same width from any starting index. Fit as many cycles as possible, '
    'then fewer than n extra words. Store the resulting index and number of wraps. Applying these '
    'transitions row by row handles continuation and words wider than a row without splitting words.',
    'O(n^2 + rows)','O(n)',difficulty=6,
    stress=[([['a'],20000,20000],200000000),([['abcdefghij']*100,20000,20000],363600),([['ab'],20000,1],0)]),
419: entry('count_battleships',[('board','list[list[str]]')],'int',
    ['matrices','arrays'],
    ['1 <= rows, columns <= 200; rectangular board with only "X" and ".".',
     'Each ship is a straight horizontal or vertical run. Different ships never touch by an edge; diagonal contact is allowed.',
     'Follow-up target: one pass, O(1) extra space, without modifying the board.'],
    [([[['X','.','.','X'],['.','.','.','X'],['.','.','.','X']]],
      'One single-cell ship starts at [0,0]; one vertical ship occupies the last column. Count ships, not four X cells.'),
     ([[['X','.'],['.','X']]],'These two single-cell ships touch only diagonally, so they remain separate ships.')],
    [[g] for g in ([[ '.']], [['X']], [list('XXX')], [['X'],['X'],['X']], [list('X.X')],
      [list('...'),list('...')],[list('XX.'),list('...'),list('.XX')],
      [list('X.X'),list('X.X')],[list('XX'),list('..')],
      [list('X..'),list('...'),list('..X')],[list('.X.'),list('.X.')],[list('....'),list('XXXX')])],
    SHIPS,['def count_battleships(board):\n    return sum(row.count("X") for row in board)\n',
           SHIPS.replace("(row==0 or board[row-1][col]!='X')",'True')],
    ['Counts occupied cells instead of ships.', 'Counts each segment of a vertical ship as a separate horizontal start.'],
    ships_oracle,random_ships,
    ['A valid ship has exactly one topmost/leftmost starting cell.',
     'Count X only when neither its upper neighbor nor its left neighbor is X.',
     'Scan every cell; if occupied and not continued from above or left, increment the count.',
     'The straight, separated-ship guarantee makes local starts sufficient. No flood fill, visited set, or board edits are needed.'],
    'Every horizontal ship has one leftmost cell, and every vertical ship one topmost cell. All '
    'other occupied cells have a preceding neighbor on that same ship. Separation prevents another '
    'ship from invalidating its start. Diagonal neighbors have no role. The reference meets the '
    'optional constant-space, nonmutating one-pass follow-up.',
    'O(rows * columns)','O(1)',difficulty=5,
    stress=[([[[ 'X' if (r+c)%2==0 else '.' for c in range(200)] for r in range(200)]],20000),
            ([[['X' if r%2==0 else '.']*200 for r in range(200)]],100)]),
420: entry('strong_password_edits',[('password','str')],'int',
    ['strings','greedy'],
    ['1 <= password.length <= 50; ASCII letters, digits, dot, or exclamation mark.',
     'Strong means length 6–20 inclusive, at least one lowercase/uppercase/digit, and no three equal consecutive characters.',
     'One step inserts, deletes, or replaces one character. Return the minimum edits under these puzzle rules, not a security-strength rating.'],
    [(['a'],'Five insertions reach length 6; choose inserted characters to supply an uppercase letter and a digit while avoiding triples.'),
     (['aaaAAA000bbbBBB111ccc'],'Length 21 forces one deletion. Deleting from a length-three run fixes that run; six replacements fix the remaining runs: 7 edits.')],
    [[s] for s in ('aA1','1337C0d3','aaa111','aaaaaa','aA0bB1','ABABAB','!!!!!','a'*20,
                   'a'*21,'a'*22,'a'*23,'aaaB1aaaB1aaaB1aaaB1aaa')],
    PASSWORD,[PASSWORD.replace('return max(replacements,missing)','return replacements+missing'),
              PASSWORD.replace('used = min(remaining,zero)','used = 0')],
    ['Adds missing-type fixes and repeated-run replacements even when one replacement fixes both.',
     'Ignores one-deletion savings on runs whose lengths are multiples of three.'],
    password_oracle,random_password,
    ['Length, missing character classes, and runs interact; an edit can solve more than one issue.',
     'A repeated run needs length//3 replacements unless insertions or mandatory deletions reduce it.',
     'Short: max(6-n,missing). Medium: max(run replacements,missing). Long: delete n-20, prioritizing run lengths mod 3 equal to 0, then 1, then groups of 3.',
     'One deletion saves a replacement for 3k runs; two for 3k+1; three thereafter. Combine remaining replacement work with missing classes using max, not addition.'],
    'For short inputs, required insertions can break runs and supply missing classes. At lengths '
    '6–20, each disjoint triple in a run needs one replacement, which can also add a missing class. '
    'For longer inputs, deletions are mandatory. Spend them where they save replacements most cheaply: '
    'first one on each 3k run, then two on each 3k+1 run, then triples. Add mandatory deletions to '
    'the maximum of remaining replacements and missing classes. Three run counters suffice for O(1) space. '
    'These are the exercise rules only; the function does not assess real-world password security.',
    'O(n)','O(1)',difficulty=8,
    stress=[(['a'*50],36),(['aA0'*16+'aA'],30),(['.'*50],36)]),
421: entry('maximum_pair_xor',[('nums','list[int]')],'int',
    ['arrays','bit-manipulation','hash-maps'],
    ['1 <= nums.length <= 200,000; 0 <= nums[i] <= 2^31-1.',
     'Choose indices i <= j, so a single item may pair with itself. Return the maximum XOR value, not indices.',
     'Repeated values are allowed. XOR is bitwise exclusive-or, not addition or exponentiation.'],
    [([[3,10,5,25,2,8]],'5 XOR 25 = 28 is largest; pairing the largest numbers by numeric size need not maximize XOR.'),
     ([[7]],'The only allowed pair uses the same index twice, and 7 XOR 7 is 0.')],
    [[v] for v in ([0],[1,1],[0,1],[1,2],[2,3,4],[8,9,10],[0,2**31-1],
                   [2**30,2**30-1],[5,5,5],[1,2,4,8,16],[14,70,53,83,49,91,36,80,92,51,66,70],[4,6,7])],
    XOR,[XOR.replace('range(30,-1,-1)','range(29,-1,-1)'),
         'def maximum_pair_xor(nums):\n    values=sorted(nums)\n    return values[-1]^values[-2] if len(values)>1 else 0\n'],
    ['Omits bit 30, losing the highest allowed input bit.', 'Assumes the two numerically largest values have the largest XOR.'],
    xor_oracle,random_xor,
    ['A higher XOR bit outweighs every lower bit together.',
     'Build the answer from high bits down, asking whether a candidate prefix can be formed by two input prefixes.',
     'For each bit collect shifted prefixes; try (answer<<1)|1 and check whether prefix XOR candidate is also present.',
     'The prefix-set identity a XOR b = candidate lets each feasibility test run in O(n); 31 bit positions give O(31n).'],
    'Suppose the optimal higher bits are fixed. Prefer setting the next bit if some pair of input '
    'prefixes achieves that extended candidate. A hash set checks the complementary prefix in '
    'constant expected time. Otherwise leave that bit zero. Lower bits cannot compensate for losing '
    'a feasible high bit. Use all 31 nonnegative signed-integer bits; a singleton correctly yields zero.',
    'O(31n) expected','O(n)',difficulty=6,
    stress=[([[((i*104729)&(2**31-1)) for i in range(199998)]+[0,2**31-1]],2**31-1)]),
423: entry('reconstruct_digits',[('s','str')],'str',
    ['strings','hash-maps'],
    ['1 <= s.length <= 100,000; s is guaranteed to be a shuffled concatenation of lowercase English digit names zero through nine.',
     'Recover every digit occurrence and return them in ascending order, preserving repeated digits.',
     'Letters may be arbitrarily interleaved; whole digit words need not remain contiguous.'],
    [(['owoztneoer'],'The letters are exactly those of zero + one + two, giving sorted digits 012.'),
     (['fviefuro'],'The letters reconstruct four and five; their sorted digit string is 45.')],
    [[s] for s in (*WORDS,'zerozeroone','eightthreefivefournine')],
    DIGITS,[DIGITS.replace("letters['h']-counts[8]","letters['h']"),
            DIGITS.replace('str(digit)*counts[digit]','str(digit) if counts[digit] else ""')],
    ['Counts the h in eight as another three instead of subtracting known digits.',
     'Emits each present digit only once, losing multiplicities.'],
    digits_oracle,random_digits,
    ['Some letters appear in only one digit name.',
     'Use z,w,u,x,g to identify 0,2,4,6,8, then subtract their contributions to shared letters.',
     'Find 3 from h-8, 5 from f-4, 7 from s-6, 1 from o-0-2-4, and 9 from i-5-6-8.',
     'Each deduction has its prerequisites known. Count letters once and emit digit counts in ascending order.'],
    'The unique-letter digits provide a triangular system of counts. Once known contributions '
    'are removed, h identifies three, f five, s seven, o one, and i nine. The validity guarantee '
    'ensures nonnegative integer counts. Work on letter frequencies, not contiguous word matching. '
    'The independent validator instead searches possible digit-count vectors and reconciles every letter.',
    'O(n)','O(1), excluding output',difficulty=5,
    stress=[(['zero'*25000],'0'*25000),([''.join(WORDS)*2000],''.join(str(i)*2000 for i in range(10)))]),
424: entry('longest_replaced_run',[('s','str'),('k','int')],'int',
    ['strings','sliding-window','hash-maps'],
    ['1 <= s.length <= 100,000; uppercase English letters only; 0 <= k <= s.length.',
     'Change at most k characters to any uppercase letter. Return the longest contiguous substring that can become one repeated letter.',
     'Choose the target letter freely; you do not need to return or mutate the string.'],
    [(['ABAB',2],'Changing both As to B (or both Bs to A) makes all four positions equal.'),
     (['AABABBA',1],'Changing the A at index 3 to B makes AABBBBA, containing a length-four BBBB substring.')],
    [[s,k] for s,k in [('A',0),('A',1),('AAAA',0),('ABCD',0),('ABCD',3),('BBBB',0),
      ('AABBA',0),('AABBA',1),('BAAAB',1),('ABABAB',2),('ABCABC',3),('ZZYZZ',1)]],
    REPLACEMENT,[REPLACEMENT.replace('largest = max(largest,counts[index])','largest = counts[0]'),
                 REPLACEMENT.replace('right-left+1-largest>k','right-left+1-largest>=k')],
    ['Always targets A, ignoring a more frequent different letter.', 'Shrinks even when exactly k replacements are sufficient.'],
    replacement_oracle,random_replacement,
    ['For a fixed window, keep its most frequent letter and replace the rest.',
     'Grow a sliding window while its size minus the best letter frequency fits the budget.',
     'Increment the newest letter, update historical largest frequency, and shift left once when window size minus largest exceeds k.',
     'A historical maximum can leave an invalid current window, but cannot create a larger false record: growth needs a genuinely increased frequency. This version returns only the best length.'],
    'A window of length L needs L-max_frequency replacements. Track 26 counts and a nondecreasing '
    'historical maximum. Window length never decreases: it either grows or shifts at constant size. '
    'A stale frequency may preserve an already achieved length, but growing past that record requires '
    'a new real frequency large enough to support it. Thus the maximum length is correct even though '
    'this optimized variant must not be used to return an arbitrary current window as a witness.',
    'O(n)','O(1)',difficulty=6,
    stress=[(['A'*50000+'B'*50000,25000],75000),(['AB'*50000,0],1),(['Z'*100000,100000],100000)]),
}

BATCH[417]['comparator'] = 'unordered'
BATCH[420]['prerequisites'] = ['strings','greedy']
