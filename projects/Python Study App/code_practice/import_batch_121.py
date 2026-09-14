"""First slice of workbook batch 121."""

from collections import Counter

from .import_batch_055 import entry


def substring_hash(text, power, modulo):
    total = 0
    factor = 1
    for char in text:
        total = (total + (ord(char) - 96) * factor) % modulo
        factor = factor * power % modulo
    return total


def hash_oracle(args):
    s, power, modulo, k, wanted = args
    for start in range(len(s) - k + 1):
        if substring_hash(s[start : start + k], power, modulo) == wanted:
            return s[start : start + k]


def random_hash(rng):
    length = rng.randint(1, 18)
    s = "".join(rng.choice("abcdef") for _ in range(length))
    power, modulo = rng.randint(1, 12), rng.randint(2, 101)
    k = rng.randint(1, length)
    start = rng.randint(0, length - k)
    return [s, power, modulo, k, substring_hash(s[start : start + k], power, modulo)]


def groups_oracle(args):
    words = args[0]
    sets = [frozenset(word) for word in words]
    graph = [[] for _ in words]
    for i in range(len(words)):
        for j in range(i):
            difference = sets[i] ^ sets[j]
            connected = sets[i] == sets[j] or len(difference) == 1 or (
                len(sets[i]) == len(sets[j]) and len(difference) == 2
            )
            if connected:
                graph[i].append(j)
                graph[j].append(i)
    seen = set()
    sizes = []
    for start in range(len(words)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return [len(sizes), max(sizes)]


def random_groups(rng):
    words = []
    for _ in range(rng.randint(1, 9)):
        letters = rng.sample("abcdefg", rng.randint(1, 5))
        rng.shuffle(letters)
        words.append("".join(letters))
    return [words]


def paint_oracle(args):
    painted = set()
    answer = []
    for left, right in args[0]:
        cells = set(range(left, right))
        answer.append(len(cells - painted))
        painted.update(cells)
    return answer


def random_paint(rng):
    paint = []
    for _ in range(rng.randint(1, 12)):
        left = rng.randint(0, 20)
        paint.append([left, rng.randint(left + 1, 25)])
    return [paint]


def split_oracle(args):
    from itertools import permutations

    digits = str(args[0])
    return min(int("".join(order[:2])) + int("".join(order[2:])) for order in permutations(digits))


def random_split(rng):
    return [rng.randint(1000, 9999)]


def pivot_oracle(args):
    nums, pivot = args
    answer = []
    for relation in (-1, 0, 1):
        answer.extend(value for value in nums if (value > pivot) - (value < pivot) == relation)
    return answer


def random_pivot(rng):
    return [[rng.randint(-8, 8) for _ in range(rng.randint(1, 30))], rng.randint(-8, 8)]


HASH = '''\
def first_substring_with_hash(s,power,modulo,k,hash_value):
    current=0
    for index in range(len(s)-1,len(s)-k-1,-1):
        current=(current*power+ord(s[index])-96)%modulo
    highest=pow(power,k-1,modulo)
    answer=len(s)-k
    if current==hash_value:answer=len(s)-k
    for start in range(len(s)-k-1,-1,-1):
        leaving=ord(s[start+k])-96
        entering=ord(s[start])-96
        current=((current-leaving*highest)*power+entering)%modulo
        if current==hash_value:answer=start
    return s[answer:answer+k]
'''

GROUPS = '''\
def connected_string_groups(words):
    from collections import Counter
    counts=Counter(sum(1<<(ord(char)-97) for char in word) for word in words)
    parent={mask:mask for mask in counts}
    size=dict(counts)
    def find(mask):
        while parent[mask]!=mask:
            parent[mask]=parent[parent[mask]];mask=parent[mask]
        return mask
    def union(a,b):
        if b not in parent:return
        a,b=find(a),find(b)
        if a==b:return
        if size[a]>size[b]:a,b=b,a
        parent[a]=b;size[b]+=size[a]
    removed={}
    for mask in list(parent):
        for bit in range(26):
            if mask>>bit&1:
                smaller=mask^(1<<bit)
                union(mask,smaller)
                if smaller in removed:union(mask,removed[smaller])
                else:removed[smaller]=mask
    roots={find(mask) for mask in parent}
    return [len(roots),max(size[find(mask)] for mask in parent)]
'''

PAINT = '''\
def new_area_painted_each_day(paint):
    next_unpainted={}
    def find(point):
        path=[]
        while point in next_unpainted:
            path.append(point);point=next_unpainted[point]
        for old in path:next_unpainted[old]=point
        return point
    answer=[]
    for left,right in paint:
        point=find(left);added=0
        while point<right:
            added+=1;next_unpainted[point]=find(point+1);point=find(point)
        answer.append(added)
    return answer
'''

SPLIT = '''\
def minimum_four_digit_split_sum(num):
    digits=sorted(map(int,str(num)))
    return 10*(digits[0]+digits[1])+digits[2]+digits[3]
'''

PIVOT = '''\
def stable_pivot_partition(nums,pivot):
    return ([value for value in nums if value<pivot]
            +[value for value in nums if value==pivot]
            +[value for value in nums if value>pivot])
'''


def fixed_hash(s, power, modulo, k, start):
    return [s, power, modulo, k, substring_hash(s[start : start + k], power, modulo)]


H = [
    fixed_hash(s, p, m, k, start)
    for s, p, m, k, start in [
        ("a", 1, 2, 1, 0), ("abc", 3, 17, 1, 1), ("abcd", 2, 97, 2, 1),
        ("aaaa", 7, 20, 2, 2), ("abcdef", 5, 101, 3, 2), ("fedcba", 4, 29, 2, 3),
        ("banana", 3, 31, 3, 1), ("cabca", 6, 37, 2, 2), ("zzzz", 9, 43, 4, 0),
        ("algorithm", 7, 113, 3, 4), ("rollinghash", 11, 127, 5, 2),
        ("mississippi", 2, 53, 4, 4), ("leetcode", 7, 20, 3, 1), ("xyzabc", 8, 89, 2, 4),
    ]
]


BATCH = {
    2156: entry('first_substring_with_hash',[('s','str'),('power','int'),('modulo','int'),('k','int'),('hash_value','int')],'str',['strings','sliding window','rolling hash'],['Use a=1 through z=26 and increasing powers from the substring left edge.','Return the leftmost length-k substring with the requested hash; an answer always exists.','Lengths may reach 20,000, so recomputing every substring hash is too slow.'],[((['leetcode',7,20,2,0]),'Both ee and a later window may hash to zero; ee is the leftmost matching length-two substring.'),((['fbxzaad',31,100,3,32]),'fbx hashes to 32 and occurs before the other matching substring bxz.')],H,HASH,[HASH.replace('range(len(s)-k-1,-1,-1)','range(len(s)-k)'),HASH.replace('ord(s[start])-96','ord(s[start])-97')],['Scans rolling windows in the wrong direction and can return a later match.','Maps a to zero instead of one when adding the incoming character.'],hash_oracle,random_hash,['A reverse rolling window makes removing the rightmost powered character straightforward.','Hash the final window, then slide from right to left while remembering every match.','Subtract the leaving value times power^(k-1), multiply by power, add the entering value, and keep the current start on a match.','The invariant is the specified polynomial hash for s[start:start+k]. Visiting starts in decreasing order means the last saved match is the smallest index.'],'O(n + log k)','O(1)',8),
    2157: entry('connected_string_groups',[('words','list[str]')],'list[int]',['bit manipulation','union find','hash maps'],['Each word contains unique lowercase letters, and letter order does not matter.','Two words connect after exactly one add, delete, or replacement; connectivity is transitive.','Return [number of connected groups, size of the largest group].'],[([['a','b','ab','cde']], 'a, b, and ab connect while cde is separate, giving two groups and largest size three.'),([['a','ab','abc']], 'Each adjacent pair differs by one added letter, so transitivity joins all three words.')],[[x] for x in [['a'],['a','a'],['a','b'],['a','ab'],['ab','cd'],['ab','ac'],['ab','abc','abcd'],['a','bc','abc'],['ace','bdf'],['ab','ba','abc'],['a','c','ac','bd'],['abc','abd','acd','bcd'],['z','yz','xyz'],['abcde','abfde','xy']]],GROUPS,[GROUPS.replace("if smaller in removed:union(mask,removed[smaller])","if False:union(mask,removed[smaller])"),GROUPS.replace('union(mask,smaller)','pass')],['Never joins words related by replacing one letter.','Never joins words related by adding or deleting a letter.'],groups_oracle,random_groups,['Represent each word as a 26-bit set and join directly connected masks.','Deletion toggles one set bit; two masks that produce the same deleted mask differ by one replacement.','Union existing deletion neighbors and keep one representative for each deleted mask; aggregate duplicate words by mask.','Every allowed edit is either one-bit deletion/addition or two masks sharing a one-letter-smaller form, so the unions encode exactly the graph edges.'],'O(26*n alpha(n))','O(n)',8),
    2158: entry('new_area_painted_each_day',[('paint','list[list[int]]')],'list[int]',['arrays','disjoint sets','intervals'],['Each [start,end] paints the half-open interval start <= x < end.','Previously painted positions do not count again, including overlap from nonadjacent earlier days.','Return the newly painted integer length for every day.'],[([[[1,4],[4,7],[5,8]]],'The first two days add three units each; day three adds only [7,8), so return [3,3,1].'),([[[1,5],[2,4]]],'The second interval lies entirely inside prior paint and adds zero new area.')],[[x] for x in [[[0,1]],[[1,3],[2,4]],[[1,5],[2,4]],[[1,2],[1,2]],[[0,5],[5,8]],[[0,10],[2,3],[9,12]],[[5,8],[1,6]],[[1,4],[4,7],[5,8]],[[3,9],[0,4],[8,12]],[[2,6],[6,10],[1,3]],[[0,2],[4,6],[1,5]],[[10,15],[12,20],[0,11]],[[1,10],[3,7],[2,12]],[[0,25],[1,24]]]],PAINT,[PAINT.replace('point=find(left)','point=left'),PAINT.replace('point<right','point<=right')],['Restarts at every coordinate and counts already painted positions again.','Treats the half-open interval endpoint as painted.'],paint_oracle,random_paint,['After a position is painted, future scans should jump over it.','Store a successor link from each painted integer unit to the next candidate unit.','For each interval, find its first unpainted unit; paint it, link it forward, and repeat until end.','Successor links skip exactly the already painted unit cells, so each cell contributes once, on its first day.'],'O(total newly painted alpha(U)+n)','O(total painted)',8),
    2160: entry('minimum_four_digit_split_sum',[('num','int')],'int',['math','greedy','sorting'],['num has exactly four decimal digits; repeated digits and zero digits are allowed.','Use all four digits in two new integers; leading zeros are allowed.','Return the minimum possible sum.'],[([2932],'Sorting gives 2,2,3,9; putting 2 and 2 in the tens places produces 23+29=52.'),([4009],'The two smallest digits are zeros, so 04+09 gives 13.')],[[x] for x in [1000,1001,1010,1023,1111,2002,3001,4009,5555,7008,8080,9000,9876,1234,4321]],SPLIT,[SPLIT.replace('digits[0]+digits[1]','digits[0]+digits[2]'),SPLIT.replace('+digits[2]+digits[3]','+digits[0]+digits[1]')],['Places a larger digit in a tens position.','Reuses the two smallest digits in the ones positions instead of using every digit once.'],split_oracle,random_split,['Tens-place digits contribute ten times as much as ones-place digits.','Sort the four digits and assign the two smallest to the two tens places.','Return 10*(d0+d1)+d2+d3 after sorting.','Any larger tens digit can be exchanged with a smaller ones digit to reduce the sum, proving the greedy placement.'],'O(1)','O(1)',3),
    2161: entry('stable_pivot_partition',[('nums','list[int]'),('pivot','int')],'list[int]',['arrays','stable partition'],['Place all values less than pivot first, equal values second, and greater values last.','Within the less-than and greater-than groups, preserve original relative order.','Return a new rearranged list.'],[(([[9,12,5,10,14,3,10],10]),'The stable groups are [9,5,3], [10,10], and [12,14].'),(([-3,4,3,2],2),'The less group is [-3], the equal group [2], and the stable greater group [4,3].')],[[a,p] for a,p in [([1],1),([1],0),([1,2],1),([2,1],1),([1,1,1],1),([3,2,1],2),([1,2,3],2),([2,3,2,1],2),([5,1,4,2,3],3),([-2,0,2],0),([9,12,5,10,14,3,10],10),([4,4,2,5,1],4),([0,-1,0,1],0),([7,3,9,2,8],5)]],PIVOT,[PIVOT.replace('value<pivot','value<=pivot'),PIVOT.replace('+[value for value in nums if value>pivot]','+[value for value in reversed(nums) if value>pivot]')],['Mixes pivot-equal values into the first group and duplicates them.','Reverses the required relative order of greater values.'],pivot_oracle,random_pivot,['This is a three-way stable partition.','Collect the three relation groups by scanning nums in original order.','Concatenate values < pivot, == pivot, and > pivot.','Each comprehension preserves order within its group, and concatenation enforces the required group ordering.'],'O(n)','O(n)',5),
}
