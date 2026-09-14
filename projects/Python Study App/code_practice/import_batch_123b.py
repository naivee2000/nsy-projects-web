"""Second slice of workbook batch 123."""

from fractions import Fraction

from .import_batch_055 import entry


def halve_oracle(args):
    values = [Fraction(value) for value in args[0]]
    target = sum(values) / 2
    reduced = Fraction(0)
    operations = 0
    while reduced < target:
        largest = max(values)
        index = values.index(largest)
        values[index] /= 2
        reduced += largest / 2
        operations += 1
    return operations


def random_halve(rng):
    return [[rng.randint(1, 100) for _ in range(rng.randint(1, 20))]]


def tiles_oracle(args):
    floor, carpets, length = args
    best = floor.count("1")

    def place(number, covered):
        nonlocal best
        if number == carpets:
            best = min(best, sum(char == "1" and index not in covered for index, char in enumerate(floor)))
            return
        for start in range(len(floor)):
            place(number + 1, covered | set(range(start, min(len(floor), start + length))))

    place(0, set())
    return best


def random_tiles(rng):
    return [
        "".join(rng.choice("01") for _ in range(rng.randint(1, 10))),
        rng.randint(1, 3),
        rng.randint(1, 5),
    ]


def hills_oracle(args):
    values = []
    for value in args[0]:
        if not values or values[-1] != value:
            values.append(value)
    return sum(
        (values[index] > values[index - 1] and values[index] > values[index + 1])
        or (values[index] < values[index - 1] and values[index] < values[index + 1])
        for index in range(1, len(values) - 1)
    )


def random_hills(rng):
    return [[rng.randint(0, 8) for _ in range(rng.randint(1, 30))]]


def collisions_oracle(args):
    stack = []
    collisions = 0
    for direction in args[0]:
        if direction == "L":
            if stack and stack[-1] == "R":
                collisions += 2
                stack.pop()
                while stack and stack[-1] == "R":
                    collisions += 1
                    stack.pop()
                stack.append("S")
            elif stack and stack[-1] == "S":
                collisions += 1
            else:
                stack.append("L")
        elif direction == "S":
            while stack and stack[-1] == "R":
                collisions += 1
                stack.pop()
            stack.append("S")
        else:
            stack.append("R")
    return collisions


def random_collisions(rng):
    return ["".join(rng.choice("LRS") for _ in range(rng.randint(1, 35)))]


def health_oracle(args):
    damage, armor = args
    return min(sum(damage) - min(value, armor) + 1 for value in damage)


def random_health(rng):
    return [[rng.randint(1, 50) for _ in range(rng.randint(1, 20))], rng.randint(1, 60)]


HALVE = '''\
def minimum_halving_operations(nums):
    import heapq
    heap=[-float(value) for value in nums];heapq.heapify(heap)
    target=sum(nums)/2;reduced=0;operations=0
    while reduced<target:
        largest=-heapq.heappop(heap);half=largest/2
        reduced+=half;operations+=1;heapq.heappush(heap,-half)
    return operations
'''

TILES = '''\
def minimum_visible_white_tiles(floor,num_carpets,carpet_len):
    from functools import lru_cache
    @lru_cache(None)
    def search(index,carpets):
        if index>=len(floor):return 0
        if carpets==0:return floor[index:].count('1')
        leave=(floor[index]=='1')+search(index+1,carpets)
        cover=search(index+carpet_len,carpets-1)
        return min(leave,cover)
    return search(0,num_carpets)
'''

HILLS = '''\
def count_hills_and_valleys(nums):
    compressed=[]
    for value in nums:
        if not compressed or compressed[-1]!=value:compressed.append(value)
    return sum((compressed[index]-compressed[index-1])*(compressed[index]-compressed[index+1])>0 for index in range(1,len(compressed)-1))
'''

COLLISIONS = '''\
def count_road_collisions(directions):
    left=0
    while left<len(directions) and directions[left]=='L':left+=1
    right=len(directions)-1
    while right>=left and directions[right]=='R':right-=1
    return sum(directions[index]!='S' for index in range(left,right+1))
'''

HEALTH = '''\
def minimum_starting_health(damage,armor):
    return sum(damage)-min(max(damage),armor)+1
'''


BATCH = {
    2208: entry('minimum_halving_operations',[('nums','list[int]')],'int',['arrays','greedy','heaps'],['One operation replaces one current value by exactly half of itself.','Continue until the array sum has decreased by at least half of its original value.','Return the minimum operation count; intermediate values may be fractional.'],[([[5,19,8,1]],'Halving the current largest value at each step reaches half the original sum in three operations.'),([[3,8,20]],'Halving twenty, then ten, reduces at least half of the original total in two operations.')],[[x] for x in [[1],[2],[5,19,8,1],[3,8,20],[1,1],[10,10],[1,2,3],[100],[7,7,7],[1,100],[8,4,2,1],[9,3,6],[5,5,20,20],[2,50,2,50]]],HALVE,[HALVE.replace('target=sum(nums)/2','target=sum(nums)/3'),HALVE.replace('heapq.heappush(heap,-half)','heapq.heappush(heap,-largest)')],['Stops after reducing only one third of the original sum.','Pushes the original value back instead of its half, allowing the same reduction repeatedly.'],halve_oracle,random_halve,['Each operation gains half of the value selected, so the largest current value gives the greatest immediate reduction.','Use a max-heap and track accumulated reduction against half the original sum.','Pop the largest, add its half to reduced, push that half back, and count until the target is reached.','An exchange argument replaces any smaller choice with the current largest without reducing progress, so the greedy sequence minimizes operations.'],'O((n+operations) log n)','O(n)',6),
    2209: entry('minimum_visible_white_tiles',[('floor','str'),('num_carpets','int'),('carpet_len','int')],'int',['strings','dynamic programming'],['floor uses one for white and zero for black tiles.','Each carpet covers carpet_len consecutive positions; carpets may overlap and may extend past the useful suffix.','Use at most num_carpets carpets to minimize uncovered white tiles.'],[(['10110101',2,2],'Two length-two carpets can cover all but two white tiles, so return two.'),(['11111',2,3],'Two carpets can cover the whole length, leaving zero visible white tiles.')],[[s,c,l] for s,c,l in [('0',1,1),('1',1,1),('10110101',2,2),('11111',2,3),('00000',2,2),('10101',1,2),('10101',2,1),('111000111',1,3),('111000111',2,3),('0101010',3,2),('1',5,4),('11011',1,5),('100001',1,2),('1011110',2,3)]],TILES,[TILES.replace("leave=(floor[index]=='1')","leave=1"),TILES.replace('index+carpet_len','index+carpet_len-1')],['Charges an uncovered tile even when the current tile is black.','Advances one tile too little after placing a carpet.'],tiles_oracle,random_tiles,['At each leftmost undecided tile, either leave it visible or begin a carpet there.','Memoize by current index and remaining carpets.','Return min(is_white+search(i+1,c), search(i+length,c-1)); handle exhausted floor or carpets.','Every covering has one of these two choices at its first undecided tile, and later cost depends only on the suffix and carpet count.'],'O(n*num_carpets)','O(n*num_carpets)',8),
    2210: entry('count_hills_and_valleys',[('nums','list[int]')],'int',['arrays','two pointers'],['For an index, compare the closest value on each side that differs from nums[i].','Equal adjacent values form one plateau and must be counted at most once.','A hill is greater than both non-equal neighbors; a valley is smaller than both.'],[([[2,4,1,1,6,5]],'After compressing the plateau, four is a hill, one a valley, and six a hill, giving three.'),([[6,6,5,5,4,1]],'The compressed values decrease monotonically, so there are no hills or valleys.')],[[x] for x in [[1],[1,2],[1,2,1],[2,1,2],[2,4,1,1,6,5],[6,6,5,5,4,1],[1,1,1],[1,2,2,1],[3,1,1,2],[1,3,2,4,1],[5,4,3,2,1],[1,2,3,4,5],[2,2,3,3,2,2],[0,1,0,1,0]]],HILLS,[HILLS.replace("compressed[-1]!=value","compressed[-1]==value"),HILLS.replace('>0','<0')],['Keeps only repeated neighbors instead of removing plateau duplicates.','Counts monotone middle values instead of strict extrema.'],hills_oracle,random_hills,['Plateaus obscure closest non-equal neighbors, so compress consecutive duplicates first.','In the compressed list, every internal local extremum represents exactly one hill or valley.','Count indices where (current-left)*(current-right)>0.','Both differences share a sign exactly when current is above both neighbors or below both; compression prevents duplicate plateau counts.'],'O(n)','O(n)',3),
    2211: entry('count_road_collisions',[('directions','str')],'int',['strings','simulation','stacks'],['Cars are ordered left to right and each starts moving L, R, or staying S.','Opposing moving cars contribute two collisions; a moving car hitting a stopped car contributes one, then becomes stopped.','Cars initially moving left from the leading edge and right from the trailing edge escape without collision.'],[(['RLRSLL'],'After all interactions, five moving cars participate in collisions.'),(['LLRR'],'Both left cars escape left and both right cars escape right, so no collision occurs.')],[[x] for x in ['L','R','S','RL','LR','RS','SL','RLRSLL','LLRR','RRLL','SSS','RRSLL','LLRSSR','RSRS','LRLR','RRRSSSLLL']],COLLISIONS,[COLLISIONS.replace("directions[left]=='L'","directions[left]=='R'"),COLLISIONS.replace("directions[right]=='R'","directions[right]=='L'")],['Trims leading right-moving cars even though they may collide ahead.','Trims trailing left-moving cars even though they may collide behind.'],collisions_oracle,random_collisions,['Only cars moving outward at the two extremes can escape forever.','Trim the leading L run and trailing R run; every remaining moving car eventually collides once.','Count non-S characters in the untrimmed middle segment.','A remaining R has a stopped or left-moving obstacle ahead, and a remaining L has one behind; each moving car contributes exactly one collision event participation.'],'O(n)','O(1)',6),
    2214: entry('minimum_starting_health',[('damage','list[int]'),('armor','int')],'int',['arrays','greedy'],['Every level deals its listed positive damage and health must remain strictly above zero.','Armor may be used once and prevents min(level damage,armor) damage.','Return the minimum integer starting health needed to survive all levels.'],[([[2,7,4,3],4],'Total damage is sixteen; armor prevents four, so starting at thirteen leaves health one.'),([[2,5,3,4],7],'Use armor on damage five to prevent all five, requiring ten starting health.')],[[d,a] for d,a in [([1],1),([5],2),([2,7,4,3],4),([2,5,3,4],7),([1,1,1],1),([10,1,1],5),([3,3,3],10),([1,100],50),([8,2,6,4],6),([5,5],5),([9,1,9],8),([2,4,6,8],3),([20,10,5],100),([7,14,21],7)]],HEALTH,[HEALTH.replace('max(damage)','min(damage)'),HEALTH.replace('+1','')],['Uses armor on the smallest damage level instead of the largest useful reduction.','Forgets the extra health point required to stay strictly above zero.'],health_oracle,random_health,['Only total damage and the largest preventable single hit matter.','Use armor on the largest damage level, reducing total loss by min(max_damage,armor).','Return sum(damage)-min(max(damage),armor)+1.','Armor’s reduction is monotone in the chosen hit, so the largest hit is optimal; one extra point is necessary and sufficient for positive final health.'],'O(n)','O(1)',5),
}
