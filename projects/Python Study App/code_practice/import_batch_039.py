"""Word-square search, tree prefixes, linked digits and in-place character prefixes."""
from itertools import combinations, groupby, product
from .import_batch_002 import positions, flatten
from .import_batch_003 import entry


def square_oracle(args):
    words = args[0]
    size = max(len(words),max(map(len,words)))
    rows = words+['']*(size-len(words))
    columns = [''.join(word[index] for word in words if index<len(word)) for index in range(size)]
    return rows==columns


def squares_oracle(args):
    words = args[0]
    size = len(words[0])
    return [list(rows) for rows in product(words,repeat=size)
            if all(rows[r][c]==rows[c][r] for r in range(size) for c in range(size))]


def gene_oracle(args):
    start,end,bank = args
    nodes = sorted(set([start]+bank))
    if end not in nodes:
        return -1
    distances = [[0 if a==b else 1 if sum(x!=y for x,y in zip(a,b))==1 else 99 for b in nodes] for a in nodes]
    for mid in range(len(nodes)):
        for first in range(len(nodes)):
            for last in range(len(nodes)):
                distances[first][last] = min(distances[first][last],distances[first][mid]+distances[mid][last])
    answer = distances[nodes.index(start)][nodes.index(end)]
    return answer if answer<99 else -1


def interval_oracle(args):
    intervals = args[0]
    return [min(((a,j) for j,(a,b) in enumerate(intervals) if a>=end),default=(0,-1))[1]
            for start,end in intervals]


def paths_oracle(args):
    mapping,target = positions(args[0]),args[1]
    total = 0
    for path in mapping:
        subtotal = 0
        for depth in range(len(path),-1,-1):
            subtotal += mapping[path[:depth]]
            total += subtotal==target
    return total


def anagrams_oracle(args):
    s,p = args
    return [i for i in range(len(s)-len(p)+1) if sorted(s[i:i+len(p)])==sorted(p)]


def ternary_oracle(args):
    expression = args[0]
    position = 0
    def parse():
        nonlocal position
        token = expression[position]
        position += 1
        if position<len(expression) and expression[position]=='?':
            assert token in 'TF'
            position += 1
            yes = parse()
            assert expression[position]==':'
            position += 1
            no = parse()
            return yes if token=='T' else no
        return token
    answer = parse()
    assert position==len(expression)
    return answer


def lexical_oracle(args):
    n,k = args
    return sorted(range(1,n+1),key=str)[k-1]


def compression_oracle(args):
    result = []
    for char,group in groupby(args[0]):
        count = len(list(group))
        result.append(char)
        if count>1:
            result.extend(str(count))
    return {'return':len(result),'prefix':result}


def linked_sum_oracle(args):
    values = [int(''.join(map(str,digits))) for digits in args]
    return [int(char) for char in str(sum(values))]


def arithmetic_oracle(args):
    nums = args[0]
    return sum(len({row[i]-row[i-1] for i in range(1,len(row))})==1
               for size in range(3,len(nums)+1) for row in combinations(nums,size))


def random_square(rng):
    size = rng.randint(1,7)
    if rng.random()<.5:
        return [[''.join(rng.choice('abc') for _ in range(rng.randint(1,8))) for _ in range(size)]]
    ragged = rng.random()<.5
    grid = [['']*(size-r if ragged else size) for r in range(size)]
    for r,row in enumerate(grid):
        for c in range(r,len(row)):
            grid[r][c] = grid[c][r] = rng.choice('abc')
    return [[''.join(row) for row in grid]]


def random_squares(rng):
    size = rng.randint(1,4)
    words = [''.join(chars) for chars in product('abcd',repeat=size)]
    return [rng.sample(words,rng.randint(1,min(5,len(words))))]


def random_gene(rng):
    start = ''.join(rng.choice('ACGT') for _ in range(8))
    current,bank = start,[]
    for _ in range(rng.randint(0,10)):
        index = rng.randrange(8)
        current = current[:index]+rng.choice('ACGT')+current[index+1:]
        bank.append(current)
    end = rng.choice([start,*bank]) if bank and rng.random()<.7 else ''.join(rng.choice('ACGT') for _ in range(8))
    if bank and rng.random()<.3:
        bank.pop(rng.randrange(len(bank)))
    return [start,end,bank]


def random_intervals(rng):
    starts = rng.sample(range(-20,21),rng.randint(1,15))
    return [[[value,value+rng.randint(0,15)] for value in starts]]


def random_paths(rng):
    count = rng.randint(0,20)
    if count==0:
        return [[],rng.randint(-8,8)]
    mapping,frontier = {():rng.randint(-3,3)},[(0,),(1,)]
    for _ in range(count-1):
        path = frontier.pop(rng.randrange(len(frontier)))
        mapping[path] = rng.randint(-3,3)
        frontier.extend([path+(0,),path+(1,)])
    return [flatten(mapping),rng.randint(-8,8)]


def random_anagrams(rng):
    return [''.join(rng.choice('abc') for _ in range(rng.randint(1,30))),
            ''.join(rng.choice('abc') for _ in range(rng.randint(1,10)))]


def random_ternary(rng):
    def build(depth):
        if depth==4 or depth and rng.random()<.5:
            return rng.choice('0123456789TF')
        return rng.choice('TF')+'?'+build(depth+1)+':'+build(depth+1)
    return [build(0)]


def random_lexical(rng):
    n = rng.randint(1,3000)
    return [n,rng.randint(1,n)]


def random_compression(rng):
    result = []
    for _ in range(rng.randint(1,8)):
        result.extend(rng.choice('aA09!?')*rng.randint(1,30))
    return [result]


def random_linked_sum(rng):
    return [[int(char) for char in str(rng.randrange(10**rng.randint(1,100)))] for _ in range(2)]


def random_arithmetic(rng):
    return [[rng.randint(-5,5) for _ in range(rng.randint(1,10))]]


def chain(values,right=True):
    if not values:
        return []
    result = [values[0]]
    for value in values[1:]:
        result.extend([None,value] if right else [value,None])
    while result[-1] is None:
        result.pop()
    return result


def binary_squares(size):
    cells = [(r,c) for r in range(size) for c in range(r,size)]
    results = []
    for chars in product('ab',repeat=len(cells)):
        matrix = [['']*size for _ in range(size)]
        for (r,c),char in zip(cells,chars):
            matrix[r][c] = matrix[c][r] = char
        results.append([''.join(row) for row in matrix])
    return results


def no_square_dictionary():
    return ['a'+b+c+d for b in 'bcdefghijklmnopqrstuvwxyz' for c in 'abcdefghijklmnopqrstuvwxyz'
            for d in 'abcdefghijklmnopqrstuvwxyz'][:1000]


def progression_count(n):
    return sum(n-(size-1)*step for step in range(1,(n-1)//2+1)
               for size in range(3,(n-1)//step+2))


SQUARE = '''\
def valid_word_square(words):
    for row,word in enumerate(words):
        for col,char in enumerate(word):
            if col>=len(words) or row>=len(words[col]) or words[col][row]!=char:
                return False
    return True
'''

SQUARES = '''\
def word_squares(words):
    from collections import defaultdict
    size = len(words[0])
    prefixes = defaultdict(list)
    for word in words:
        for length in range(size):
            prefixes[word[:length]].append(word)
    path,answers = [],[]
    def visit():
        depth = len(path)
        if depth==size:
            answers.append(path.copy())
            return
        prefix = ''.join(row[depth] for row in path)
        for word in prefixes.get(prefix,[]):
            path.append(word)
            visit()
            path.pop()
    visit()
    return answers
'''

GENE = '''\
def minimum_gene_mutations(start_gene, end_gene, bank):
    from collections import deque
    if start_gene==end_gene:
        return 0
    allowed = set(bank)
    if end_gene not in allowed:
        return -1
    queue = deque([(start_gene,0)])
    seen = {start_gene}
    while queue:
        gene,steps = queue.popleft()
        if gene==end_gene:
            return steps
        for index in range(8):
            for letter in 'ACGT':
                following = gene[:index]+letter+gene[index+1:]
                if following in allowed and following not in seen:
                    seen.add(following)
                    queue.append((following,steps+1))
    return -1
'''

INTERVAL = '''\
def find_right_intervals(intervals):
    from bisect import bisect_left
    order = sorted((start,index) for index,(start,end) in enumerate(intervals))
    starts = [start for start,index in order]
    result = []
    for start,end in intervals:
        position = bisect_left(starts,end)
        result.append(order[position][1] if position<len(order) else -1)
    return result
'''

PATHS = '''\
def count_downward_path_sums(root, target_sum):
    counts = {0:1}
    total = 0
    stack = [(root,0,False)]
    while stack:
        node,prefix,leaving = stack.pop()
        if node is None:
            continue
        if leaving:
            counts[prefix] -= 1
            if counts[prefix]==0:
                del counts[prefix]
            continue
        prefix += node.val
        total += counts.get(prefix-target_sum,0)
        counts[prefix] = counts.get(prefix,0)+1
        stack.append((node,prefix,True))
        stack.append((node.right,prefix,False))
        stack.append((node.left,prefix,False))
    return total
'''

ANAGRAMS = '''\
def anagram_starts(s, p):
    needed,window = [0]*26,[0]*26
    for char in p:
        needed[ord(char)-97] += 1
    result = []
    for right,char in enumerate(s):
        window[ord(char)-97] += 1
        if right>=len(p):
            window[ord(s[right-len(p)])-97] -= 1
        if right>=len(p)-1 and window==needed:
            result.append(right-len(p)+1)
    return result
'''

TERNARY = '''\
def evaluate_ternary(expression):
    stack = []
    for char in reversed(expression):
        if stack and stack[-1]=='?':
            stack.pop()
            yes = stack.pop()
            stack.pop()
            no = stack.pop()
            stack.append(yes if char=='T' else no)
        else:
            stack.append(char)
    return stack[-1]
'''

LEXICAL = '''\
def kth_lexical_number(n, k):
    prefix,remaining = 1,k-1
    while remaining:
        low,high,count = prefix,prefix+1,0
        while low<=n:
            count += min(n+1,high)-low
            low,high = low*10,high*10
        if count<=remaining:
            prefix += 1
            remaining -= count
        else:
            prefix *= 10
            remaining -= 1
    return prefix
'''

COMPRESSION = '''\
def compress_characters(chars):
    read = write = 0
    while read<len(chars):
        end = read+1
        while end<len(chars) and chars[end]==chars[read]:
            end += 1
        count = end-read
        chars[write] = chars[read]
        write += 1
        if count>1:
            first_digit = write
            while count:
                chars[write] = chr(48+count%10)
                write += 1
                count //= 10
            left,right = first_digit,write-1
            while left<right:
                chars[left],chars[right] = chars[right],chars[left]
                left,right = left+1,right-1
        read = end
    return write
'''

LINKED_SUM = '''\
def add_forward_lists(l1, l2):
    left,right = [],[]
    while l1 is not None:
        left.append(l1.val)
        l1 = l1.next
    while l2 is not None:
        right.append(l2.val)
        l2 = l2.next
    head,carry = None,0
    while left or right or carry:
        total = (left.pop() if left else 0)+(right.pop() if right else 0)+carry
        carry = total//10
        head = ListNode(total%10,head)
    return head
'''

ARITHMETIC = '''\
def arithmetic_subsequence_count(nums):
    endings = [{} for _ in nums]
    total = 0
    for right in range(len(nums)):
        for left in range(right):
            difference = nums[right]-nums[left]
            extend = endings[left].get(difference,0)
            total += extend
            endings[right][difference] = endings[right].get(difference,0)+extend+1
    return total
'''


BATCH = {
422: entry('valid_word_square',[('words','list[str]')],'bool',['strings','matrices'],
    ['1 <= words.length <= 500; each word has 1–500 lowercase English letters.',
     'Rows may have different lengths. Every kth row must match the kth column, including character count.',
     'Check the given rows in their existing order; do not rearrange them.'],
    [([['abcd','bnrt','crmy','dtye']],'Each row equals its corresponding column: for example row 1 and column 1 both read bnrt.'),
     ([['abcd','bnrt','crm','dt']],'This ragged arrangement is valid: its row and column lengths are both 4,4,3,2, with matching letters.')],
    [[v] for v in (['a'],['ab'],['a','a'],['ab','ba'],['ab','bb'],['abc','bad','c'],
      ['ball','area','read','lady'],['ab','b'],['aa','a'],['aa','bb'],['abc','bca','cab'],['abc','bc','c'])],
    SQUARE,[SQUARE.replace('for row,word in enumerate(words):','if any(len(word)!=len(words) for word in words):\n        return False\n    for row,word in enumerate(words):'),
            "def valid_word_square(words):\n    return all(row==''.join(col) for row,col in zip(words,zip(*words)))\n"],
    ['Incorrectly requires a full rectangular n-by-n matrix.', 'Truncates checks at the shortest row and overlooks missing mirrored positions.'],
    square_oracle,random_square,
    ['Every existing character needs a matching character at the transposed position.',
     'Check both bounds before comparing words[row][col] with words[col][row].',
     'For each character, reject if the other row is missing, too short, or has a different character.',
     'Mirror checks accept symmetric ragged shapes and reject missing entries. Full-square dimensions are not required.'],
    'If every character has an equal transposed partner, each row and column has the same characters '
    'at the same positions. Missing mirrored positions invalidate the square. Do not use zip to '
    'truncate to the shortest row, and do not require every row to have n characters. Each given '
    'character is checked once with constant extra storage.',
    'O(total characters)','O(1)',difficulty=3,
    stress=[([['a'*500]*500],True),([['a'*(500-r) for r in range(500)]],True)]),
425: entry('word_squares',[('words','list[str]')],'list[list[str]]',['strings','backtracking','recursion'],
    ['1 <= words.length <= 1,000; all words are unique lowercase English strings of the same length n, 1 <= n <= 4.',
     'Build every n-row square whose kth row equals its kth column. A dictionary word may be used more than once.',
     'Outer answer order is arbitrary; row order inside each square matters. Do not emit duplicate squares.'],
    [([['area','lead','wall','lady','ball']],'Both ball | area | lead | lady and wall | area | lead | lady have matching rows and columns.'),
     ([['abat','baba','atan','atal']],'The two squares begin baba | abat | baba and end atal or atan. Reusing baba is allowed and necessary.')],
    [[v] for v in (['a'],['a','b'],['aa'],['ab'],['ab','ba'],['aa','ab','ba','bb'],
      ['aaa','aba','bab'],['abc','bca','cab'],['abcd'],['aaaa'],['aaaa','bbbb'],['aa','bb'])],
    SQUARES,[SQUARES.replace('path.append(word)','if word in path:\n                continue\n            path.append(word)'),
             SQUARES.replace('row[depth]','row[depth-1]')],
    ['Forbids dictionary-word reuse within a square.', 'Builds the next required prefix from the previous column.'],
    squares_oracle,random_squares,
    ['After choosing some rows, the next row already has a required prefix.',
     'Index dictionary words by prefix, then recursively try only words matching the next column prefix.',
     'At depth d, required = previous_rows[0][d] + ... + previous_rows[d-1][d]. Try each match, recurse, and undo.',
     'The prefix constraint checks each new mirrored pair. Copy completed row lists; do not mark dictionary words as globally used.'],
    'The rows already chosen determine the first d characters of row d. A prefix index avoids '
    'scanning unrelated words at each branch. Every matching choice preserves symmetry among '
    'chosen rows, so a depth-n path is a complete square. Unique dictionary words give one path '
    'per square, but the same word can legitimately occupy multiple rows. With W words, prefix '
    'strings cost O(W*n^2) storage; search is output-sensitive with the stated loose worst-case bound.',
    'O(W*n^2 + n*W^n) worst case','O(W*n^2 + n), excluding output',difficulty=8,
    stress=[([no_square_dictionary()],[]),([[''.join(row) for row in product('ab',repeat=4)]],binary_squares(4))]),
433: entry('minimum_gene_mutations',[('start_gene','str'),('end_gene','str'),('bank','list[str]')],'int',
    ['graphs','breadth-first-search'],
    ['Genes have exactly eight characters from A,C,G,T; 0 <= bank.length <= 10.',
     'One mutation changes one character. Every reached gene after a change must belong to the bank.',
     'The starting gene is valid even outside the bank. Equal start/end needs zero mutations; return -1 when unreachable.'],
    [(['AACCGGTT','AACCGGTA',['AACCGGTA']],'Changing the final T to A reaches the bank gene in one mutation.'),
     (['AAAAAAAA','CCAAAAAA',['GAAAAAAA','GCAAAAAA','CCAAAAAA']],
      'The only route is AA… → GA… → GC… → CC…, taking 3 changes although the endpoints differ in only 2 positions.')],
    [[a,b,bank] for a,b,bank in [('AAAAAAAA','AAAAAAAA',[]),('AAAAAAAA','AAAAAAAA',['AAAAAAAA']),
      ('AAAAAAAA','CAAAAAAA',[]),('AAAAAAAA','CAAAAAAA',['CAAAAAAA']),('AAAAAAAA','CCAAAAAA',['CCAAAAAA']),
      ('AAAAAAAA','CCAAAAAA',['CAAAAAAA','CCAAAAAA']),('AACCGGTT','AAACGGTA',['AACCGGTA','AACCGCTA','AAACGGTA']),
      ('TTTTTTTT','TTTTTTTA',['TTTTTTTA','TTTTTTTA']),('AAAAAAAA','CCCCCCCC',['CCCCCCCC']),
      ('AAAAAAAA','GAAAAAAA',['CAAAAAAA','GAAAAAAA']),('AAAAAAAA','GCAAAAAA',['CAAAAAAA','GCAAAAAA']),
      ('ACGTACGT','ACGTTCGT',['ACGTTCGT'])]],
    GENE,[GENE.replace('if start_gene==end_gene:','if False:'),
          "def minimum_gene_mutations(start_gene,end_gene,bank):\n    if start_gene==end_gene: return 0\n    return sum(a!=b for a,b in zip(start_gene,end_gene)) if end_gene in bank else -1\n"],
    ['Requires the destination in the bank even for an already-equal starting gene.', 'Uses endpoint Hamming distance without checking valid intermediate genes.'],
    gene_oracle,random_gene,
    ['Treat valid genes as vertices joined by one-character changes.',
     'Breadth-first search finds the fewest edges; only enqueue bank genes not already visited.',
     'Start at distance 0. For each of eight positions try A,C,G,T, enqueue valid unseen strings, and stop at the destination.',
     'The starting state needs no bank entry. With fixed length and alphabet, each bank gene generates a constant number of candidates.'],
    'Every edge costs one mutation, so BFS layers are increasing shortest distances. Generating '
    'single-character neighbors enforces edge validity, and a bank set enforces allowed intermediate '
    'states. Mark states when enqueuing to avoid repeated cycles. Endpoint differences alone do '
    'not prove a route exists or that no detour is needed. An identical start/end has distance zero.',
    'O(b) for fixed 8-character genes','O(b)',difficulty=5,
    stress=[(['AAAAAAAA','CCCCCCCC',['C'*i+'A'*(8-i) for i in range(1,9)]+['GAAAAAAA','TAAAAAAA']],8)]),
436: entry('find_right_intervals',[('intervals','list[list[int]]')],'list[int]',
    ['arrays','binary-search','sorting'],
    ['1 <= intervals.length <= 20,000; -10^6 <= start <= end <= 10^6.',
     'All starts are unique. Choose the smallest start >= the current end, returning that interval\'s original index.',
     'A zero-length interval may choose itself. Preserve original query order and return -1 if no right interval exists.'],
    [([[[1,2]]],'No start is at least 2, so the only answer is -1.'),
     ([[[3,4],[2,3],[1,2]]],'The answers are [-1,0,1]. Touching endpoints qualify, and indices refer to the unsorted input.')],
    [[v] for v in (
      [[0,0]],[[-1,0],[0,0]],[[1,4],[2,3],[3,4]],[[4,4],[2,4],[0,2]],
      [[-5,-3],[-3,-1],[-1,0]],[[10,20],[1,2]],[[2,2],[1,2]],
      [[-1000000,1000000]],[[0,1],[2,3],[4,5]],[[3,3],[1,1],[2,2]],
      [[5,9],[2,5],[9,9]],[[0,100],[1,99],[2,98]])],
    INTERVAL,[INTERVAL.replace('bisect_left','bisect_right'),INTERVAL.replace('order[position][1]','position')],
    ['Skips an equal start, wrongly requiring a strict gap.', 'Returns the sorted position instead of the original interval index.'],
    interval_oracle,random_intervals,
    ['Only starts matter when selecting the smallest eligible right interval.',
     'Sort starts together with their original indices, then lower-bound each end.',
     'Find the first sorted start >= end; return its saved input index or -1.',
     'Lower-bound includes equality and can return the current interval when start=end. Queries remain in original order.'],
    'Sorting makes eligible starts a suffix. Binary search locates its first element, which is the '
    'minimum qualifying start. Store original indices alongside starts to undo sorting for answers. '
    'Do not force a different interval: equality and zero-length self matches are part of the contract.',
    'O(n log n)','O(n)',difficulty=5,
    stress=[([[[i,i+1] for i in range(19999,-1,-1)]],[-1]+list(range(19999))),
            ([[[i,i] for i in range(-10000,10000)]],list(range(20000)))]),
437: entry('count_downward_path_sums',[('root','TreeNode | None'),('target_sum','int')],'int',
    ['trees','recursion','depth-first-search','hash-maps'],
    ['0 <= node count <= 1,000; -10^9 <= node values <= 10^9; -1,000 <= target_sum <= 1,000.',
     'Count nonempty parent-to-child paths. They may begin or end at any node, not only root or leaves.',
     'Different node paths count separately even if their values are identical. The function receives TreeNode objects or None.'],
    [([[10,5,-3,3,2,None,11,3,-2,None,1],8],'The three paths are 5→3, 5→2→1, and -3→11. None needs to start at the root.'),
     ([[0,0,0],0],'Each singleton zero and each root-to-child path qualifies: 3 + 2 = 5. The empty path is not counted.')],
    [[tree,target] for tree,target in [([],0),([1],1),([1],0),([0],0),([1,2,3],3),
      ([1,-1,-1],0),([5,4,8,11,None,13,4,7,2,None,None,5,1],22),([1,None,2,None,3],3),
      ([1,2,2,1,None,None,1],3),([10**9,-10**9,0],0),([2,-2,2,-2],-2),([1,0,0],0)]],
    PATHS,[PATHS.replace('counts[prefix] -= 1','pass  # forgot to leave this branch'),
           PATHS.replace('total += counts.get(prefix-target_sum,0)','total += int(prefix==target_sum)')],
    ['Retains prefix counts from completed branches, counting paths across unrelated nodes.', 'Counts only paths beginning at the root.'],
    paths_oracle,random_paths,
    ['A downward path sum is the difference between two prefix sums on the same root-to-node chain.',
     'Track ancestor-prefix frequencies during DFS, and remove a prefix when leaving its node.',
     'Before adding the current prefix, count prefix-target in the map. Add the prefix, visit children, then decrement it.',
     'Initialize prefix 0 once for paths beginning at root. Exit events emulate recursive backtracking without call-stack overflow.'],
    'At a node with prefix S, every ancestor boundary with prefix S-target defines one desired '
    'nonempty path ending here. Query before inserting S to exclude empty paths. Frequencies handle '
    'equal prefixes caused by zeros or cancellation. DFS exit events restore the map before a '
    'sibling branch, preventing cross-branch paths. Removing zero-count entries bounds storage by '
    'tree height. Python integers retain large signed cumulative sums exactly.',
    'O(n) expected','O(height)',difficulty=6,
    stress=[([chain([0]*1000),0],500500),([chain([1]*1000,False),1000],1),
            ([chain([10**9,-10**9]*500),0],250000)]),
438: entry('anagram_starts',[('s','str'),('p','str')],'list[int]',
    ['strings','hash-maps','sliding-window'],
    ['1 <= s.length, p.length <= 30,000; lowercase English letters only.',
     'Return every zero-based start of a contiguous substring with exactly the same letter counts as p.',
     'Overlapping matches count. Return indices in any order; a longer pattern has no matches.'],
    [(['cbaebabacd','abc'],'cba at index 0 and bac at index 6 each use one a, one b, and one c.'),
     (['abab','ab'],'ab, ba, and ab begin at indices 0,1,2. All three overlapping windows qualify.')],
    [[s,p] for s,p in [('a','a'),('a','b'),('a','aa'),('aaaa','aa'),('aabb','ab'),('bbaa','aa'),
      ('abab','aab'),('abc','abc'),('abc','c'),('baaab','aab'),('zzzz','zz'),('abcabc','bca')]],
    ANAGRAMS,[ANAGRAMS.replace('needed[ord(char)-97] += 1','needed[ord(char)-97] = 1'),
              ANAGRAMS.replace('enumerate(s):','enumerate(s[:-1]):')],
    ['Tracks pattern membership instead of multiplicity.', 'Never processes the last character, dropping the final window.'],
    anagrams_oracle,random_anagrams,
    ['Anagrams have matching frequency counts, not necessarily matching character order.',
     'Maintain a fixed-size window of length len(p) and two 26-entry count arrays.',
     'Add the incoming character, remove the outgoing one, and compare counts once the window is full.',
     'Comparing 26 counts is constant work. Sliding by one position preserves overlapping matches.'],
    'At each right endpoint, the window contains exactly the last len(p) characters once enough '
    'characters have arrived. Equality with the pattern count vector proves an anagram. The first '
    'full window and the last window both matter; a pattern longer than the text never produces one.',
    'O(len(s)+len(p))','O(1), excluding output',difficulty=5,
    stress=[(['a'*30000,'a'*15000],list(range(15001))),(['ab'*15000,'c'*30000],[])]),
439: entry('evaluate_ternary',[('expression','str')],'str',['strings','stacks','recursion'],
    ['5 <= expression.length <= 10,000; input is a valid ternary expression using T,F,?,:, and single decimal digits.',
     'Conditions are T or F; branches may be nested. Group conditional expressions right-to-left.',
     'Return one character as a string: a digit, T, or F. Do not use Python truthiness of the character F.'],
    [(['T?2:3'],'T chooses the true branch, so return the string "2".'),
     (['T?T?F:5:3'],'The true branch is T?F:5, which evaluates to F. The outer true condition therefore returns "F".')],
    [[s] for s in ('F?1:T?4:5','F?2:3','T?0:9','F?T:F','T?T:F','T?1:F?2:3',
                   'F?T?1:2:3','F?0:F?1:T?2:3','T?F?1:2:3','T?9:0','F?9:T','T?F?T:F:F')],
    TERNARY,["def evaluate_ternary(expression):\n    return expression[2] if expression[0]=='T' else expression[-1]\n",
             TERNARY.replace("char=='T'",'bool(char)')],
    ['Assumes both branches are single tokens, ignoring nested structure.', 'Treats nonempty F as a true Python string.'],
    ternary_oracle,random_ternary,
    ['A branch may itself be an entire conditional expression.',
     'Scan from right to left so nested branch results are ready before their condition.',
     'On a condition before ?, pop the reduced true and false branches and push the selected value; otherwise push the token.',
     'Each token is pushed and popped at most once. An explicit stack supports thousands of nested conditions without recursive evaluation.'],
    'Right-to-left scanning respects right association. When a condition is encountered, its two '
    'branches have already collapsed into single results, so selection is local. Keep T/F as '
    'literal characters and test equality with T; both strings are truthy in Python. Return the '
    'final character, preserving boolean-looking results as strings.',
    'O(n)','O(n)',difficulty=6,
    stress=[(['F?0:'*2499+'7'],'7'),(['T?'*2499+'F'+':0'*2499],'F')]),
440: entry('kth_lexical_number',[('n','int'),('k','int')],'int',['math','trees','prefix-counting'],
    ['1 <= k <= n <= 10^9. Rank the integers 1 through n by their decimal text, without leading zeros.',
     'k is one-based. Return the selected integer, not its position or the whole sorted list.'],
    [([13,2],'The order starts 1,10,11,12,13,2,…, so rank 2 contains 10.'),
     ([13,6],'After all five numbers beginning with 1, rank 6 contains 2. A whole prefix subtree can be skipped.')],
    [[n,k] for n,k in ((1,1),(2,2),(9,9),(10,2),(10,10),(11,3),(19,11),(20,12),
                       (99,50),(100,3),(101,4),(1000,1000))],
    LEXICAL,['def kth_lexical_number(n,k):\n    return k\n',
             LEXICAL.replace('prefix,remaining = 1,k-1','prefix,remaining = 1,max(0,k-2)')],
    ['Uses numeric order instead of decimal lexicographic order.', 'Shifts a one-based rank twice and selects the previous lexicographic item.'],
    lexical_oracle,random_lexical,
    ['Decimal prefixes form a tree whose preorder is lexicographic order.',
     'Count integers under the current prefix to choose between skipping that subtree and descending into it.',
     'At each digit length intersect [prefix*10^d,(prefix+1)*10^d) with [1,n+1); sum widths and compare with remaining rank.',
     'Skip a subtree when its count fits before the target; otherwise consume its root and descend. Counting levels avoids enumerating up to a billion values.'],
    'A prefix subtree contains consecutive numeric intervals at successive decimal lengths. Clip '
    'each interval at n+1 to count it exactly. Starting at prefix 1 and rank offset k-1, skip whole '
    'subtrees or descend to the first child. At most a fixed number of sibling moves occur at each '
    'digit level, each requiring a logarithmic-depth count. This yields O(log^2 n) time and O(1) space.',
    'O(log^2 n)','O(1)',difficulty=8,
    stress=[([10**9,10],10**9),([10**9,111111112],199999999),([10**9,111111113],2),([10**9,10**9],999999999)]),
443: entry('compress_characters',[('chars','list[str]')],'int',['strings','two-pointers'],
    ['1 <= chars.length <= 2,000; each item is one letter, digit, or symbol.',
     'Compress consecutive runs in the original array: write the character, then decimal count digits only for counts greater than one.',
     'Return the meaningful prefix length k. Only chars[:k] is graded; the tail is ignored. Target constant extra space.'],
    [([list('aabbccc')],'Return 6 and write [a,2,b,2,c,3] into the first six cells. Returning a separate string is not sufficient.'),
     ([list('a'+'b'*12)],'Return 4 with prefix [a,b,1,2]. A singleton has no count, and 12 occupies two character cells.')],
    [[list(s)] for s in ('a','aa','abc','aaaaaaaaaa','aaaaaaaaaaa','aab','abb','!!??','1111','AAaa','a'*100,'abababa')],
    COMPRESSION,["def compress_characters(chars):\n    from itertools import groupby\n    result=[]\n    for char,group in groupby(chars):\n        count=len(list(group))\n        result.append(char)\n        if count>1: result.extend(str(count))\n    return len(result)\n",
                 COMPRESSION.replace('if count>1:\n','if count>1:\n            count %= 10\n')],
    ['Calculates the compressed length but never updates the original array.', 'Keeps only the ones digit of a multi-digit run length.'],
    compression_oracle,random_compression,
    ['Read one complete run before overwriting its compressed output.',
     'Use a read pointer for runs and a write pointer for the meaningful output prefix.',
     'Write the run character. For count>1 write its digits, then advance to the next unread run; return write.',
     'Compression never expands a run, so writes cannot overtake unread input. Extract count digits arithmetically and reverse that digit segment in place for O(1) auxiliary space.'],
    'Save the end of each run before writing. A singleton emits only its character; longer runs '
    'emit the character followed by count digits. The reference writes count digits least-significant '
    'first, then reverses just that output segment without allocating a count string. Since each '
    'compressed run is no longer than its input run, unread data is safe. The judge checks both '
    'the integer length and the actual modified prefix, not the unused tail.',
    'O(n)','O(1)',difficulty=6,
    stress=[([list('a'*2000)],{'return':5,'prefix':list('a2000')}),
            ([list('!'*1000+'?'*1000)],{'return':10,'prefix':list('!1000?1000')})]),
445: entry('add_forward_lists',[('l1','ListNode | None'),('l2','ListNode | None')],'ListNode | None',
    ['linked-lists','stacks','math'],
    ['Each nonempty list has 1–100 digit nodes (0–9), most-significant digit first.',
     'No leading zero except the single-node number 0. Return the sum as a ListNode chain in the same forward-digit order.',
     'Follow-up: avoid reversing the input lists. The reference uses stacks and leaves both inputs unchanged.'],
    [([[7,2,4,3],[5,6,4]],'The chains represent 7243 and 564. Their sum is the chain 7→8→0→7.'),
     ([[9,9],[1]],'Carry passes through both 9s and creates a new leading node: 1→0→0.')],
    [[a,b] for a,b in [([0],[0]),([0],[1]),([1],[0]),([1],[2]),([9],[9]),([1,0],[9]),
      ([9],[1,0]),([2,4,3],[5,6,4]),([1,0,0],[1]),([5,0],[5,0]),([1,2,3],[4,5,6]),([9,0,9],[9,1])]],
    LINKED_SUM,[LINKED_SUM.replace('return head','previous = None\n    while head is not None:\n        following = head.next\n        head.next = previous\n        previous,head = head,following\n    return previous'),
                LINKED_SUM.replace('while left or right or carry:','while left or right:')],
    ['Returns least-significant digit first, confusing the reverse-order addition contract.', 'Drops a final carry after both stacks are exhausted.'],
    linked_sum_oracle,random_linked_sum,
    ['Addition starts at the least-significant digits, but these lists expose the most-significant ones first.',
     'Push input digits onto two stacks; pop from their ends to add with carry.',
     'While either stack or carry remains, compute one digit and prepend its new node to the answer.',
     'Prepending restores forward order without reversing input links. Both inputs and output remain real linked lists, not returned Python arrays.'],
    'Two stacks expose digits in addition order without changing either input. Pop available digits '
    'or use zero when a stack is empty, propagate carry, and prepend each result node. A remaining '
    'carry creates a new leading node. Unlike the earlier reverse-digit addition exercise, the '
    'returned chain is most-significant first. The small oracle converts at most 100 digits to an '
    'exact integer; the reference performs node/digit arithmetic only.',
    'O(m+n)','O(m+n), excluding output',difficulty=6,
    stress=[([[9]*100,[1]],[1]+[0]*100),([[5]*100,[4]*100],[9]*100)]),
446: entry('arithmetic_subsequence_count',[('nums','list[int]')],'int',
    ['arrays','dynamic-programming'],
    ['1 <= nums.length <= 1,000; -2^31 <= nums[i] <= 2^31-1.',
     'Count index-distinct arithmetic subsequences of length at least three, keeping original order but allowing gaps.',
     'The answer is guaranteed to fit a signed 32-bit integer. Differences may exceed that range; equal-valued choices at different indices remain distinct.'],
    [([[2,4,6,8,10]],'Six contiguous arithmetic slices plus the gapped subsequence [2,6,10] give 7.'),
     ([[7,7,7,7,7]],'Every index choice of at least three items qualifies: C(5,3)+C(5,4)+C(5,5)=16, not one value sequence.')],
    [[v] for v in ([1],[1,2],[1,2,3],[3,2,1],[1,1,1],[1,2,4],[0,0,0,0],
      [1,3,2,5,7],[1,2,3,4],[-2**31,0,-2**31],[-2**31,-1,2**31-2],[2**31-1,-2**31,0])],
    ARITHMETIC,[ARITHMETIC.replace('total += extend','total += extend+1'),
                'def arithmetic_subsequence_count(nums):\n    total=ending=0\n    for i in range(2,len(nums)):\n        ending=ending+1 if nums[i]-nums[i-1]==nums[i-1]-nums[i-2] else 0\n        total+=ending\n    return total\n'],
    ['Counts new length-two pairs as complete arithmetic subsequences.', 'Counts only contiguous slices, omitting valid subsequences with gaps.'],
    arithmetic_oracle,random_arithmetic,
    ['A partial arithmetic sequence is described by its last index and common difference.',
     'For each pair left<right, extend every sequence ending at left with that difference.',
     'Add previous_count to the answer; store previous_count+1 at right to include the new pair as a future seed.',
     'Pairs are seeds, not answers. Each extension reaches length at least three and is counted at its unique final index.'],
    'Store counts of length-at-least-two subsequences by final index and difference. For each '
    'earlier index, every matching state extends to a valid answer; the new two-item pair is stored '
    'but not counted yet. Counts represent index choices, preserving multiplicities of equal values. '
    'Use exact signed differences. The 1,000-item stress progression has a bounded answer; an '
    'all-equal 1,000-item input would violate the source\'s answer-size guarantee and is not generated.',
    'O(n^2) expected','O(n^2)',difficulty=8,
    stress=[([list(range(1000))],progression_count(1000)),([[0]*31],2**31-1-31-31*30//2)]),
}

BATCH[425]['comparator'] = 'unordered'
BATCH[438]['comparator'] = 'unordered'
BATCH[425]['prerequisites'] = ['recursion','backtracking']
BATCH[440]['prerequisites'] = ['math','trees']
BATCH[446]['prerequisites'] = ['arrays','dynamic-programming']
BATCH[437]['params'] = [('root','TreeNode | None','treenode'),('target_sum','int','raw')]
BATCH[443]['result_mode'] = 'returned_prefix'
BATCH[443]['mutated_parameter'] = 0
BATCH[443]['sample_contract_adapter'] = {
    'source_sample':'Input chars = ["a","a","b","b","c","c","c"] → Output 6.',
    'arguments':[list('aabbccc')], 'expected':{'return':6,'prefix':list('a2b2c3')},
    'reason':'The workbook sample prints only the returned count. The source description also explicitly gives the required mutated prefix [a,2,b,2,c,3]; the adapter preserves both parts of that contract.'}
BATCH[445]['params'] = [('l1','ListNode | None','listnode'),('l2','ListNode | None','listnode')]
BATCH[445]['adapter'] = 'listnode'
