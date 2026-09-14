"""Second slice of workbook batch 131."""

from .import_batch_055 import entry


def conflict_oracle(args):
    first,second=args
    def minute(value):
        hour,minute=map(int,value.split(':'));return hour*60+minute
    occupied_a=set(range(minute(first[0]),minute(first[1])+1))
    occupied_b=set(range(minute(second[0]),minute(second[1])+1))
    return bool(occupied_a&occupied_b)


def random_conflict(rng):
    def text(value):return f'{value//60:02d}:{value%60:02d}'
    a,b=sorted(rng.sample(range(1440),2));c,d=sorted(rng.sample(range(1440),2))
    return [[text(a),text(b)],[text(c),text(d)]]


def odd_oracle(args):
    words=args[0]
    signatures=[[ord(word[i+1])-ord(word[i]) for i in range(len(word)-1)] for word in words]
    for index,signature in enumerate(signatures):
        if signatures.count(signature)==1:return words[index]


def random_odd(rng):
    length=rng.randint(2,8);count=rng.randint(3,9);base=[rng.randint(-3,3) for _ in range(length-1)]
    odd=list(base);position=rng.randrange(length-1);odd[position]+=1 if odd[position]<25 else -1
    def make(signature,start):
        values=[start]
        for difference in signature:values.append(values[-1]+difference)
        if min(values)<0 or max(values)>25:return make(signature,12)
        return ''.join(chr(97+v) for v in values)
    words=[make(base,rng.randint(6,18)) for _ in range(count-1)]+[make(odd,rng.randint(6,18))]
    rng.shuffle(words);return [words]


def average_oracle(args):
    values=[value for value in args[0] if value%6==0]
    return sum(values)//len(values) if values else 0


def random_average(rng):
    return [[rng.randint(1,100) for _ in range(rng.randint(1,25))]]


def operations_oracle(args):
    nums=list(args[0])
    for i in range(len(nums)-1):
        if nums[i]==nums[i+1]:nums[i]*=2;nums[i+1]=0
    result=[value for value in nums if value]
    return result+[0]*(len(nums)-len(result))


def random_operations(rng):
    return [[rng.randint(0,5) for _ in range(rng.randint(2,20))]]


def averages_oracle(args):
    values=sorted(args[0]);sums=[]
    while values:sums.append(values.pop(0)+values.pop())
    return len(set(sums))


def random_averages(rng):
    return [[rng.randint(0,30) for _ in range(2*rng.randint(1,10))]]


CONFLICT='''\
def events_conflict(event1,event2):
    return max(event1[0],event2[0])<=min(event1[1],event2[1])
'''

ODD='''\
def odd_difference_string(words):
    signatures=[]
    for word in words:signatures.append(tuple(ord(right)-ord(left) for left,right in zip(word,word[1:])))
    for word,signature in zip(words,signatures):
        if signatures.count(signature)==1:return word
'''

AVERAGE='''\
def average_even_divisible_by_three(nums):
    values=[value for value in nums if value%6==0]
    return sum(values)//len(values) if values else 0
'''

OPERATIONS='''\
def apply_adjacent_double_operations(nums):
    nums=list(nums)
    for index in range(len(nums)-1):
        if nums[index]==nums[index+1]:nums[index]*=2;nums[index+1]=0
    nonzero=[value for value in nums if value]
    return nonzero+[0]*(len(nums)-len(nonzero))
'''

AVERAGES='''\
def number_of_distinct_extreme_averages(nums):
    values=sorted(nums);sums=set()
    for index in range(len(values)//2):sums.add(values[index]+values[-1-index])
    return len(sums)
'''


BATCH={
2446:entry('events_conflict',[('event1','list[str]'),('event2','list[str]')],'bool',['strings','intervals'],['Each event is [start,end] in 24-hour HH:MM format.','Both endpoints are included.','Return whether the two events share at least one minute.'],[([['01:15','02:00'],['02:00','03:00']],'The first event ends exactly when the second starts, and inclusive endpoints make that a conflict.'),([['10:00','11:00'],['11:01','12:00']],'The second event begins one minute after the first ends, so they do not overlap.')],[[a,b] for a,b in [(['00:00','00:00'],['00:00','00:00']),(['00:00','01:00'],['01:00','02:00']),(['00:00','00:59'],['01:00','02:00']),(['12:00','13:00'],['11:00','12:00']),(['12:00','13:00'],['13:01','14:00']),(['09:30','10:30'],['09:45','10:00']),(['09:45','10:00'],['09:30','10:30']),(['23:00','23:59'],['22:00','22:59']),(['05:00','06:00'],['04:00','07:00']),(['04:00','07:00'],['05:00','06:00']),(['08:15','08:45'],['08:46','09:00']),(['14:10','15:20'],['15:20','15:30']),(['01:00','03:00'],['02:00','04:00']),(['20:00','21:00'],['19:59','20:00'])]],CONFLICT,[CONFLICT.replace('<=','<'),CONFLICT.replace('max(event1[0],event2[0])','min(event1[0],event2[0])')],['Treats touching inclusive endpoints as nonconflicting.','Uses the earlier start, which can report separated events as overlapping.'],conflict_oracle,random_conflict,['Lexicographic order of zero-padded HH:MM strings is chronological order.','An overlap starts at the later start and ends at the earlier end.','Return later_start <= earlier_end because endpoints are inclusive.','Two closed intervals intersect exactly under that inequality.'],'O(1)','O(1)',3),
2451:entry('odd_difference_string',[('words','list[str]')],'str',['strings','arrays','counting'],['All words have equal length.','A word’s difference signature contains each next character code minus the previous code.','Exactly one word has a signature different from every other word; return that word.'],[([['adc','wzy','abc']],'adc and wzy share differences [3,-1], while abc has [1,1], so abc is odd.'),([['aaa','bob','ccc','ddd']],'The constant-letter words share [0,0], while bob has [13,-13].')],[[w] for w in [['ab','bc','ac'],['abc','bcd','ace'],['aaa','bbb','aba'],['az','by','aa'],['abcd','bcde','abce'],['xyx','aba','cdc'],['mnop','nopq','mnpp'],['zzzz','aaaa','zzzy'],['cat','dbu','dog'],['ace','bdf','acf'],['hello','ifmmp','hellp'],['aaa','bbb','ccc','aab'],['pqrs','qrst','prst'],['azby','bycx','azbz']]],ODD,[ODD.replace('ord(right)-ord(left)','ord(right)+ord(left)'),ODD.replace('==1','>1')],['Uses sums of adjacent codes, which are not invariant under uniform character shifts.','Returns a word from the repeated signature group instead of the unique signature.'],odd_oracle,random_odd,['Convert each word into its tuple of adjacent character-code differences.','Uniformly shifted words have identical difference tuples.','Count signatures and return the word whose signature occurs once.','The contract guarantees exactly one unique signature, so that lookup identifies the required word.'],'O(words*length)','O(words*length)',3),
2455:entry('average_even_divisible_by_three',[('nums','list[int]')],'int',['arrays','filtering'],['Select values divisible by both two and three.','Return their integer arithmetic mean.','Return zero when no value qualifies.'],[([[1,3,6,10,12,15]],'Six and twelve qualify, and their average is nine.'),([[1,2,4,7,10]],'No value is divisible by six, so the result is zero.')],[[a] for a in [[6],[12,18],[1],[0],[3,6],[2,4,8],[6,7,8],[24,30,36],[5,10,15,20],[1,6,13,18],[60,1,2],[7,14,21,28],[6,6,7],[100,102,104]]],AVERAGE,[AVERAGE.replace('value%6==0','value%3==0'),AVERAGE.replace('//len(values)','//len(nums)')],['Includes odd multiples of three even though qualifying values must also be even.','Divides the qualifying sum by the full input length.'],average_oracle,random_average,['Divisibility by both two and three is equivalent to divisibility by six.','Collect or count values with value%6==0.','Return their sum divided by their count, or zero for an empty selection.','The filter exactly represents both divisibility conditions, so its arithmetic mean is the requested value.'],'O(n)','O(n)',3),
2460:entry('apply_adjacent_double_operations',[('nums','list[int]')],'list[int]',['arrays','simulation','two pointers'],['Scan indexes left to right once.','When adjacent values are equal, double the left value and replace the right value with zero.','After the scan, move all zeroes to the end while preserving nonzero order.'],[([[1,2,2,1,1,0]],'The two pairs combine during the scan, then compaction gives [1,4,2,0,0,0].'),([[0,1]],'No equal adjacent operation changes the values, and compaction gives [1,0].')],[[a] for a in [[1,1],[2,2,2],[0,0],[1,2,3],[1,1,1,1],[2,0,2],[4,4,8,8],[0,1,1],[3,3,0,3,3],[1,2,2,4],[5,5,10],[1,1,2,2,4,4],[0,0,1,1],[2,2,4,4,8]]],OPERATIONS,[OPERATIONS.replace('range(len(nums)-1)','range(len(nums)-2)'),OPERATIONS.replace('if nums[index]==nums[index+1]','if nums[index]!=nums[index+1]')],['Never processes the final adjacent pair.','Doubles unequal neighbors instead of equal neighbors.'],operations_oracle,random_operations,['Simulate the adjacent operations before moving any zeroes.','At each index, compare the current value with the next value, because earlier operations may have changed it.','After one left-to-right pass, collect nonzero values and append enough zeroes to restore the length.','The simulation follows the required order exactly, and stable compaction preserves the mandated nonzero order.'],'O(n)','O(n)',3),
2465:entry('number_of_distinct_extreme_averages',[('nums','list[int]')],'int',['arrays','sorting','two pointers'],['The array has even length.','Repeatedly remove its current minimum and maximum and record their average.','Return the number of distinct recorded averages.'],[([[4,1,4,0,3,5]],'Sorted extreme pairs sum to five, five, and seven, producing two distinct averages.'),([[1,100]],'Only one pair is removed, so exactly one average occurs.')],[[a] for a in [[1,2],[1,1],[1,2,3,4],[1,1,2,2],[0,5,1,4],[1,5,2,4,3,3],[10,20,30,40],[0,0,0,0],[1,10,2,9,3,8],[5,6,5,6],[2,4,6,8,10,12],[9,1,9,1],[3,7,4,6],[100,0,50,50]]],AVERAGES,[AVERAGES.replace('values[-1-index]','values[-index]'),AVERAGES.replace('sums.add(values[index]+values[-1-index])','sums.add(values[index]-values[-1-index])')],['Pairs the minimum with itself on the first iteration because of an incorrect negative index.','Records extreme differences instead of averages (or their doubled sums).'],averages_oracle,random_averages,['Sort the values so current minima and maxima are at opposite ends.','Pair values[index] with values[-1-index].','Store each pair sum; two averages are equal exactly when their sums are equal because every pair is divided by two.','Sorted symmetric pairs are exactly the sequence of extreme removals, and the set counts distinct results.'],'O(n log n)','O(n)',3),
}
