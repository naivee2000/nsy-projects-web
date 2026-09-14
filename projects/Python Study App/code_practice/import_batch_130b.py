"""Second slice of workbook batch 130: compact mapping and sorting exercises."""

from collections import Counter
from datetime import date
from math import gcd

from .import_batch_055 import entry


def distance_oracle(args):
    text, distance = args
    for code in range(26):
        char = chr(97 + code); positions = [i for i, value in enumerate(text) if value == char]
        if positions and (len(positions) != 2 or positions[1] - positions[0] - 1 != distance[code]): return False
    return True


def random_distance(rng):
    letters = rng.sample(list('abcdefgh'), rng.randint(1, 6)); chars = letters * 2; rng.shuffle(chars); text = ''.join(chars)
    distances = [0] * 26
    for char in letters:
        first = text.index(char); distances[ord(char)-97] = text.index(char, first + 1) - first - 1
    if rng.random() < .5:
        code = ord(rng.choice(letters)) - 97; distances[code] += rng.choice((-1, 1))
    return [text, distances]


def even_oracle(args):
    counts = Counter(value for value in args[0] if value % 2 == 0)
    return min((-frequency, value) for value, frequency in counts.items())[1] if counts else -1


def random_even(rng):
    return [[rng.randint(0, 20) for _ in range(rng.randint(1, 25))]]


def together_oracle(args):
    arrive_a, leave_a, arrive_b, leave_b = args
    def ordinal(text):
        month, day = map(int, text.split('-')); return date(2023, month, day).timetuple().tm_yday
    return max(0, min(ordinal(leave_a), ordinal(leave_b)) - max(ordinal(arrive_a), ordinal(arrive_b)) + 1)


def random_together(rng):
    starts = sorted(rng.sample(range(1, 365), 4)); a,b,c,d=starts
    def text(day):
        current=date.fromordinal(date(2023,1,1).toordinal()+day-1); return current.strftime('%m-%d')
    return [text(a),text(rng.randint(a,d)),text(b),text(rng.randint(b,d))]


def multiple_oracle(args):
    n=args[0]; return n*2//gcd(n,2)


def random_multiple(rng): return [rng.randint(1,150)]


def people_oracle(args):
    names, heights=args
    return [name for _,name in sorted(zip(heights,names),reverse=True)]


def random_people(rng):
    n=rng.randint(1,12); heights=rng.sample(range(100,250),n)
    return [[f'person{i}' for i in range(n)],heights]


DISTANCE='''\
def check_letter_distances(s,distance):
    first={}
    for index,char in enumerate(s):
        if char in first:
            if index-first[char]-1!=distance[ord(char)-97]:return False
        else:first[char]=index
    return True
'''

EVEN='''\
def most_frequent_even(nums):
    counts=__import__('collections').Counter(value for value in nums if value%2==0)
    return min(counts,key=lambda value:(-counts[value],value)) if counts else -1
'''

TOGETHER='''\
def count_days_together(arriveAlice,leaveAlice,arriveBob,leaveBob):
    days=[31,28,31,30,31,30,31,31,30,31,30,31]
    def ordinal(text):
        month,day=map(int,text.split('-'));return sum(days[:month-1])+day
    return max(0,min(ordinal(leaveAlice),ordinal(leaveBob))-max(ordinal(arriveAlice),ordinal(arriveBob))+1)
'''

MULTIPLE='''\
def smallest_even_multiple(n):
    return n if n%2==0 else n*2
'''

PEOPLE='''\
def sort_people_by_height(names,heights):
    return [name for _,name in sorted(zip(heights,names),reverse=True)]
'''


BATCH={
2399:entry('check_letter_distances',[('s','str'),('distance','list[int]')],'bool',['strings','arrays'],['Every letter used in s appears exactly twice.','For a letter at alphabet index i, exactly distance[i] characters must lie between its occurrences.','Unused letters impose no condition.'],[(['abaccb',[1,3,0,5]+[0]*22],'The gaps for a, b, and c equal one, three, and zero respectively.'),(['aa',[1]+[0]*25],'The two a characters have gap zero, not the required one.')],[[s,d] for s,d in [('aa',[0]*26),('abba',[2,0]+[0]*24),('abcbac',[3,1,2]+[0]*23),('abcabc',[2,2,2]+[0]*23),('zz',[0]*25+[0]),('zaz a'.replace(' ',''),[1]+[0]*24+[1]),('aabb',[0,0]+[0]*24),('abab',[1,1]+[0]*24),('bccb',[0,1,0]+[0]*23),('xyyx',[0]*23+[2,0,0]),('qrrq',[0]*16+[2,0]+[0]*8),('abcddcba',[6,4,2,0]+[0]*22),('mnnm',[0]*12+[2,0]+[0]*12),('abccba',[4,2,0]+[0]*23)]],DISTANCE,[DISTANCE.replace('-1!=distance','!=distance'),DISTANCE.replace('return False','return True',1)],['Counts the endpoints as part of the between-character distance.','Returns true on the first mismatched letter instead of rejecting it.'],distance_oracle,random_distance,['Remember the index of each letter’s first occurrence.','At its second occurrence, the number between is current-first-1.','Compare that gap with distance[ord(letter)-ord(a)] and reject any mismatch.','Every used letter is checked exactly at its second occurrence, so accepting means all required gaps match.'],'O(n)','O(1)',3),
2404:entry('most_frequent_even',[('nums','list[int]')],'int',['arrays','counting'],['Consider only even values.','Return the even value with greatest frequency.','Break frequency ties by choosing the smallest value; return -1 when no even value exists.'],[([[0,1,2,2,4,4,1]],'Two and four tie at two occurrences, so the smaller value two is returned.'),([[1,3,5,7]],'No even value occurs, so the result is minus one.')],[[a] for a in [[2],[1],[2,2],[2,4],[4,4,2,2],[0,0,2],[6,4,6,4],[8,8,8,2,2],[1,2,3,4],[10,6,10],[0,1,0],[14,12,12,14],[9,8,7,8],[20,18,16]]],EVEN,[EVEN.replace('value%2==0','value%2==1'),EVEN.replace('(-counts[value],value)','(-counts[value],-value)')],['Counts odd values instead of even values.','Breaks a frequency tie in favor of the largest value.'],even_oracle,random_even,['Count only values divisible by two.','If the frequency map is empty, return -1.','Choose the key minimizing (-frequency,value), which maximizes frequency then minimizes value.','That ordering encodes both the primary frequency rule and the required tie break.'],'O(n)','O(n)',3),
2409:entry('count_days_together',[('arriveAlice','str'),('leaveAlice','str'),('arriveBob','str'),('leaveBob','str')],'int',['strings','prefix sums','intervals'],['Dates use MM-DD within the same non-leap year.','Arrival and departure dates are both included.','Return the number of calendar days when both people are present.'],[(['08-15','08-18','08-16','08-19'],'The inclusive overlap is August sixteenth through eighteenth, totaling three days.'),(['10-01','10-31','11-01','12-31'],'The intervals do not overlap, so the result is zero.')],[[a,b,c,d] for a,b,c,d in [('01-01','01-01','01-01','01-01'),('01-01','01-10','01-05','01-06'),('01-05','01-06','01-01','01-10'),('02-28','03-01','03-01','03-02'),('04-01','04-30','04-30','05-01'),('12-01','12-31','12-31','12-31'),('06-10','06-20','06-21','06-30'),('03-15','04-15','04-01','05-01'),('01-31','02-01','02-01','02-02'),('07-04','07-04','07-01','07-10'),('09-10','09-20','09-15','09-25'),('11-30','12-02','12-01','12-01'),('05-01','05-31','05-10','05-20'),('02-01','02-28','01-15','02-01')]],TOGETHER,[TOGETHER.replace('+1)',')'),TOGETHER.replace('min(ordinal(leaveAlice),ordinal(leaveBob))','max(ordinal(leaveAlice),ordinal(leaveBob))')],['Treats the inclusive date ranges as half-open and misses one overlap day.','Uses the later departure rather than the earlier one, extending the intersection.'],together_oracle,random_together,['Convert each MM-DD date to a one-based day-of-year using month lengths.','The overlap begins at the later arrival and ends at the earlier departure.','If end < start return zero; otherwise return end-start+1 for inclusive dates.','Intersection endpoints characterize exactly the dates contained in both intervals.'],'O(1)','O(1)',3),
2413:entry('smallest_even_multiple',[('n','int')],'int',['math'],['Return the smallest positive integer divisible by both n and two.','n is a positive integer.','The result is the least common multiple of n and two.'],[([5],'Ten is the first multiple of five that is also even.'),([6],'Six itself is already even and divisible by six.')],[[n] for n in [1,2,3,4,7,8,9,10,11,12,25,50,99,150]],MULTIPLE,[MULTIPLE.replace('n*2','n+2'),MULTIPLE.replace('n if n%2==0 else n*2','2*n')],['Adds two to an odd number, which is not generally divisible by the original n.','Always doubles n even when n itself is already even.'],multiple_oracle,random_multiple,['An even n already satisfies both divisibility requirements.','An odd n needs one factor of two, so 2*n is divisible by both.','Return n for even input and 2*n for odd input.','These are exactly lcm(n,2) in the two possible parity cases, so no smaller common multiple exists.'],'O(1)','O(1)',3),
2418:entry('sort_people_by_height',[('names','list[str]'),('heights','list[int]')],'list[str]',['arrays','sorting'],['names[i] belongs to the person with heights[i].','All heights are distinct.','Return names ordered from greatest height to least height.'],[([['Mary','John','Emma'],[180,165,170]],'Descending heights 180, 170, and 165 correspond to Mary, Emma, and John.'),([['Alice','Bob','Bob'],[155,185,150]],'Names need not be unique; the taller Bob appears before Alice and the shorter Bob.')],[[n,h] for n,h in [(['a'],[1]),(['a','b'],[1,2]),(['a','b'],[2,1]),(['x','y','z'],[3,1,2]),(['same','same'],[5,4]),(['p','q','r','s'],[10,40,20,30]),(['u','v','w'],[100,99,98]),(['u','v','w'],[98,99,100]),(['n1','n2','n3'],[150,200,175]),(['a','b','c','d'],[4,1,3,2]),(['red','blue'],[170,180]),(['one','two','three'],[1,3,2]),(['k','j','i'],[7,9,8]),(['aa','bb','cc','dd'],[12,15,11,14])]],PEOPLE,[PEOPLE.replace('reverse=True','reverse=False'),PEOPLE.replace('zip(heights,names)','zip(names,heights)')],['Sorts heights in ascending order.','Pairs fields in the wrong order and returns numeric heights rather than names.'],people_oracle,random_people,['Zip each height with its corresponding name.','Sort those pairs by height in descending order.','Extract the name from every sorted pair.','Distinct heights make the order unique, and preserving each zipped pair keeps names aligned with their owners.'],'O(n log n)','O(n)',3),
}
