"""Character paths, repeated runs, coprime arrangements, state search, and chess rays."""
from collections import deque

from .import_batch_055 import entry


def conversion_oracle(args):
    source, target, original, changed, costs = args
    graph = {char: [] for char in 'abcdefghijklmnopqrstuvwxyz'}
    for left, right, cost in zip(original, changed, costs):
        graph[left].append((right, cost))

    def shortest(start, goal):
        distances = {start: 0}; unused = set(graph)
        while unused:
            current = min(unused, key=lambda char: distances.get(char, float('inf')))
            unused.remove(current)
            if current == goal:
                return distances[current]
            if current not in distances:
                break
            for following, price in graph[current]:
                candidate = distances[current] + price
                if candidate < distances.get(following, float('inf')):
                    distances[following] = candidate
        return None

    total = 0
    for left, right in zip(source, target):
        if left == right:
            continue
        price = shortest(left, right)
        if price is None:
            return -1
        total += price
    return total


def random_conversion(rng):
    alphabet = 'abcde'; size = rng.randint(1, 12)
    source = ''.join(rng.choice(alphabet) for _ in range(size))
    target = ''.join(rng.choice(alphabet) for _ in range(size))
    edges = [(left, right) for left in alphabet for right in alphabet if left != right]
    rng.shuffle(edges); edges = edges[:rng.randint(1, len(edges))]
    return [source, target, [a for a, _ in edges], [b for _, b in edges],
            [rng.randint(1, 20) for _ in edges]]


def special_oracle(args):
    text = args[0]; counts = {}; answer = -1
    for left in range(len(text)):
        for right in range(left, len(text)):
            piece = text[left:right + 1]
            if len(set(piece)) == 1:
                counts[piece] = counts.get(piece, 0) + 1
                if counts[piece] >= 3:
                    answer = max(answer, len(piece))
    return answer


def random_special(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(3, 24)))]


def permutations_oracle(args):
    from math import gcd
    size = args[0]; ways = [0] * (1 << size); ways[0] = 1
    for mask in range(1 << size):
        position = mask.bit_count() + 1
        for value in range(1, size + 1):
            bit = 1 << (value - 1)
            if not mask & bit and gcd(position, value) == 1:
                ways[mask | bit] += ways[mask]
    return ways[-1]


def random_permutations(rng):
    return [rng.randint(1, 12)]


def operations_oracle(args):
    start, target = args
    bound = 2 * max(start, target) + 11
    queue = deque([(start, 0)]); seen = {start}
    while queue:
        value, distance = queue.popleft()
        if value == target:
            return distance
        following = [value - 1, value + 1]
        if value % 5 == 0:
            following.append(value // 5)
        if value % 11 == 0:
            following.append(value // 11)
        for candidate in following:
            if 1 <= candidate <= bound and candidate not in seen:
                seen.add(candidate); queue.append((candidate, distance + 1))


def random_operations(rng):
    return [rng.randint(1, 180), rng.randint(1, 180)]


def chess_oracle(args):
    rook = tuple(args[:2]); bishop = tuple(args[2:4]); queen = tuple(args[4:])

    def attacks(piece, blocker, directions):
        for row_step, column_step in directions:
            row, column = piece
            while True:
                row += row_step; column += column_step
                if not (1 <= row <= 8 and 1 <= column <= 8):
                    break
                square = (row, column)
                if square == blocker:
                    break
                if square == queen:
                    return True
        return False

    if attacks(rook, bishop, ((1, 0), (-1, 0), (0, 1), (0, -1))):
        return 1
    if attacks(bishop, rook, ((1, 1), (1, -1), (-1, 1), (-1, -1))):
        return 1
    return 2


def random_chess(rng):
    squares = rng.sample([(row, column) for row in range(1, 9) for column in range(1, 9)], 3)
    return [coordinate for square in squares for coordinate in square]


CONVERSION = '''def minimum_character_conversion_cost(source,target,original,changed,cost):
    infinity=float('inf');distance=[[infinity]*26 for _ in range(26)]
    for letter in range(26):distance[letter][letter]=0
    for left,right,price in zip(original,changed,cost):
        a=ord(left)-97;b=ord(right)-97;distance[a][b]=min(distance[a][b],price)
    for middle in range(26):
        for left in range(26):
            for right in range(26):
                distance[left][right]=min(distance[left][right],distance[left][middle]+distance[middle][right])
    answer=0
    for left,right in zip(source,target):
        price=distance[ord(left)-97][ord(right)-97]
        if price==infinity:return -1
        answer+=price
    return answer
'''


SPECIAL = '''def longest_thrice_special_substring(s):
    runs={}
    start=0
    while start<len(s):
        end=start+1
        while end<len(s) and s[end]==s[start]:end+=1
        runs.setdefault(s[start],[]).append(end-start);start=end
    answer=-1
    for lengths in runs.values():
        for size in range(1,max(lengths)+1):
            if sum(max(0,length-size+1) for length in lengths)>=3:answer=max(answer,size)
    return answer
'''


PERMUTATIONS = '''def count_self_divisible_permutations(n):
    from functools import lru_cache
    from math import gcd
    @lru_cache(None)
    def search(mask):
        position=mask.bit_count()+1
        if position>n:return 1
        return sum(search(mask|(1<<(value-1))) for value in range(1,n+1) if not mask&(1<<(value-1)) and gcd(position,value)==1)
    return search(0)
'''


OPERATIONS = '''def minimum_operations_to_equal(x,y):
    from functools import lru_cache
    @lru_cache(None)
    def solve(value):
        if value<=y:return y-value
        answer=value-y
        for divisor in (5,11):
            remainder=value%divisor
            answer=min(answer,remainder+1+solve(value//divisor))
            answer=min(answer,divisor-remainder+1+solve(value//divisor+1))
        return answer
    return solve(x)
'''


CHESS = '''def minimum_queen_capture_moves(a,b,c,d,e,f):
    rook_clear_row=a==e and not (c==a and min(b,f)<d<max(b,f))
    rook_clear_column=b==f and not (d==b and min(a,e)<c<max(a,e))
    bishop_aligned=abs(c-e)==abs(d-f)
    bishop_blocked=abs(a-e)==abs(b-f) and abs(a-c)==abs(b-d) and min(c,e)<a<max(c,e)
    return 1 if rook_clear_row or rook_clear_column or (bishop_aligned and not bishop_blocked) else 2
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
2976: entry('minimum_character_conversion_cost',[('source','str'),('target','str'),('original','list[str]'),('changed','list[str]'),('cost','list[int]')],'int',['graphs','shortest paths','strings'],['source and target are equal-length lowercase strings.','Each listed directed character conversion may be used any number of times; duplicate rules may have different costs.','Return the minimum total position-wise conversion cost, or -1 if any position is unreachable.'],[(['abcd','acbe',['a','b','c','c','e','d'],['b','c','b','e','b','e'],[2,5,5,1,2,20]],'The cheapest position costs are zero, five, three through c→e→b, and twenty, totaling twenty-eight.'),(['aaaa','bbbb',['a','c'],['c','b'],[1,2]],'Each a follows the two-edge path a→c→b for three, so four positions cost twelve.')],[[s,t,o,c,p] for s,t,o,c,p in [('a','a',['a'],['b'],[5]),('a','b',['a'],['b'],[5]),('a','c',['a','b'],['b','c'],[2,3]),('a','d',['a','b'],['b','c'],[1,1]),('abc','abc',['a'],['b'],[1]),('abc','bca',['a','b','c'],['b','c','a'],[1,2,3]),('aa','cc',['a','a','b'],['b','b','c'],[2,10,3]),('z','a',['z'],['a'],[9]),('az','za',['a','z'],['z','a'],[4,7]),('abcd','abce',['a'],['e'],[10000]),('cab','abc',['c','a','b'],['a','b','c'],[3,4,5]),('hello','world',['h','e','l','o','w','r','d'],['w','o','r','d','h','l','o'],[2,2,2,2,2,2,2]),('bbb','aaa',['b','c','b'],['c','a','a'],[1,1,9]),('a','b',['a','z','a'],['z','b','b'],[1,1,9])]],CONVERSION,[CONVERSION.replace('min(distance[a][b],price)','price'),CONVERSION.replace('for middle in range(26):','for middle in range(25):')],['Overwrites a cheaper duplicate direct rule with the last listed cost.','Never allows z as an intermediate character in a cheapest conversion path.'],conversion_oracle,random_conversion,lesson('Character rules form a directed weighted graph shared by every string position.','Compute all-pairs shortest paths once, then sum the required distance for each aligned character pair.','Initialize direct minima and zero diagonals; run Floyd–Warshall; reject infinity while scanning source and target.','Every sequence of character changes is a graph path, and Floyd–Warshall finds its minimum cost; positions are independent, so their minima add.'),'O(26^3+n+rules)','O(26^2)',5),
2981: entry('longest_thrice_special_substring',[('s','str')],'int',['strings','counting','runs'],['s has at least three lowercase letters.','A special substring contains repetitions of only one character, and overlapping occurrences count separately.','Return the greatest length occurring at least three times, or -1.'],[(['aaaa'],'The length-two substring aa starts at positions zero, one, and two, while length three appears only twice.'),(['abcdef'],'Every one-letter special substring uses a different character, so none appears three times.')],[[s] for s in ['aaa','aab','aba','abcaba','aaaaa','aaabaa','ababab','bbbcccbbb','abcabcabc','zzzzzz','aabaaabaa','ccaccacc','xyyyyyx','mississippi']],SPECIAL,[SPECIAL.replace('>=3','>3'),SPECIAL.replace('max(0,length-size+1)','max(0,length-size)')],['Requires four occurrences instead of the specified three.','Undercounts overlapping substrings inside each repeated-character run by one.'],special_oracle,random_special,lesson('A run of length r contains max(0,r-L+1) occurrences of a one-character substring of length L.','Collect run lengths per character and test candidate lengths by summing their occurrence contributions.','For each character and L through its largest run, sum max(0,run-L+1); retain L when the sum is at least three.','Every special occurrence lies wholly in exactly one same-character run, so the run formula counts all starts exactly once, including overlaps.'),'O(n^2)','O(n)',5),
2992: entry('count_self_divisible_permutations',[('n','int')],'int',['bitmask dynamic programming','backtracking','number theory'],['n is between one and fifteen; values thirteen through fifteen are a tested app-domain extension of the source limit.','Permute values 1 through n into one-indexed positions.','Count arrangements where gcd(value, position) equals one at every position.'],[([1],'The sole arrangement [1] satisfies gcd(1,1)=1.'),([3],'Exactly [1,3,2], [3,1,2], and [2,3,1] satisfy every coprimality condition.')],[[n] for n in [2,4,5,6,7,8,9,10,11,12,13,14,15]],PERMUTATIONS,[PERMUTATIONS.replace('gcd(position,value)==1','(position%value==0 or value%position==0)'),PERMUTATIONS.replace('position=mask.bit_count()+1','position=mask.bit_count()')],['Uses the divisibility rule from Beautiful Arrangement instead of coprimality.','Treats the zero-based filled count as the one-based position.'],permutations_oracle,random_permutations,lesson('A used-value bitmask determines the next one-based position, so no ordering prefix beyond the mask is needed.','Memoize the number of valid completions for every mask and try each unused value coprime to the next position.','position=popcount(mask)+1; recurse after setting each eligible value bit; return one when all positions are filled.','Every valid permutation follows one unique choice path, invalid placements are excluded immediately, and identical masks have identical remaining choices.'),'O(n*2^n)','O(2^n)',5),
2998: entry('minimum_operations_to_equal',[('x','int'),('y','int')],'int',['dynamic programming','recursion','shortest paths'],['x and y are positive integers.','One move increments or decrements the current value, or divides it by five or eleven when exactly divisible.','Return the minimum moves needed to reach y.'],[([26,1],'Decrement to twenty-five, then divide by five twice, for three moves.'),([54,2],'Increment to fifty-five, divide by eleven and five, then increment to two, for four moves.')],[[x,y] for x,y in [(1,1),(1,10),(10,1),(5,1),(11,1),(25,1),(24,1),(27,1),(100,3),(99,2),(121,1),(25,30),(10000,1),(73,14)]],OPERATIONS,[OPERATIONS.replace('(5,11)','(5,)'),OPERATIONS.replace('divisor-remainder+1+solve(value//divisor+1)','remainder+1+solve(value//divisor+1)')],['Never considers division by eleven.','Uses the decrement distance when moving upward to the next divisible value.'],operations_oracle,random_operations,lesson('Before a division, the optimal path may adjust either down or up to the nearest multiple.','Memoize by current value and compare direct decrements with both rounding directions for divisors five and eleven.','For each divisor d, try r decrements then divide, or d-r increments then divide; stop with direct increments once value≤y.','Any path using a next division must first reach some multiple; the nearest multiple in either direction dominates farther ones before that same division, so the recurrence is exhaustive.'),'O(log x states with memoization)','O(log x)',5),
3001: entry('minimum_queen_capture_moves',[('a','int'),('b','int'),('c','int'),('d','int'),('e','int'),('f','int')],'int',['geometry','simulation','chess'],['All coordinates are from one through eight, with rook at (a,b), bishop at (c,d), queen at (e,f), and no shared square.','A rook attacks along rows and columns; a bishop attacks along diagonals; neither may jump over the other white piece.','Return one if either has a clear direct attack, otherwise two.'],[([1,1,8,8,2,3],'Neither white piece attacks the queen initially, so repositioning and then capturing needs two moves.'),([5,3,3,4,5,2],'The rook shares row five with the queen and the bishop does not block the adjacent path, so one move suffices.')],[[*s] for s in [((1,1),(2,2),(1,8)),((1,1),(1,4),(1,8)),((1,1),(2,1),(8,1)),((8,8),(4,4),(1,1)),((1,8),(4,5),(8,1)),((4,4),(2,2),(6,6)),((4,4),(5,5),(6,6)),((3,7),(5,5),(7,3)),((3,7),(4,6),(7,3)),((2,3),(7,4),(2,8)),((2,3),(2,5),(2,8)),((7,2),(4,5),(1,8)),((6,6),(1,2),(3,4)),((8,1),(2,7),(5,4))] for s in [[coordinate for square in s for coordinate in square]]],CHESS,[CHESS.replace('min(b,f)<d<max(b,f)','False'),CHESS.replace('bishop_aligned=abs(c-e)==abs(d-f)','bishop_aligned=c-e==d-f')],['Ignores a bishop blocking the rook along a shared row.','Checks only one diagonal slope for the bishop and misses the other.'],chess_oracle,random_chess,lesson('Only a direct attack can finish in one move; otherwise the unobstructed board always permits capture in two.','Test rook row/column alignment and bishop diagonal alignment, excluding cases where the other piece lies strictly between attacker and queen.','Evaluate the two rook rays and four bishop rays with blocker checks; return one on any clear ray, else two.','The ray tests exactly characterize legal one-move captures, and when none exists a white piece can reposition to create a capture on its following move.'),'O(1)','O(1)',5),
}
