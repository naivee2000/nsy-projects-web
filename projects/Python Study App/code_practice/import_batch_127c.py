"""Third slice of workbook batch 127: strings, arithmetic, and graph components."""

from itertools import combinations

from .import_batch_055 import entry


def greatest_letter_oracle(args):
    (text,) = args
    candidates = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  if letter in text and letter.lower() in text]
    return candidates[-1] if candidates else ''


def random_greatest_letter(rng):
    alphabet = 'abcxyzABCXYZ012'
    return [''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 24)))]


def units_oracle(args):
    number, digit = args
    if number == 0:
        return 0
    allowed = [value for value in range(1, number + 1) if value % 10 == digit]
    possible = [False] * (number + 1); possible[0] = True
    best = [number + 1] * (number + 1); best[0] = 0
    for total in range(1, number + 1):
        for value in allowed:
            if value > total:
                break
            if possible[total - value]:
                possible[total] = True
                best[total] = min(best[total], best[total - value] + 1)
    return best[number] if possible[number] else -1


def random_units(rng):
    return [rng.randint(0, 200), rng.randint(0, 9)]


def binary_subsequence_oracle(args):
    text, limit = args; best = 0
    for length in range(1, len(text) + 1):
        if any(int(''.join(text[index] for index in chosen), 2) <= limit
               for chosen in combinations(range(len(text)), length)):
            best = length
    return best


def random_binary_subsequence(rng):
    return [''.join(rng.choice('01') for _ in range(rng.randint(1, 12))), rng.randint(0, 80)]


def asterisk_oracle(args):
    (text,) = args; inside = False; count = 0
    for char in text:
        if char == '|': inside = not inside
        elif char == '*' and not inside: count += 1
    return count


def random_asterisks(rng):
    groups = rng.randint(0, 5); pieces = []
    for _ in range(groups):
        pieces += [''.join(rng.choice('ab*') for _ in range(rng.randint(0, 5))), '|',
                   ''.join(rng.choice('ab*') for _ in range(rng.randint(0, 5))), '|']
    pieces.append(''.join(rng.choice('ab*') for _ in range(rng.randint(0, 7))))
    return [''.join(pieces)]


def unreachable_oracle(args):
    n, edges = args; linked = {tuple(sorted(edge)) for edge in edges}; total = 0
    for start in range(n):
        seen = {start}; stack = [start]
        while stack:
            node = stack.pop()
            for other in range(n):
                if other not in seen and tuple(sorted((node, other))) in linked:
                    seen.add(other); stack.append(other)
        total += sum(other not in seen for other in range(start + 1, n))
    return total


def random_unreachable(rng):
    n = rng.randint(1, 10)
    edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.25]
    return [n, edges]


GREATEST = '''\
def greatest_bilingual_english_letter(s):
    present=set(s)
    for letter in reversed('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        if letter in present and letter.lower() in present:return letter
    return ''
'''

UNITS = '''\
def minimum_count_with_units_digit(num,k):
    if num==0:return 0
    for count in range(1,11):
        if count*k<=num and (count*k-num)%10==0:return count
    return -1
'''

BINARY = '''\
def longest_binary_subsequence_at_most(s,k):
    answer=s.count('0');value=0;place=1
    for char in reversed(s):
        if char=='1' and value+place<=k:answer+=1;value+=place
        if place<=k:place*=2
    return answer
'''

ASTERISKS = '''\
def count_asterisks_outside_bars(s):
    return sum(part.count('*') for part in s.split('|')[::2])
'''

UNREACHABLE = '''\
def count_unreachable_node_pairs(n,edges):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    seen=set();remaining=n;answer=0
    for start in range(n):
        if start in seen:continue
        stack=[start];seen.add(start);size=0
        while stack:
            node=stack.pop();size+=1
            for neighbor in graph[node]:
                if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
        remaining-=size;answer+=size*remaining
    return answer
'''


BATCH = {
    2309: entry('greatest_bilingual_english_letter',[('s','str')],'str',['strings','hash sets'],['A letter qualifies only when both its uppercase and lowercase forms occur.','Return the alphabetically greatest qualifying uppercase letter, or an empty string if none qualifies.','Nonletter characters do not qualify.'],[(['lEeTcOdE'],'E is the greatest letter appearing in both cases.'),(['abcXYZ'],'No letter appears in both cases, so the result is empty.')],[[s] for s in ['aA','zZ','AaZz','abcABC','xYyX','A','a','1aA2','bBcC','mnopMNOP','qQrRsS','ZZzz','aAz','HelloWORLDworld','0']],GREATEST,[GREATEST.replace("reversed('ABCDEFGHIJKLMNOPQRSTUVWXYZ')","'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"),GREATEST.replace("and letter.lower() in present",'')],['Returns the smallest qualifying letter instead of the greatest.','Checks only uppercase presence and ignores the required lowercase form.'],greatest_letter_oracle,random_greatest_letter,['Put every character in a set.','Inspect uppercase letters from Z down to A.','Return the first letter whose uppercase and lowercase forms are both present.','Descending inspection makes the first qualifying letter exactly the greatest one.'],'O(n)','O(1)',3),
    2310: entry('minimum_count_with_units_digit',[('num','int'),('k','int')],'int',['math','enumeration'],['Choose any positive integers whose decimal units digit is k; values may repeat.','Return the minimum count whose sum is num, or -1 when impossible.','The empty selection is allowed only when num is zero.'],[([58,9],'Two valid numbers such as 9 and 49 sum to fifty-eight.'),([37,2],'No count can have both a units-digit sum ending in seven and a total at most thirty-seven.')],[[n,k] for n,k in [(0,0),(0,7),(1,1),(1,0),(10,0),(10,1),(10,5),(11,1),(20,0),(20,2),(27,9),(9,9),(8,4),(100,0),(3,7)]],UNITS,[UNITS.replace('range(1,11)','range(1,10)'),UNITS.replace('count*k<=num and ','')],['Never considers ten chosen values, which is sometimes the first feasible count.','Checks only the last digit and may claim a count whose minimum possible sum exceeds num.'],units_oracle,random_units,['Only the chosen count and k determine the sum units digit.','Try counts one through ten; decimal residues repeat after ten.','A count works when count*k is no greater than num and has the same residue modulo ten.','Any remaining difference is a nonnegative multiple of ten and can be added to one chosen number without changing its units digit.'],'O(1)','O(1)',5),
    2311: entry('longest_binary_subsequence_at_most',[('s','str'),('k','int')],'int',['strings','greedy','bit manipulation'],['Choose a subsequence while preserving character order.','Interpret the chosen bits as a binary integer; leading zeroes are allowed.','Return the maximum subsequence length whose value is at most k.'],[(['1001010',5],'All zeroes plus selected low-place one bits form a length-five value no greater than five.'),(['00101001',1],'Five zeroes and the final one form a valid length-six subsequence.')],[[s,k] for s,k in [('0',0),('1',0),('1',1),('0000',0),('1111',3),('101',5),('101',4),('100000',1),('010101',2),('111000',7),('0011',2),('10',1),('1010101010',10),('0001000',0)]],BINARY,[BINARY.replace("answer=s.count('0')",'answer=0'),BINARY.replace("if char=='1' and value+place<=k","if char=='1' and value+place<k")],['Discards leading zeroes even though they add length without increasing value.','Rejects a bit when it makes the value exactly equal to k.'],binary_subsequence_oracle,random_binary_subsequence,['Every zero can be included because leading zeroes do not increase the value.','The cheapest one bits are at the rightmost positions, so inspect bits from right to left.','Include a one only when adding its place value keeps the total at most k; count all zeroes.','Exchanging any selected higher-place one for an available lower-place one cannot increase value, proving the greedy choice.'],'O(n)','O(1)',6),
    2315: entry('count_asterisks_outside_bars',[('s','str')],'int',['strings','simulation'],['Vertical bars occur in matched pairs.','Characters between each first and second bar of a pair are excluded.','Count asterisks outside all excluded regions.'],[(['l|*e*et|c**o|*de|'],'The two stars inside each barred region are ignored and two outside stars remain.'),(['iamprogrammer'],'There are no asterisks, so the count is zero.')],[[s] for s in ['*','|*|','*|*|*','a*b','||','|abc|**','**|**|','a|b*c|d*','|*||*|','***|a|b','a|*|b|**|c','no-stars','|inside|','x*y|z|*','a||*']],ASTERISKS,[ASTERISKS.replace("[::2]",'[1::2]'),ASTERISKS.replace("s.split('|')",'s')],['Counts the barred segments instead of the unbarred segments.','Iterates individual characters and calls count on each, including stars inside bars.'],asterisk_oracle,random_asterisks,['Splitting at each bar alternates outside and inside regions.','Outside regions have even indexes in the split result.','Count stars only in slices zero, two, four, and so on.','Matched bars guarantee the parity alternation is exact across the entire string.'],'O(n)','O(n)',3),
    2316: entry('count_unreachable_node_pairs',[('n','int'),('edges','list[list[int]]')],'int',['graphs','connected components'],['Nodes are numbered zero through n-1 and edges are undirected.','A pair is unreachable when its two nodes belong to different connected components.','Count each unordered pair once.'],[([3,[[0,1],[0,2],[1,2]]],'Every node is connected, so there are no unreachable pairs.'),([7,[[0,2],[0,5],[2,4],[1,6],[5,4]]],'The component sizes are four, two, and one, producing fourteen unreachable pairs.')],[[n,e] for n,e in [(1,[]),(2,[]),(2,[[0,1]]),(3,[]),(4,[[0,1]]),(4,[[0,1],[2,3]]),(5,[[0,1],[1,2]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(6,[[0,1],[0,2],[3,4]]),(6,[[0,1],[1,2],[0,2]]),(7,[[0,1],[2,3],[4,5]]),(8,[[0,1],[1,2],[3,4],[5,6],[6,7]]),(4,[[0,1],[0,2]]),(10,[])]],UNREACHABLE,[UNREACHABLE.replace('answer+=size*remaining','answer+=size*(remaining-size)'),UNREACHABLE.replace('remaining-=size;answer+=size*remaining','answer+=size*remaining;remaining-=size')],['Subtracts the component twice before counting its cross-component pairs.','Counts against nodes that still include the current component, adding reachable and self pairs.'],unreachable_oracle,random_unreachable,['Find every connected-component size with DFS or BFS.','After finding a component, pair its nodes only with nodes in components not processed yet.','Subtract size from remaining, then add size*remaining.','Each cross-component unordered pair is counted exactly when its earlier component is completed.'],'O(n+edges)','O(n+edges)',5),
}
