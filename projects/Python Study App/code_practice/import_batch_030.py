"""Hard greedy merging, Euler itineraries, segment geometry and palindrome tries."""
from functools import lru_cache

from .import_batch_003 import entry


def maximum_number_oracle(args):
    left, right, length = args
    @lru_cache(None)
    def choose(i, j, remaining):
        if remaining == 0:
            return ()
        if len(left)-i + len(right)-j < remaining:
            return None
        candidates = []
        for p in range(i, len(left)):
            tail = choose(p+1, j, remaining-1)
            if tail is not None:
                candidates.append((left[p],) + tail)
        for q in range(j, len(right)):
            tail = choose(i, q+1, remaining-1)
            if tail is not None:
                candidates.append((right[q],) + tail)
        return max(candidates) if candidates else None
    return list(choose(0, 0, length))


def itinerary_oracle(args):
    tickets = args[0]
    @lru_cache(None)
    def visit(airport, remaining):
        if not remaining:
            return (airport,)
        answers = []
        for position, index in enumerate(remaining):
            origin, destination = tickets[index]
            if origin == airport:
                suffix = visit(destination, remaining[:position]+remaining[position+1:])
                if suffix is not None:
                    answers.append((airport,) + suffix)
        return min(answers) if answers else None
    result = visit('JFK', tuple(range(len(tickets))))
    if result is None:
        raise ValueError('Source requires at least one itinerary using every ticket')
    return list(result)


def crossing_oracle(args):
    """Compare every new closed axis-aligned segment with older nonadjacent ones."""
    directions = ((0,1),(-1,0),(0,-1),(1,0))
    segments = []
    x = y = 0
    for i, distance in enumerate(args[0]):
        dx, dy = directions[i%4]
        nx, ny = x+dx*distance, y+dy*distance
        segment = (min(x,nx), max(x,nx), min(y,ny), max(y,ny))
        for left, right, bottom, top in segments[:-1]:
            if (max(segment[0],left) <= min(segment[1],right)
                    and max(segment[2],bottom) <= min(segment[3],top)):
                return True
        segments.append(segment)
        x, y = nx, ny
    return False


def palindrome_pairs_oracle(args):
    words = args[0]
    return [[i,j] for i,left in enumerate(words) for j,right in enumerate(words)
            if i != j and (combined := left+right) == combined[::-1]]


def random_maximum_number(rng):
    arrays = [[rng.randint(1,9)] + [rng.randint(0,9) for _ in range(rng.randint(0,4))]
              for _ in range(2)]
    return [*arrays, rng.randint(1, sum(map(len, arrays)))]


def random_itinerary(rng):
    airports = ['JFK','AAA','BBB','CCC']
    current, tickets = 'JFK', []
    for _ in range(rng.randint(1,8)):
        destination = rng.choice([name for name in airports if name != current])
        tickets.append([current,destination])
        current = destination
    rng.shuffle(tickets)
    return [tickets]


def random_crossing(rng):
    return [[rng.randint(1,12) for _ in range(rng.randint(1,12))]]


def random_palindrome_pairs(rng):
    count = rng.randint(1,8)
    words = set()
    while len(words) < count:
        words.add(''.join(rng.choice('abc') for _ in range(rng.randint(0,5))))
    return [sorted(words)]


MAXIMUM_NUMBER = '''\
def create_maximum_number(nums1, nums2, k):
    def select(values, count):
        drop = len(values)-count
        stack = []
        for value in values:
            while drop and stack and stack[-1] < value:
                stack.pop()
                drop -= 1
            stack.append(value)
        return ''.join(str(value) for value in stack[:count])
    best = ''
    for count in range(max(0,k-len(nums2)), min(k,len(nums1))+1):
        left, right = select(nums1,count), select(nums2,k-count)
        merged = []
        while left or right:
            if left > right:
                merged.append(left[0])
                left = left[1:]
            else:
                merged.append(right[0])
                right = right[1:]
        best = max(best, ''.join(merged))
    return [int(digit) for digit in best]
'''

ITINERARY = '''\
def reconstruct_itinerary(tickets):
    graph = {}
    for origin, destination in sorted(tickets, reverse=True):
        graph.setdefault(origin, []).append(destination)
    stack, reverse_route = ['JFK'], []
    while stack:
        airport = stack[-1]
        if graph.get(airport):
            stack.append(graph[airport].pop())
        else:
            reverse_route.append(stack.pop())
    return reverse_route[::-1]
'''

CROSSING = '''\
def is_self_crossing(distance):
    d = distance
    for i in range(3,len(d)):
        if d[i] >= d[i-2] and d[i-1] <= d[i-3]:
            return True
        if i >= 4 and d[i-1] == d[i-3] and d[i]+d[i-4] >= d[i-2]:
            return True
        if (i >= 5 and d[i-2] >= d[i-4] and d[i]+d[i-4] >= d[i-2]
                and d[i-1] <= d[i-3] and d[i-1]+d[i-5] >= d[i-3]):
            return True
    return False
'''

PALINDROME_PAIRS = '''\
def palindrome_pairs(words):
    def prefix_palindromes(text):
        joined = text + '#' + text[::-1]
        failure = [0]*len(joined)
        for i in range(1,len(joined)):
            j = failure[i-1]
            while j and joined[i] != joined[j]:
                j = failure[j-1]
            if joined[i] == joined[j]:
                j += 1
            failure[i] = j
        flags = [False]*(len(text)+1)
        flags[0] = True
        length = failure[-1]
        while length:
            flags[length] = True
            length = failure[length-1]
        return flags
    # Each trie node stores children, an exact word index, and indices whose
    # unconsumed original prefix is palindromic at this node.
    children, ends, palindromic = [{}], [-1], [[]]
    suffix_flags = []
    for word_index, word in enumerate(words):
        prefixes = prefix_palindromes(word)
        suffix_flags.append(prefix_palindromes(word[::-1]))
        node = 0
        for j in range(len(word)-1,-1,-1):
            if prefixes[j+1]:
                palindromic[node].append(word_index)
            letter = word[j]
            if letter not in children[node]:
                children[node][letter] = len(children)
                children.append({})
                ends.append(-1)
                palindromic.append([])
            node = children[node][letter]
        ends[node] = word_index
        palindromic[node].append(word_index)
    result = []
    for i, word in enumerate(words):
        node = 0
        for j, letter in enumerate(word):
            other = ends[node]
            if other != -1 and other != i and suffix_flags[i][len(word)-j]:
                result.append([i,other])
            if letter not in children[node]:
                break
            node = children[node][letter]
        else:
            for other in palindromic[node]:
                if other != i:
                    result.append([i,other])
    return result
'''

SORT_ALL_DIGITS = '''\
def create_maximum_number(nums1, nums2, k):
    return sorted(nums1+nums2, reverse=True)[:k]
'''
FIRST_DIGIT_TIE = MAXIMUM_NUMBER.replace('if left > right:', 'if left[:1] >= right[:1]:')
GREEDY_ITINERARY = '''\
def reconstruct_itinerary(tickets):
    graph = {}
    for origin,destination in sorted(tickets, reverse=True):
        graph.setdefault(origin,[]).append(destination)
    route = ['JFK']
    while graph.get(route[-1]):
        route.append(graph[route[-1]].pop())
    return route
'''
DEDUP_ITINERARY = ITINERARY.replace('sorted(tickets, reverse=True)', 'sorted(set(map(tuple,tickets)), reverse=True)')
ONLY_SIMPLE_CROSSING = '''\
def is_self_crossing(distance):
    return any(distance[i] >= distance[i-2] and distance[i-1] <= distance[i-3]
               for i in range(3,len(distance)))
'''
STRICT_CROSSING = CROSSING.replace('>=', '>').replace('<=', '<')
REVERSE_ONLY_PAIRS = '''\
def palindrome_pairs(words):
    lookup = {word:i for i,word in enumerate(words)}
    return [[i,lookup[word[::-1]]] for i,word in enumerate(words)
            if word[::-1] in lookup and lookup[word[::-1]] != i]
'''
UNORDERED_INDEX_PAIRS = PALINDROME_PAIRS.replace('    return result', '    return [[i,j] for i,j in result if i < j]')


def code3(number):
    return ''.join(chr(ord('a') + digit) for digit in (number//676,number//26%26,number%26))


airport_path = ['JFK'] + [code3(i).upper() for i in range(300)]
large_words = ['a'+code3(i)+'x'*295+'b' for i in range(5000)]
paired_words = ['a'+code3(i)+'b' for i in range(2500)]
paired_words += [word[::-1] for word in paired_words[:]]
paired_expected = [[i,i+2500] for i in range(2500)] + [[i+2500,i] for i in range(2500)]

BATCH = {
    321: entry('create_maximum_number',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'list[int]',
        ['greedy','stacks','strings','arrays'],
        ['nums1 and nums2 each contain 1–500 digits from 0 through 9, without leading zeros; 1 <= k <= len(nums1)+len(nums2).',
         'Choose exactly k digits in total. You may interleave the arrays freely, but must preserve the order of the chosen digits from EACH array. Return the lexicographically largest length-k digit list.'],
        [([[3,4,6,5],[9,1,2,5,8,3],5],'Choose [6,5] from nums1 and [9,8,3] from nums2, then interleave them as [9,8,6,5,3]. Both within-array orders are preserved.'),
         ([[6,0,4],[6,7],5],'Both next digits are 6, but the suffix [6,7] is larger than [6,0,4]. Take it first to obtain [6,7,6,0,4].')],
        [[a,b,k] for a,b,k in (([1],[2],1),([1],[2],2),([0],[0],1),([9],[1,2],2),
            ([3,9],[8,9],3),([6,7],[6,0,4],5),([8,1,9],[8,2],4),([9,0,1],[8,9],3),
            ([1,2,3],[4,5,6],3),([9,8],[7,6],4),([1,1],[1,1],3),([9,1],[9,0],3),
            ([2,5,6,4],[4,3,8],5),([7,0,0],[7,0,1],6))],
        MAXIMUM_NUMBER,[SORT_ALL_DIGITS,FIRST_DIGIT_TIE],
        ['Sorts the chosen digits globally, violating their original within-array order.', 'Breaks equal-leading-digit ties without comparing the remaining suffixes.'],
        maximum_number_oracle,random_maximum_number,
        ['Try each feasible split of the k selected digits between the two arrays.',
         'For a fixed split, use a monotone stack to choose the largest subsequence of the required length from each array.',
         'Merge those subsequences by comparing their entire remaining suffixes, not just their first digits; keep the best merge across splits.',
         'A removal budget controls each stack. Equal heads require looking ahead; if one suffix is a prefix of the other, the longer suffix is larger.'],
        'Every answer has some allocation of selected positions to the two inputs. For each allocation, greedily deleting a smaller earlier digit when enough positions remain yields each largest fixed-length subsequence. The maximal interleaving always consumes from the lexicographically larger remaining suffix; comparing only the first digit fails on ties. Enumerate feasible allocations and keep the greatest resulting list. The oracle directly enumerates every legal next index in either array with memoization, independently of split selection and greedy merging.',
        'O(s*(m+n+k^2)), s = feasible split count','O(m+n+k)',difficulty=8,
        stress=[([[9]*500,[9]*500,500],[9]*500),([[9]*500,[8]*500,1000],[9]*500+[8]*500),
                ([[1]+[0]*499,[9]+[0]*499,1],[9])]),
    332: entry('reconstruct_itinerary',[('tickets','list[list[str]]')],'list[str]',
        ['graphs','recursion','depth-first-search','eulerian-path'],
        ['1–300 tickets; each [origin,destination] contains two different three-uppercase-letter airport codes.',
         'Start at JFK and use EVERY ticket occurrence exactly once. Repeated tickets are separate flights. At least one complete itinerary exists; return the lexicographically smallest complete airport sequence.'],
        [([[['MUC','LHR'],['JFK','MUC'],['SFO','SJC'],['LHR','SFO']]],'The tickets form JFK→MUC→LHR→SFO→SJC; all four flights are used once.'),
         ([[['JFK','KUL'],['JFK','NRT'],['NRT','JFK']]],'JFK→KUL is alphabetically first but ends too early. The complete route must be JFK→NRT→JFK→KUL.')],
        [[tickets] for tickets in ([['JFK','AAA']], [['JFK','AAA'],['AAA','JFK']],
            [['JFK','BBB'],['BBB','CCC']], [['JFK','AAA'],['JFK','AAA'],['AAA','JFK']],
            [['JFK','AAA'],['AAA','JFK'],['JFK','BBB'],['BBB','JFK']],
            [['JFK','SFO'],['JFK','ATL'],['SFO','ATL'],['ATL','JFK'],['ATL','SFO']],
            [['JFK','BBB'],['BBB','AAA'],['AAA','BBB'],['BBB','JFK']],
            [['AAA','BBB'],['JFK','AAA'],['BBB','CCC']],
            [['JFK','AAA'],['AAA','BBB'],['BBB','AAA'],['AAA','CCC']],
            [['JFK','AAA'],['AAA','JFK'],['JFK','AAA'],['AAA','JFK']],
            [['JFK','ZZZ'],['ZZZ','YYY'],['YYY','JFK']],
            [['JFK','AAA'],['AAA','BBB'],['BBB','JFK'],['JFK','CCC']])],
        ITINERARY,[GREEDY_ITINERARY,DEDUP_ITINERARY],
        ['Commits the first lexicographically small flight even if it strands unused tickets.', 'Collapses repeated ticket occurrences into one edge and cannot use all flights.'],
        itinerary_oracle,random_itinerary,
        ['Tickets are directed edges; the route must traverse every edge once, including duplicate edges.',
         'Use an Euler-trail construction. Explore smallest destinations first, but record an airport only after all outgoing edges are consumed.',
         'Keep a stack starting at JFK. Push the smallest unused outgoing destination; if none remains, pop into a reverse route. Reverse at the end.',
         'Sorting destination lists in reverse order lets pop() take the smallest. Postorder places dead ends at the end instead of prematurely committing them.'],
        'Hierholzer traversal consumes each ticket once and joins cycles through postorder. Exploring destinations in lexical order produces the smallest complete Euler trail, while reversing the finished-node list moves unavoidable dead ends to their proper final positions. Duplicate list entries represent distinct edges and must remain. The oracle independently tries all legal remaining-ticket choices and selects the minimum complete route.',
        'O(e log e)','O(e)',difficulty=8,
        stress=[([[['JFK','AAA'],['AAA','JFK']]*150],['JFK']+['AAA','JFK']*150),
                ([[[a,b] for a,b in zip(airport_path,airport_path[1:])]],airport_path)]),
    335: entry('is_self_crossing',[('distance','list[int]')],'bool',
        ['geometry','arrays','math'],
        ['1 <= len(distance) <= 100000; 1 <= distance[i] <= 100000.',
         'Start at (0,0) and move north, west, south, east, repeating. Return whether a segment crosses, overlaps, or touches a NONADJACENT earlier segment. The shared endpoint of consecutive moves alone does not count.'],
        [([[2,1,1,2]],'The fourth move runs east from (-1,1) to (1,1), crossing the first vertical segment at (0,1). Return true.'),
         ([[1,2,3,4]],'Each turn continues an outward-expanding path, with no intersection or touch of an older nonadjacent segment. Return false.')],
        [[values] for values in ([1],[1,1],[1,1,1],[1,1,1,1],[1,1,2,1,1],
            [1,1,2,2,1,1],[3,3,4,2,2],[2,2,3,3,2,2],[1,2,3,4,5,6],
            [5,4,3,2,1],[2,1,2,1],[1,1,1,2,1],[3,2,2,3],[1,2,3,4,2,2])],
        CROSSING,[ONLY_SIMPLE_CROSSING,STRICT_CROSSING],
        ['Checks only a crossing with the third previous segment, missing overlap and inward-spiral crossings.', 'Uses strict inequalities and fails when the path merely touches or overlaps an earlier segment.'],
        crossing_oracle,random_crossing,
        ['With a fixed counter-clockwise turn order, the first crossing has only a few local configurations.',
         'Check the segment three moves earlier, the collinear segment four moves earlier, and the inward-spiral segment five moves earlier.',
         'For i>=3 check d[i]>=d[i-2] and d[i-1]<=d[i-3]. Add the i>=4 overlap and i>=5 inward-transition inequalities.',
         'Touching counts, so use inclusive comparisons. Only the last six lengths are needed, giving linear time and constant extra space.'],
        'Before the first intersection, an outward spiral may continue expanding or transition inward. The next crossing can meet one of the three relevant nonadjacent segments: i-3, i-4 (collinear overlap), or i-5 (inward transition). Coordinate inequalities for these cases yield the three constant-time tests in the reference. Endpoints are included. The oracle constructs actual closed axis-aligned segments and compares every nonadjacent pair without using these local cases.',
        'O(n)','O(1)',difficulty=8,
        stress=[([list(range(1,100001))],False),([[100000]*100000],True)]),
    336: entry('palindrome_pairs',[('words','list[str]')],'list[list[int]]',
        ['strings','tries','palindromes','string-matching'],
        ['1 <= len(words) <= 5000; all words are distinct; each has 0–300 lowercase English letters.',
         'Return every ordered pair [i,j] with i != j such that words[i]+words[j] is a palindrome. Pair order in the answer is arbitrary; the two orders of indices are separate answers. An empty word is allowed.',
         'Target linear work in total input characters plus produced pairs; avoid checking every possible word pair or rescanning every substring for palindromes.'],
        [([['abcd','dcba','lls','s','sssll']],'The four ordered pairs are [0,1],[1,0],[3,2],[2,4], yielding abcddcba, dcbaabcd, slls, and llssssll.'),
         ([['a','']],'Both a+empty and empty+a equal the palindrome a, so return both [0,1] and [1,0]. Self-pairs are forbidden.')],
        [[words] for words in ([''],['a'],['ab','ba'],['bat','tab','cat'],['a','b','c'],
            ['aa','a',''],['abc','cba','bc','cb'],['a','aa','aaa'],['ab','b','ba'],
            ['abcd','dcba'],['lls','s','sssll'],['aba','xyz',''],['aa','bb'],['ab','cd'])],
        PALINDROME_PAIRS,[REVERSE_ONLY_PAIRS,UNORDERED_INDEX_PAIRS],
        ['Finds only exact reversed words, missing pairs with a palindromic unmatched prefix or suffix.', 'Keeps only i<j even though ordered pairs in both directions may be valid.'],
        palindrome_pairs_oracle,random_palindrome_pairs,
        ['A shorter word can match the reverse of part of a longer word when the unmatched part is a palindrome.',
         'Insert reversed words into a trie. At each node remember which words have a palindromic prefix still unconsumed.',
         'While querying a word, an earlier terminal matches if the remaining suffix is palindromic. After consuming the word, emit stored palindromic remainders. Exclude the same index.',
         'Precompute all palindromic prefix/suffix lengths in linear time using KMP on text+# + reversed(text), following its failure-link chain. Empty strings work at the trie root.'],
        'A reversed-word trie shares comparisons across candidate partners. If a partner ends first, the remainder of the query must be a palindrome; if the query ends first, the unconsumed original partner prefix must be a palindrome. Precomputed boundary flags make each check constant-time. The KMP border chain of text+# + reverse(text) identifies every palindromic prefix without substring rescans; reverse the text to obtain suffix flags. Each input character creates at most one trie node and contributes bounded annotations. Including emitted pairs, time and space are O(S+w+p), where S is total characters, w is word count, and p is result size. The independent oracle directly concatenates every ordered pair and checks reversal.',
        'O(S+w+p), input characters S, word count w, output pairs p','O(S+w+p)',difficulty=8,
        stress=[([large_words],[]),([paired_words],paired_expected),([['a'*300,'']],[[0,1],[1,0]])]),
}
BATCH[336]['comparator'] = 'unordered'
for source_id, prerequisites in {321:['arrays','stacks'],332:['graphs','recursion'],335:['arrays','math'],336:['strings','string-matching']}.items():
    BATCH[source_id]['prerequisites'] = prerequisites
