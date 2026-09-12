"""Prefix traversal, structural parsing, recursive windows, greedy digits and frog states."""
from collections import Counter, deque
from itertools import combinations
import re

from .import_batch_003 import entry


def lexical_oracle(args):
    return sorted(range(1,args[0]+1),key=str)


def file_oracle(args):
    records = [(len(line)-len(line.lstrip('\t')),line.lstrip('\t')) for line in args[0].split('\n')]
    best = 0
    for index,(depth,name) in enumerate(records):
        if '.' not in name:
            continue
        parts, needed = [name], depth-1
        for level,parent in reversed(records[:index]):
            if level == needed:
                parts.insert(0,parent)
                needed -= 1
        best = max(best,len('/'.join(parts)))
    return best


def elimination_oracle(args):
    values, left = list(range(1,args[0]+1)), True
    while len(values)>1:
        if left:
            values = values[1::2]
        else:
            values = values[::-1][1::2][::-1]
        left = not left
    return values[0]


def elimination_reflection(n):
    return 1 if n == 1 else 2*(n//2+1-elimination_reflection(n//2))


BYTE_PATTERN = re.compile(r'(?:0[01]{7}|110[01]{5}10[01]{6}|1110[01]{4}(?:10[01]{6}){2}|11110[01]{3}(?:10[01]{6}){3})+')


def utf_oracle(args):
    return BYTE_PATTERN.fullmatch(''.join(f'{value:08b}' for value in args[0])) is not None


def decode_oracle(args):
    text = args[0]
    def expand(match):
        count = int(match[1])
        if not 1<=count<=300:
            raise ValueError('Repeat count is outside the source bounds')
        return count*match[2]
    while '[' in text:
        changed = re.sub(r'([0-9]+)\[([a-z]*)\]',expand,text)
        if changed == text:
            raise ValueError('Invalid encoding in fixture')
        text = changed
    if re.fullmatch('[a-z]*',text) is None:
        raise ValueError('Undecoded control characters remain in fixture')
    return text


def repeating_oracle(args):
    s,k = args
    best = 0
    for start in range(len(s)):
        counts = Counter()
        for end in range(start,len(s)):
            counts[s[end]] += 1
            if min(counts.values()) >= k:
                best = max(best,end-start+1)
    return best


def replacement_oracle(args):
    queue, seen = deque([(args[0],0)]), {args[0]}
    while queue:
        value,distance = queue.popleft()
        if value == 1:
            return distance
        for following in ([value//2] if value%2==0 else [value-1,value+1]):
            if following not in seen:
                seen.add(following)
                queue.append((following,distance+1))


def digits_oracle(args):
    num,k = args
    candidates = (''.join(num[i] for i in indices) for indices in combinations(range(len(num)),len(num)-k))
    return min(candidates).lstrip('0') or '0'


def frog_oracle(args):
    stones = args[0]
    def walk(index,previous):
        if index == len(stones)-1:
            return True
        for nxt in range(index+1,len(stones)):
            distance = stones[nxt]-stones[index]
            if distance > previous+1:
                break
            if distance >= max(1,previous-1) and walk(nxt,distance):
                return True
        return False
    return walk(0,0)


def abbreviation_oracle(args):
    word,abbr = args
    pattern = []
    for token in re.findall(r'[0-9]+|[a-z]',abbr):
        if token.isdigit():
            if token[0] == '0' or int(token)>len(word):
                return False
            pattern.append('.{'+token+'}')
        else:
            pattern.append(token)
    return re.fullmatch(''.join(pattern),word) is not None


def random_lexical(rng):
    return [rng.randint(1,5000)]


def random_file(rng):
    lines = []
    serial = 0
    def directory(depth):
        nonlocal serial
        for _ in range(rng.randint(1,4)):
            serial += 1
            name = rng.choice(['a','Long Name ','9'])+str(serial)
            is_file = depth >= 3 or rng.random()<.5
            lines.append('\t'*depth+name+('.txt' if is_file else ''))
            if not is_file:
                directory(depth+1)
    directory(0)
    return ['\n'.join(lines)]


def random_elimination(rng):
    return [rng.randint(1,1000)]


def random_utf(rng):
    if rng.random()<.5:
        return [[rng.randrange(256) for _ in range(rng.randint(1,30))]]
    result = []
    for _ in range(rng.randint(1,8)):
        width = rng.randint(1,4)
        result.append(rng.randrange(128) if width==1 else rng.randrange({2:192,3:224,4:240}[width],{2:224,3:240,4:248}[width]))
        result.extend(rng.randrange(128,192) for _ in range(width-1))
    return [result]


def random_decode(rng):
    def group(depth):
        if depth == 3 or rng.random()<.35:
            return ''.join(rng.choice('abc') for _ in range(rng.randint(1,3)))
        if rng.random()<.6:
            return str(rng.randint(1,12))+'['+group(depth+1)+']'
        return group(depth+1)+group(depth+1)
    while True:
        text = group(0)
        if len(text)<=30 and len(decode_oracle([text]))<=100000:
            return [text]


def random_repeating(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,20))),rng.randint(1,10)]


def random_replacement(rng):
    return [rng.randint(1,2**31-1)]


def random_digits(rng):
    n = rng.randint(1,10)
    text = rng.choice('123456789')+''.join(rng.choice('0123456789') for _ in range(n-1))
    return [text,rng.randint(1,n)]


def random_frog(rng):
    return [[0]+sorted(rng.sample(range(1,30),rng.randint(1,11))) ]


def random_abbreviation(rng):
    word = ''.join(rng.choice('abc') for _ in range(rng.randint(1,10)))
    if rng.random()<.5:
        return [word,''.join(rng.choice('abc01239') for _ in range(rng.randint(1,9)))]
    parts, count = [], 0
    for char in word:
        if rng.random()<.5:
            count += 1
        else:
            if count:
                parts.append(str(count))
                count = 0
            parts.append(char)
    if count:
        parts.append(str(count))
    return [word,''.join(parts)]


LEXICAL = '''\
def lexicographical_numbers(n):
    result, current = [], 1
    for _ in range(n):
        result.append(current)
        if current*10 <= n:
            current *= 10
        else:
            while current%10 == 9 or current+1 > n:
                current //= 10
            current += 1
    return result
'''
FILE = '''\
def longest_absolute_path(input):
    lengths, best = [0], 0
    for line in input.split('\\n'):
        name = line.lstrip('\\t')
        depth = len(line)-len(name)
        del lengths[depth+1:]
        total = lengths[depth]+len(name)
        if '.' in name:
            best = max(best,total)
        else:
            lengths.append(total+1)
    return best
'''
ELIMINATION = '''\
def last_remaining(n):
    head, step, left = 1,1,True
    while n>1:
        if left or n%2:
            head += step
        n //= 2
        step *= 2
        left = not left
    return head
'''
UTF = '''\
def valid_utf8(data):
    remaining = 0
    for value in data:
        if remaining:
            if value & 0xC0 != 0x80:
                return False
            remaining -= 1
        elif value < 128:
            continue
        elif value & 0xE0 == 0xC0:
            remaining = 1
        elif value & 0xF0 == 0xE0:
            remaining = 2
        elif value & 0xF8 == 0xF0:
            remaining = 3
        else:
            return False
    return remaining == 0
'''
DECODE = '''\
def decode_string(s):
    index = 0
    def parse():
        nonlocal index
        pieces = []
        while index<len(s) and s[index]!=']':
            if s[index].isdigit():
                count = 0
                while s[index].isdigit():
                    count = count*10+int(s[index])
                    index += 1
                index += 1
                segment = parse()
                index += 1
                pieces.append(segment*count)
            else:
                pieces.append(s[index])
                index += 1
        return ''.join(pieces)
    return parse()
'''
REPEATING = '''\
def longest_repeating_substring(s, k):
    def solve(left,right):
        if right-left < k:
            return 0
        counts = {}
        for index in range(left,right):
            char = s[index]
            counts[char] = counts.get(char,0)+1
        bad = {char for char,count in counts.items() if count<k}
        if not bad:
            return right-left
        best, start = 0,left
        for index in range(left,right):
            if s[index] in bad:
                best = max(best,solve(start,index))
                start = index+1
        return max(best,solve(start,right))
    return solve(0,len(s))
'''
REPLACEMENT = '''\
def integer_replacement(n):
    steps = 0
    while n!=1:
        if n%2 == 0:
            n //= 2
        elif n == 3 or n & 3 == 1:
            n -= 1
        else:
            n += 1
        steps += 1
    return steps
'''
DIGITS = '''\
def remove_k_digits(num, k):
    stack = []
    for digit in num:
        while k and stack and stack[-1]>digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    if k:
        del stack[-k:]
    return ''.join(stack).lstrip('0') or '0'
'''
FROG = '''\
def can_cross(stones):
    jumps = {position:set() for position in stones}
    jumps[0].add(0)
    for position in stones:
        for previous in jumps[position]:
            for distance in (previous-1,previous,previous+1):
                if distance>0 and position+distance in jumps:
                    if position+distance == stones[-1]:
                        return True
                    jumps[position+distance].add(distance)
    return False
'''
ABBREVIATION = '''\
def valid_word_abbreviation(word, abbr):
    i = j = 0
    while j<len(abbr):
        if abbr[j].isdigit():
            if abbr[j]=='0':
                return False
            count = 0
            while j<len(abbr) and abbr[j].isdigit():
                count = count*10+int(abbr[j])
                j += 1
            i += count
            if i>len(word):
                return False
        else:
            if i>=len(word) or word[i]!=abbr[j]:
                return False
            i += 1
            j += 1
    return i==len(word)
'''


BATCH = {
386: entry('lexicographical_numbers',[('n','int')],'list[int]',
    ['math','trees','depth-first-search','recursion'],
    ['1 <= n <= 50,000.', 'Return each integer from 1 through n exactly once, ordered by its decimal text.',
     'Required target: O(n) time and O(1) extra space excluding the output.'],
    [([13],'Decimal prefix 1 comes first: 1, 10, 11, 12, 13; then 2 through 9. Numeric sorting would put 2 before 10.'),
     ([21],'The prefix-1 group is 1, 10 through 19. It is followed by 2, 20, 21, then 3 through 9.')],
    [[n] for n in (1,2,8,9,10,11,19,20,99,100,101,109)],
    LEXICAL,['def lexicographical_numbers(n):\n    return list(range(1,n+1))',
             'def lexicographical_numbers(n):\n    return sorted(range(1,n+1),key=lambda value:str(value)[0])'],
    ['Uses numeric rather than dictionary order.', 'Compares only the first digit, missing deeper decimal prefixes.'],
    lexical_oracle,random_lexical,
    ['Think of integers as a decimal prefix tree, visited before their descendants.',
     'Descend by multiplying by ten when possible; otherwise move to the next sibling.',
     'When the next sibling exceeds n or the last digit is 9, divide by ten until a sibling exists, then increment.',
     'Iterative preorder traversal needs only the current integer. Across the traversal, climbs and descents total O(n). A recursive traversal is simpler but uses stack space.'],
    'A number precedes all longer numbers beginning with its digits. Start at 1; descend to current*10 '
    'if it exists. Otherwise climb past exhausted prefixes (trailing 9 or a next value beyond n), '
    'then increment. Emit exactly n values. This simulates recursive digit-tree preorder without '
    'a recursion stack or sorting; only the required output list grows.',
    'O(n)','O(1) excluding output',difficulty=5,
    stress=[([50000],lexical_oracle([50000]))]),
388: entry('longest_absolute_path',[('input','str')],'int',
    ['strings','stacks','trees'],
    ['1 <= input.length <= 10,000; the filesystem representation is valid.',
     'Newline (\\n) separates entries; leading tabs (\\t) give directory depth. Spaces inside names count.',
     'Directories contain letters/digits/spaces. A file has a nonempty name and extension separated by a dot.',
     'Return the longest full file-path length including / separators, or 0 when there are no files. Do not access the real filesystem.'],
    [(['dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext'],'The only file is dir/subdir2/file.ext: 3 + 1 + 7 + 1 + 8 = 20 characters.'),
     (['longdirectory\n\tempty\na.txt'],'The long directory branch has no file. Only the root file a.txt counts, so return 5.')],
    [[s] for s in ('a','a.txt','dir\n\tf.x','a\n\tb\n\t\tf.x','a\n\tb\n\tc.x',
                   'a\n\tb\n\t\tf.x\n\tc.txt','a.txt\nbb.txt','long\n\ts.x\nb\n\tlonger.txt',
                   'a b\n\tc d.e f','a\n\tb\n\t\tc','a\n\tb.x\n\tc\n\t\td.x','a\n\t f .x ')],
    FILE,[FILE.replace('best = max(best,total)','pass').replace('lengths.append(total+1)','lengths.append(total+1)\n            best = max(best,total)'),
          FILE.replace('lengths.append(total+1)','lengths.append(total)')],
    ['Counts directory-only paths as files.', 'Omits slash separators between path components.'],
    file_oracle,random_file,
    ['A file path consists of its name plus its ancestor directory names and slashes.',
     'Keep the cumulative prefix length for each directory depth, discarding deeper prefixes when moving to a sibling.',
     'For depth d: total = prefix[d] + len(name). Update the answer for files; save total+1 as the child prefix for directories.',
     'Only leading tabs encode depth. Do not strip spaces from names, and never let a long empty directory win.'],
    'Scan entries in their encoded preorder. Maintain directory-prefix lengths indexed by depth, '
    'starting with zero for root entries. A file updates the maximum; a directory stores its prefix '
    'including one slash for descendants. Trim stale deeper prefixes when the depth decreases. '
    'This operates only on a string, not files on disk. Splitting lines uses O(m) space in this implementation.',
    'O(m), m = input length','O(m)',difficulty=5,
    stress=[(['a'*9998+'.x'],10000),
            (['\n'.join('\t'*d+'a' for d in range(120))+'\n'+'\t'*120+'f.x'],243)]),
390: entry('last_remaining',[('n','int')],'int',
    ['math','recursion'],
    ['1 <= n <= 1,000,000,000.', 'Each round deletes the first encountered element, then every other element; direction alternates.',
     'When only one element remains, stop without performing another round.'],
    [([9],'The surviving lists are [2,4,6,8], then [2,6] when deleting from the right, then [6].'),
     ([6],'First [2,4,6] survives. The right-to-left round removes 6 and 2, leaving 4.')],
    [[n] for n in (1,2,3,4,5,7,8,10,11,12,15,16)],
    ELIMINATION,[ELIMINATION.replace('if left or n%2:','if left:'),ELIMINATION.replace('if left or n%2:','if True:')],
    ['Fails to move the first survivor during a right-to-left round with an odd count.',
     'Always moves the first survivor, even when an even right-to-left round preserves it.'],
    elimination_oracle,random_elimination,
    ['Survivors always form an arithmetic progression; you do not need to store them.',
     'Track the first survivor, gap, remaining count, and direction.',
     'Advance the first survivor when deleting from the left or when the remaining count is odd. Then halve count, double gap, and reverse direction.',
     'There are O(log n) rounds. An equivalent recursive reflection formula is f(n)=2*(floor(n/2)+1−f(floor(n/2))), with f(1)=1.'],
    'Deleting alternate elements doubles the gap. From the left, the first element is always '
    'removed; from the right, it is removed exactly when the count is odd. Update the head before '
    'halving the count. The recursive formula reflects the next round’s survivor index within '
    'the even numbers, providing another way to understand alternating direction.',
    'O(log n)','O(1)',difficulty=5,
    stress=[([n],elimination_reflection(n)) for n in (10**9,10**9-1,2**29)]),
393: entry('valid_utf8',[('data','list[int]')],'bool',
    ['bit-manipulation','arrays','state-machines'],
    ['1 <= data.length <= 20,000; 0 <= data[i] <= 255.',
     'Check only the listed 1–4-byte prefix patterns. A continuation byte must start with binary 10.',
     'This exercise does not add Unicode scalar-value, surrogate, or shortest-encoding restrictions.'],
    [([[197,130,1]],'11000101 starts a two-byte group, 10000010 completes it, and 00000001 is a separate one-byte group.'),
     ([[235,140,4]],'11101011 requires two continuation bytes. 10001100 is valid, but 00000100 is not a continuation byte.')],
    [[v] for v in ([0],[127],[128],[197],[197,130],[197,197],[224,128,128],
                   [240,159,152,128],[240,128,128],[248,128,128,128,128],[255],
                   [192,128],[237,160,128],[244,144,128,128])],
    UTF,[UTF.replace('return remaining == 0','return True'),UTF.replace('value & 0xC0 != 0x80','value & 0x80 != 0x80')],
    ['Accepts an unfinished multibyte group at the end.', 'Checks only a high bit of 1 rather than the required two-bit prefix 10.'],
    utf_oracle,random_utf,
    ['Keep the number of continuation bytes still required by the current leading byte.',
     'While that number is positive, accept only bytes beginning with 10. Otherwise recognize a legal leading prefix.',
     'Prefixes 0, 110, 1110, and 11110 require 0, 1, 2, and 3 following continuation bytes. Decrement on each continuation; require zero at the end.',
     'A leading byte is not a continuation byte. The source exercise checks these structural patterns only, so a strict Unicode decoder enforces extra rules.'],
    'A small state machine tracks the required continuation count. Masks distinguish ASCII, '
    'two-, three-, and four-byte headers. An unexpected continuation, illegal five-byte header, '
    'wrong continuation prefix, or unfinished group fails. The grading contract follows the '
    'listed bit patterns, not all real-world Unicode validity restrictions: for example '
    '[192,128] satisfies this exercise’s two-byte shape even though strict UTF-8 decoding rejects it.',
    'O(n)','O(1)',difficulty=5,
    stress=[([[65]*20000],True),([[240,128,128,128]*5000],True),([[65]*19999+[226]],False)]),
394: entry('decode_string',[('s','str')],'str',
    ['strings','recursion','parsing','stacks'],
    ['1 <= s.length <= 30; only lowercase letters, digits, and square brackets.',
     'The encoding is valid; every repeat count is in [1,300]. Digits are counts, never literal output.',
     'The decoded output length is at most 100,000. Repetitions can nest and concatenate.'],
    [(['3[a]2[bc]'],'Decode each group, then concatenate: aaa + bcbc = aaabcbc.'),
     (['3[a2[c]]'],'First 2[c] becomes cc, so the outer group is acc repeated three times: accaccacc.')],
    [[s] for s in ('a','abc','1[a]','2[a]','10[a]','12[ab]','2[abc]3[cd]ef',
                   'a2[b]c','2[2[a]]','2[a3[b]]','3[z]2[2[y]pq]','1[1[1[a]]]')],
    DECODE,[DECODE.replace('count = count*10+int(s[index])','count = int(s[index])'),
            "def decode_string(s):\n    import re\n    text = re.sub(r'([1-9][0-9]*)\\[([a-z]+)\\]',lambda m:int(m[1])*m[2],s)\n    return re.sub(r'[0-9\\[\\]]','',text)"],
    ['Overwrites rather than accumulates a multidigit repeat count.', 'Expands innermost groups only once, then discards still-unprocessed outer counts.'],
    decode_oracle,random_decode,
    ['A bracketed group has the same grammar as the whole string; recursion fits naturally.',
     'Let one parser consume characters up to the matching closing bracket and return that decoded section.',
     'Read all count digits, skip [, recursively parse the child, skip ], and append count copies. Append literal letters directly.',
     'One shared cursor ensures each bracket belongs to one level. Join pieces after parsing, and include expanded output size when analyzing cost.'],
    'The parser handles either a literal letter or a count followed by a bracketed subexpression. '
    'Recursive calls stop before their closing bracket so the caller can consume it. Counts need '
    'decimal accumulation, and separate groups concatenate. The grammar bounds recursion depth by '
    'the short encoded input. If n is encoded length, L decoded length, and d nesting depth, '
    'O(n+dL) is a conservative time bound for repeated string materialization, with O(n+L) space.',
    'O(n + dL)','O(n + L)',difficulty=5,
    stress=[(['100[100[aaaaaaaaaa]]'],'a'*100000),(['300[abc]'],'abc'*300)]),
395: entry('longest_repeating_substring',[('s','str'),('k','int')],'int',
    ['strings','divide-and-conquer','recursion'],
    ['1 <= s.length <= 10,000; s contains lowercase English letters only; 1 <= k <= 100,000.',
     'The substring is contiguous. Every distinct character within it must occur at least k times within that substring.'],
    [(['aaabb',3],'aaa is valid with three a characters. Including either b would require three b characters, so the answer is 3.'),
     (['ababbc',2],'ababb contains two a and three b characters. Adding c makes it invalid, so the answer is 5.')],
    [['a',1],['a',2],['abc',1],['abc',2],['aaaa',3],['abab',2],['aaabbbxaaab',3],
     ['aaabbbxbbaaa',3],['abaccc',2],['bbaaacbd',3],['aabbcc',2],['ababacb',3]],
    REPEATING,["def longest_repeating_substring(s,k):\n    from collections import Counter\n    return sum(count for count in Counter(s).values() if count>=k)",
               "def longest_repeating_substring(s,k):\n    from itertools import groupby\n    return max((n for _,group in groupby(s) if (n:=len(list(group)))>=k),default=0)"],
    ['Counts globally frequent characters across invalid separators instead of one contiguous substring.',
     'Finds only uniform runs, missing valid substrings containing several repeating characters.'],
    repeating_oracle,random_repeating,
    ['A character occurring fewer than k times in an interval cannot belong to a valid answer inside that interval.',
     'Split around every such character, then solve the resulting intervals independently.',
     'Count an interval. If every count reaches k, return its length; otherwise recursively inspect segments separated by under-frequency characters.',
     'Each level removes at least one character kind from descendant intervals. There are at most 26 lowercase character kinds, so recursion depth stays bounded.'],
    'A globally under-frequency character cannot reach k inside a smaller interval; it is a mandatory '
    'separator. Recompute frequencies inside each segment, because a character frequent in the '
    'parent may become scarce in a child. Use index intervals instead of copying substrings. '
    'For A distinct letters, intervals at one depth are disjoint and recursion depth is at most A. '
    'The reference uses O(An) time and O(A²) auxiliary counters/stack storage, with A <= 26.',
    'O(A n), A <= 26','O(A²)',difficulty=6,
    stress=[(['a'*10000,10000],10000),(['ab'*5000,5000],10000),
            (['a'*4999+'b'+'a'*5000,5000],5000),(['abc'*3333+'a',100000],0)]),
397: entry('integer_replacement',[('n','int')],'int',
    ['bit-manipulation','greedy','math'],
    ['1 <= n <= 2^31−1.', 'Even values must halve; odd values can increase or decrease by one. Count operations until reaching 1.',
     'Intermediate values may exceed 2^31−1; Python integers support this.'],
    [([8],'Only halving is needed: 8 → 4 → 2 → 1, for three operations.'),
     ([15],'Increasing first is better: 15 → 16 → 8 → 4 → 2 → 1 uses five operations; always decreasing would take six.')],
    [[n] for n in (1,2,3,4,5,6,7,9,10,11,13,17)],
    REPLACEMENT,[REPLACEMENT.replace('elif n == 3 or n & 3 == 1:','elif True:'),
                 REPLACEMENT.replace('elif n == 3 or n & 3 == 1:','elif n & 3 == 1:')],
    ['Always decreases odd values, missing faster routes through a power of two.',
     'Omits the n=3 exception and takes three operations instead of two.'],
    replacement_oracle,random_replacement,
    ['Even values have a forced next step. For odd values, consider the trailing binary digits.',
     'Usually choose the neighbor that creates more trailing zeros, allowing repeated halving.',
     'If even, halve. If n=3 or the low two bits are 01, subtract one; otherwise add one. Count each operation.',
     'The value 3 is special because subtracting reaches 2 then 1. Near 2^31−1, adding one is valid and produces a power of two.'],
    'After an odd adjustment, at least one halving follows. Except at 3, an ending 01 favors '
    'subtracting and an ending 11 favors adding; this removes a run of low one-bits and creates '
    'more forced halvings. The special value 3 reaches the target sooner by subtracting. '
    'The independent oracle explores both allowed choices with breadth-first search instead '
    'of relying on this bit rule. Each constant-size group of operations shortens the bit length.',
    'O(log n)','O(1)',difficulty=5,
    stress=[([n],replacement_oracle([n])) for n in (2**31-1,2**30,2**30-1,2**30+1)]),
402: entry('remove_k_digits',[('num','str'),('k','int')],'str',
    ['strings','stacks','greedy'],
    ['1 <= k <= num.length <= 100,000; num contains decimal digits only.',
     'The input has no leading zeros unless it is "0". Remove exactly k digits without reordering survivors.',
     'Return a decimal string with no leading zeros; an empty or all-zero result is "0".'],
    [(['1432219',3],'Remove 4, 3, and one 2 while preserving the remaining order, yielding 1219.'),
     (['10200',1],'Removing the leading 1 leaves 0200, which is normalized to the string "200".')],
    [['0',1],['1',1],['10',2],['10',1],['112',1],['123',1],['321',1],['111',2],
     ['1000',1],['1000',2],['10200',2],['765028',3]],
    DIGITS,[DIGITS.replace('stack[-1]>digit','stack[-1]>=digit'),
            DIGITS.replace('    if k:\n        del stack[-k:]\n','')],
    ['Deletes equal digits too early, consuming the budget before a later larger digit can be removed.',
     'Forgets to remove leftover digits from an increasing suffix.'],
    digits_oracle,random_digits,
    ['A smaller earlier digit improves the result more than any later digit.',
     'Maintain a nondecreasing stack, removing larger preceding digits while deletions remain.',
     'For each digit, pop larger stack tops while k>0, then append. Remove any leftover k digits from the end and strip leading zeros.',
     'Each digit is pushed and popped at most once. Preserve equal earlier digits, remove exactly k total, and avoid converting the huge number to an integer.'],
    'When a smaller digit arrives, removing a larger preceding digit improves the earliest '
    'possible position. A monotone stack applies this exchange greedily. If deletions remain, '
    'the remaining sequence is nondecreasing, so delete from its end. Normalize leading zeros '
    'only after the required deletions. All work stays on strings, supporting 100,000-digit inputs.',
    'O(n)','O(n)',difficulty=5,
    stress=[(['9'*50000+'0'*50000,50000],'0'),(['1'*100000,99999],'1'),
            (['123456789'*11111,99998],'1')]),
403: entry('can_cross',[('stones','list[int]')],'bool',
    ['dynamic-programming','graphs','recursion'],
    ['2 <= stones.length <= 2000; 0 <= stones[i] <= 2^31−1.',
     'Positions are strictly increasing and stones[0] is 0. The first jump must be exactly 1.',
     'After a jump of k, the next distance is k−1, k, or k+1, must be positive, and must land on a stone.'],
    [([[0,1,3,5,6,8,12,17]],'One route is 0 → 1 → 3 → 5 → 8 → 12 → 17, with jumps 1,2,2,3,4,5. Choosing the farthest possible stone can get stuck.'),
     ([[0,1,2,3,4,8,9,11]],'The early stones cannot build a jump large enough to bridge from 4 to 8; the final stone is unreachable.')],
    [[s] for s in ([0,1],[0,2],[0,1,2],[0,1,3],[0,1,4],[0,1,2,4],
                   [0,1,3,6,10],[0,1,3,6,11],[0,1,2,3,5,6,8],
                   [0,1,3,5,6,8,12],[0,1,2147483647],[0,2147483647])],
    FROG,[FROG.replace('(previous-1,previous,previous+1)','(previous-1,previous+1)'),
          '''
def can_cross(stones):
    available = set(stones)
    position = previous = 0
    while position != stones[-1]:
        options = [step for step in (previous-1,previous,previous+1) if step>0 and position+step in available]
        if not options:
            return False
        previous = max(options)
        position += previous
    return True
'''],
    ['Forbids repeating the previous jump distance, although equal consecutive jumps are legal.',
     'Greedily chooses the largest next jump and discards alternative routes.'],
    frog_oracle,random_frog,
    ['Reaching a stone is not enough information: the previous jump length determines what can happen next.',
     'Track reachable (stone position, last jump length) states.',
     'Start with (0,0). For each reachable state, try positive distances k−1, k, k+1 and add resulting states only for existing stones.',
     'Forward-only motion lets an iterative DP process stones in order. A memoized recursive search uses the same state but can exceed Python’s stack limit on a 2000-stone chain.'],
    'Associate each stone with all jump lengths that can reach it. Processing stones in increasing '
    'order is a topological traversal: every transition goes to a later stone, so its states are '
    'ready before it is processed. Starting with last jump 0 permits only the required first '
    'distance 1. Retain every feasible jump length, not just one per position. There are O(n²) '
    'possible states; the iterative reference avoids deep recursive calls at the 2000-stone limit.',
    'O(n²)','O(n²)',difficulty=8,
    stress=[([list(range(2000))],True),([[i*(i+1)//2 for i in range(2000)]],True),
            ([list(range(1999))+[2**31-1]],False)]),
408: entry('valid_word_abbreviation',[('word','str'),('abbr','str')],'bool',
    ['strings','two-pointers','parsing'],
    ['1 <= word.length <= 20; word contains lowercase English letters.',
     '1 <= abbr.length <= 10; abbr contains lowercase letters and digits; every integer token fits signed 32-bit.',
     'A numeric token skips that many letters. It must be positive and have no leading zero. The entire word must be consumed.'],
    [(['internationalization','i12iz4n'],'Keep i, skip 12 letters, keep iz, skip 4 letters, then keep n. This consumes exactly the 20-letter word.'),
     (['apple','a2e'],'After a and two skipped letters, the next letter is l, not e. The valid abbreviation a3e would skip three letters instead.')],
    [['a','a'],['a','1'],['a','0'],['a','01'],['apple','a3e'],['apple','5'],['apple','4'],
     ['apple','6'],['apple','a0pple'],['abcdefghij','10'],['abcdefghij','1b8'],['word','2147483647']],
    ABBREVIATION,[ABBREVIATION.replace("            if abbr[j]=='0':\n                return False\n",''),
                  ABBREVIATION.replace('return i==len(word)','return i<=len(word)')],
    ['Accepts zero or leading-zero skip tokens.', 'Accepts abbreviations that consume only a prefix of the word.'],
    abbreviation_oracle,random_abbreviation,
    ['Keep separate positions in the word and the abbreviation.',
     'A maximal run of digits is one skip count; a letter must match the current word position.',
     'Reject a numeric token starting with 0. Parse its full value, advance the word pointer, and reject overshoot. Require exact exhaustion at the end.',
     'Consecutive digits represent one number, not separate adjacent replacements. This is a validity query, unlike generating all possible abbreviations.'],
    'Scan each abbreviation token once. Literal letters advance both pointers only on a match; '
    'numeric tokens advance only the word pointer. Reject zero-prefixed counts and any overshoot. '
    'Finally require the word pointer to equal the word length. The independent oracle translates '
    'tokens to a full-match pattern; exhaustive small-mask tests additionally check the semantics '
    'against enumerated valid abbreviations.',
    'O(len(abbr))','O(1)',difficulty=3,
    stress=[(['a'*20,'20'],True),(['a'*20,'19a'],True),(['a'*20,'a18a'],True)])
}
BATCH[403]['prerequisites'] = ['recursion','dynamic-programming']
BATCH[388]['statement'] = (
    'A string describes an abstract filesystem: actual newline characters (\\n) separate entries, '
    'and each leading tab (\\t) increases the directory depth by one. Return the length of the '
    'longest absolute path to a file, including / separators, or 0 if there are no files. '
    'A dot distinguishes a filename from a directory name. Spaces inside names count. '
    'Process the supplied string only; do not inspect files on disk.')
BATCH[393]['statement'] = (
    'Check whether data can be partitioned into groups with these binary byte-prefix patterns: '
    '0xxxxxxx; 110xxxxx 10xxxxxx; 1110xxxx 10xxxxxx 10xxxxxx; or '
    '11110xxx 10xxxxxx 10xxxxxx 10xxxxxx. Return True exactly when every byte belongs to '
    'a complete valid group. This exercise checks these structural patterns only, not additional '
    'Unicode scalar-value or shortest-encoding restrictions.')
