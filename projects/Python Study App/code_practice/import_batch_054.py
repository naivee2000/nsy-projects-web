"""Value-pair counting, pixel groups, complex products, clocks and binary parity."""
from collections import Counter
from .import_batch_003 import entry


def pairs_oracle(args):
    nums,k=args
    return len({tuple(sorted((a,b))) for i,a in enumerate(nums) for b in nums[i+1:] if abs(a-b)==k})


def pixel_oracle(args):
    picture,target=args;rows=len(picture);cols=len(picture[0]);answer=0
    for r in range(rows):
        for c in range(cols):
            if picture[r][c]!='B':continue
            if sum(v=='B' for v in picture[r])!=target:continue
            owners=[i for i in range(rows) if picture[i][c]=='B']
            if len(owners)==target and all(picture[i]==picture[r] for i in owners):answer+=1
    return answer


def complex_oracle(args):
    a,b=[complex(s.replace('+-','-').replace('i','j')) for s in args]
    value=a*b
    return f'{int(value.real)}+{int(value.imag)}i'


def clock_oracle(args):
    minutes=[int(t[:2])*60+int(t[3:]) for t in args[0]]
    return min(min(abs(a-b),1440-abs(a-b)) for i,a in enumerate(minutes) for b in minutes[i+1:])


def singleton_oracle(args):
    return next(v for v,count in Counter(args[0]).items() if count==1)


def reverse_oracle(args):
    text,k=args;out=[]
    for index in range(len(text)):
        start=index//(2*k)*(2*k);width=min(k,len(text)-start);offset=index-start
        out.append(text[start+width-1-offset] if offset<width else text[index])
    return ''.join(out)


def random_pairs(rng):
    pool=[-10**7,0,10**7]+[rng.randint(-10**7,10**7) for _ in range(8)]
    k=rng.choice([0,1,2,10**7]);base=rng.randint(-100,100)
    if k<=2:pool.extend((base,base+k,base+2*k))
    return [[rng.choice(pool) for _ in range(rng.randint(1,40))],k]


def random_pixel(rng):
    rows=rng.randint(1,7);cols=rng.randint(1,7);target=rng.randint(1,min(rows,cols))
    if rng.random()<.4:
        selected=set(rng.sample(range(cols),target));pattern=['B' if j in selected else 'W' for j in range(cols)]
        picture=[pattern[:] for _ in range(target)]+[['W']*cols for _ in range(rows-target)];rng.shuffle(picture)
    else:picture=[[rng.choice('BW') for _ in range(cols)] for _ in range(rows)]
    return [picture,target]


def random_complex(rng):return [f'{rng.randint(-100,100)}+{rng.randint(-100,100)}i' for _ in range(2)]
def clock_string(minutes):return f'{minutes//60:02d}:{minutes%60:02d}'
def random_clock(rng):
    values=[rng.randrange(1440) for _ in range(rng.randint(2,35))]
    if rng.random()<.2:values[-1]=values[0]
    return [[clock_string(v) for v in values]]


def singleton_input(values,single):return [v for v in values for _ in range(1 if v==single else 2)]
def random_singleton(rng):
    values=sorted(rng.sample(range(100001),rng.randint(1,40)))
    return [singleton_input(values,rng.choice(values))]
def random_reverse(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,100))),rng.randint(1,10000)]


PAIRS='''\
def count_k_diff_pairs(nums,k):
    from collections import Counter
    counts=Counter(nums)
    if k==0:return sum(count>=2 for count in counts.values())
    return sum(value+k in counts for value in counts)
'''
WEIGHTED_PAIRS='''\
def count_k_diff_pairs(nums,k):
    from collections import Counter
    counts=Counter(nums)
    if k==0:return sum(c*(c-1)//2 for c in counts.values())
    return sum(count*counts.get(value+k,0) for value,count in counts.items())
'''
PIXEL='''\
def count_lonely_pixels(picture,target):
    from collections import Counter
    frequencies=Counter(tuple(row) for row in picture)
    columns=[sum(row[c]=='B' for row in picture) for c in range(len(picture[0]))]
    answer=0
    for row,copies in frequencies.items():
        if copies==target and row.count('B')==target:
            answer+=copies*sum(value=='B' and columns[c]==target for c,value in enumerate(row))
    return answer
'''
PIXEL_COUNTS='''\
def count_lonely_pixels(picture,target):
    rows=[row.count('B') for row in picture]
    cols=[sum(row[c]=='B' for row in picture) for c in range(len(picture[0]))]
    return sum(v=='B' and rows[r]==target and cols[c]==target for r,row in enumerate(picture) for c,v in enumerate(row))
'''
COMPLEX='''\
def multiply_complex_numbers(num1,num2):
    a,b=map(int,num1[:-1].split('+'));c,d=map(int,num2[:-1].split('+'))
    real=a*c-b*d;imag=a*d+b*c
    return f'{real}+{imag}i'
'''
CLOCK='''\
def minimum_time_difference(timePoints):
    seen=[False]*1440
    for text in timePoints:
        hour,minute=map(int,text.split(':'));value=hour*60+minute
        if seen[value]:return 0
        seen[value]=True
    first=previous=None;best=1440
    for value,present in enumerate(seen):
        if not present:continue
        if previous is not None:best=min(best,value-previous)
        else:first=value
        previous=value
    return min(best,1440-previous+first)
'''
SINGLETON='''\
def single_sorted_element(nums):
    lo=0;hi=len(nums)-1
    while lo<hi:
        mid=(lo+hi)//2
        if mid%2:mid-=1
        if nums[mid]==nums[mid+1]:lo=mid+2
        else:hi=mid
    return nums[lo]
'''
REVERSE='''\
def reverse_alternating_blocks(s,k):
    chars=list(s)
    for start in range(0,len(chars),2*k):
        left=start;right=min(start+k,len(chars))-1
        while left<right:
            chars[left],chars[right]=chars[right],chars[left];left+=1;right-=1
    return ''.join(chars)
'''
PIXEL_EXAMPLE=[list('WBWBBW'),list('WBWBBW'),list('WBWBBW'),list('WWBWBW')]
LONG_TEXT=('abcdefghijklmnopqrstuvwxyz'*385)[:10000]

BATCH={
532:entry('count_k_diff_pairs',[('nums','list[int]'),('k','int')],'int',['arrays','hash-maps'],
    ['1 <= len(nums) <= 10,000; -10,000,000 <= nums[i] <= 10,000,000; 0 <= k <= 10,000,000.',
     'Count distinct unordered VALUE pairs with absolute difference k. Each pair needs two different input indices, but repeated occurrences do not create additional value pairs.'],
    [([[3,1,4,1,5],2],'The distinct value pairs are (1,3) and (3,5), so return 2. The second occurrence of 1 does not create a third pair.'),
     ([[1,1,1,2],0],'Only the value pair (1,1) qualifies, so return 1. There are three index pairs of ones, but they represent one value pair; a single 2 cannot pair with itself.')],
    [a for a in ([[1],0],[[1],1],[[1,1],0],[[1,2],0],[[1,2],1],[[1,2],2],
        [[-5,-3],2],[[-1,0,1],1],[[1,1,2,2],1],[[1,1,1,1],0],[[3,3,1,1],2],
        [[0,0,1],0],[[-10000000,0,10000000],10000000],[[5,4,3,2,1],1],[[1,3,5,7],2])],
    PAIRS,[WEIGHTED_PAIRS,PAIRS.replace('sum(count>=2 for count in counts.values())','len(counts)')],
    ['Counts index-pair multiplicity instead of distinct value pairs.', 'Allows each singleton value to pair with itself when k is zero.'],
    pairs_oracle,random_pairs,
    ['Separate repeated occurrences from distinct values.',
     'For positive k, count each smaller value whose larger partner exists. For k=0, a value needs frequency at least two.',
     'Build a frequency map; return count(frequency>=2) when k=0, otherwise count(value+k present) over distinct keys.',
     'Use only the larger partner for each key so each unordered pair is counted once. Do not multiply the two frequencies.'],
    'Every positive-k value pair has one unique smaller member v and larger member '
    'v+k, so checking distinct keys counts it exactly once. For zero difference '
    'the same value needs two input positions, making frequency at least two '
    'necessary and sufficient. The independent oracle enumerates all index pairs '
    'then deduplicates their ordered value tuples.',
    'O(n)','O(n)',difficulty=5,
    stress=[([[7]*10000,0],1),([list(range(10000)),1],9999),
            ([[v for v in range(5000) for _ in range(2)],0],5000),
            ([[-10000000]*5000+[0]*5000,10000000],1)]),
533:entry('count_lonely_pixels',[('picture','list[list[str]]'),('target','int')],'int',['matrices','hash-maps'],
    ['Source 533 uses boards up to 200 by 200. This app explicitly supports 1 <= rows, columns <= 500 to cover source 531 as target=1.',
     'The board is rectangular and contains only B (black) or W (white). 1 <= target <= min(rows,columns).',
     'Count black pixels, not rows or columns. A qualifying pixel has exactly target black cells in its row and column, AND every row containing a black pixel in that column is identical in all columns.'],
    [([PIXEL_EXAMPLE,3],'Columns 1 and 3 each contain three black pixels in the three identical top rows. All six pixels qualify. Column 4 has four black pixels, so none there qualify.'),
     ([[list('BBW'),list('BWB'),list('WBB')],2],'Return 0: each row and column has two black pixels, but the rows sharing any black column are different. Matching counts alone are not enough.')],
    [[list(map(list,rows)),target] for rows,target in ((['B'],1),(['W'],1),(['BB','BB'],2),(['BW','WB'],1),
        (['BB','WW'],1),(['BW','BW'],1),(['WW','WW'],2),(['BWW','WBW','WWB'],1),
        (['WWB','WWB','WWB'],1),(['BBWW','BBWW','WWWW'],2),(['BBWW','BWBW','WWWW'],2),
        (['BBB','BBB','BBB'],3),(['BBB','BBB','BBB'],2),(['BBW','BBW','WWB'],2),(['BWB','BWB','WWW'],2))],
    PIXEL,[PIXEL_COUNTS,PIXEL.replace('answer+=copies*sum','answer+=sum')],
    ['Checks row and column counts but omits the identical-row condition.', 'Counts qualifying columns instead of all pixels in their identical row copies.'],
    pixel_oracle,random_pixel,
    ['Rows that are exactly equal can be grouped together.',
     'A qualifying row pattern must appear target times, have target black positions, and use columns whose total black count is target.',
     'Count row tuples and column black cells; for each row pattern with frequency target and target black cells, add frequency for every qualifying black column.',
     'A column can be spoiled by one black pixel in a different row pattern. Multiply by the number of identical rows because the answer counts pixels.'],
    'For a qualifying pixel, all target black cells in its column belong to '
    'identical rows. Hence its row pattern appears exactly target times. Conversely, '
    'a pattern with target copies and target black positions qualifies at each '
    'black column whose total is target: there can be no extra nonidentical row '
    'there. Grouping row tuples and counting columns takes O(rows*columns) time '
    'and space. The oracle directly inspects every black pixel and compares all '
    'rows contributing to its column without grouped-frequency reasoning.',
    'O(rows*columns)','O(rows*columns)',difficulty=5,
    stress=[([[['B']*200 for _ in range(200)],200],40000),
            ([[['B']*500 for _ in range(500)],500],250000),
            ([[['W']*500 for _ in range(500)],1],0),
            ([[['B' if r==c else 'W' for c in range(500)] for r in range(500)],1],500)]),
537:entry('multiply_complex_numbers',[('num1','str'),('num2','str')],'str',['math','strings','parsing'],
    ['Inputs represent real+imaginaryi with integer components in -100..100. The separator is always +, even before a negative imaginary component (for example, 1+-1i).',
     'Use i*i=-1 and return real+imaginaryi with integer components, including zero components. Do not remove the + separator before a negative result.'],
    [(['1+1i','1+1i'],'(1+i)^2=1+2i+i^2=2i. Return 0+2i, including the zero real component.'),
     (['1+-1i','1+-1i'],'(1-i)^2=-2i. Return 0+-2i: the format keeps its literal + separator before the negative imaginary component.')],
    [[a,b] for a,b in (('0+0i','1+2i'),('1+0i','2+3i'),('0+1i','0+1i'),('0+-1i','0+1i'),
        ('2+3i','4+5i'),('-2+3i','4+-5i'),('-1+-1i','-1+-1i'),('3+0i','-2+0i'),
        ('0+2i','3+0i'),('1+2i','1+-2i'),('-100+-100i','-100+-100i'),('100+-100i','100+100i'),
        ('100+100i','100+100i'),('-100+0i','100+0i'),('0+-100i','0+-100i'))],
    COMPLEX,[COMPLEX.replace('a*c-b*d','a*c+b*d'),COMPLEX.replace('a*d+b*c','a*d-b*c')],
    ['Treats i squared as +1 instead of -1.', 'Subtracts one imaginary cross term instead of adding both.'],
    complex_oracle,random_complex,
    ['Distribute the product across the real and imaginary terms.',
     'The two imaginary-only factors produce a real term because i squared is -1.',
     'Parse a,b,c,d; real=a*c-b*d, imaginary=a*d+b*c; format both integers with a literal + and trailing i.',
     'Keep negative signs inside their components. A negative imaginary result is written as real+-valuei, not by removing the separator.'],
    'Expanding (a+bi)(c+di) gives ac+(ad+bc)i+bd*i^2. Substitute i^2=-1 '
    'and collect the real and imaginary parts. The fixed component bounds make '
    'parsing, arithmetic and formatting constant-size work. The independent '
    'oracle multiplies Python complex values and formats their exact integer '
    'components; all possible products here are exactly representable.',
    'O(1)','O(1)',difficulty=5),
539:entry('minimum_time_difference',[('timePoints','list[str]')],'int',['arrays','counting','circular-order'],
    ['2 <= len(timePoints) <= 20,000; each entry is a valid 24-hour HH:MM time from 00:00 through 23:59.',
     'Return the shortest circular gap in minutes between any two entries, including across midnight. Repeated identical times give zero.'],
    [([['23:59','00:00']],'Return 1: midnight wraps the 24-hour clock. Subtracting the written minute counts without wrapping would incorrectly give 1439.'),
     ([['00:00','23:59','00:00']],'Return 0 because two separate entries are both 00:00. Do not discard duplicates before computing the answer.')],
    [[times] for times in (['00:00','12:00'],['12:34','12:35'],['01:00','02:00'],['00:01','23:59'],
        ['08:00','08:00'],['23:00','01:00'],['00:00','00:01'],['23:58','23:59'],
        ['00:10','12:00','23:50'],['12:00','12:01','00:00'],['06:00','18:00'],
        ['04:00','08:00','12:00'],['01:59','02:00'],['09:10','10:09'],['00:01','23:58'])],
    CLOCK,[CLOCK.replace('return min(best,1440-previous+first)','return best'),
           CLOCK.replace('if seen[value]:return 0','if seen[value]:continue')],
    ['Checks only adjacent times within the day and misses the last-to-first gap.', 'Discards duplicates, losing zero-minute pairs.'],
    clock_oracle,random_clock,
    ['There are only 1440 distinct minute positions in a day.',
     'Record occupied minutes and detect duplicates. The minimum gap is between adjacent occupied positions on the circle.',
     'Scan the 1440 positions in order, updating adjacent gaps, then also compare 1440-last+first.',
     'The wraparound comparison is required even for two entries. A repeated minute is already an optimal gap of zero.'],
    'Any nonadjacent pair on a circle contains an intervening occupied time '
    'and cannot improve on every intervening gap. Thus scan adjacent occupied '
    'minutes and include the wraparound gap. A 1440-slot occupancy table avoids '
    'sorting and immediately detects duplicates. The oracle enumerates every '
    'pair and compares both circular directions independently.',
    'O(n+1440)','O(1440)',difficulty=5,
    stress=[([['00:00']*20000],0),([[clock_string(i%1440) for i in range(20000)]],0),
            ([[clock_string(i) for i in range(1440)]],1),
            ([[clock_string(i) for i in range(0,1440,2)]],2)]),
540:entry('single_sorted_element',[('nums','list[int]')],'int',['arrays','binary-search'],
    ['1 <= len(nums) <= 100,000; 0 <= nums[i] <= 100,000. nums is sorted; every value occurs exactly twice except one value occurring once, so its length is odd.',
     'Return the singleton VALUE, not its index. Required algorithmic target: O(log n) time and O(1) extra space; use the sorted pair structure instead of a linear XOR or counting pass.'],
    [([[1,1,2,3,3,4,4,8,8]],'Return 2, the only value without a partner. Before it, pairs begin at even indices; after it, pairs begin at odd indices.'),
     ([[3,3,7,7,10,11,11]],'Return the value 10, not its index 4. Its position separates intact even-starting pairs from the shifted pairs to its right.')],
    [[values] for values in ([0],[42],[100000],[1,1,2],[1,2,2],[0,0,1,2,2],[0,1,1,2,2],
        [0,0,1,1,2],[1,1,3,3,5,7,7],[1,1,2,3,3,4,4],
        [0,0,1,1,2,2,3],[0,1,1,2,2,3,3],[1,1,2,2,3,4,4,5,5],
        [99998,99998,99999],[99999,100000,100000])],
    SINGLETON,[SINGLETON.replace('return nums[lo]','return lo'),SINGLETON.replace('if nums[mid]==nums[mid+1]:lo=mid+2','if nums[mid]==nums[mid+1]:return nums[mid]')],
    ['Returns the singleton index instead of its value.', 'Returns an intact pair value rather than searching beyond that pair.'],
    singleton_oracle,random_singleton,
    ['The unpaired value changes the parity of all later pair starts.',
     'Round the midpoint down to an even index and check that candidate pair.',
     'If nums[mid]==nums[mid+1], move lo to mid+2; otherwise keep mid by setting hi=mid. Stop at one remaining index.',
     'Both boundaries remain even. An intact pair means the singleton is strictly to its right; a broken pair means it is at mid or earlier. Return nums[lo].'],
    'Before the singleton, each pair starts at an even index; after it, pair '
    'starts are odd. Testing an even-aligned midpoint therefore identifies '
    'which half contains the singleton. The interval shrinks geometrically '
    'without copying slices or scanning input, using constant extra storage. '
    'An independent frequency oracle checks values, and instrumented sequences '
    'verify a logarithmic element-read bound. This differs from the existing '
    'unsorted Single Number exercise, whose O(n) XOR algorithm does not meet '
    'this explicit O(log n) requirement.',
    'O(log n)','O(1)',difficulty=5,
    stress=[([singleton_input(list(range(50000)),single)],single) for single in (0,25000,49999)]),
541:entry('reverse_alternating_blocks',[('s','str'),('k','int')],'str',['strings','two-pointers'],
    ['1 <= len(s) <= 10,000; lowercase English letters only; 1 <= k <= 10,000.',
     'Partition positions into blocks of 2*k starting at index zero. Reverse the first k characters of each block and keep its second k unchanged.',
     'If the last block has fewer than k characters, reverse all of them. Otherwise reverse just its first k. Return a new string.'],
    [(['abcdefg',2],'Blocks are abcd and efg. Reverse ab to ba and ef to fe, keeping cd and g unchanged: bacdfeg.'),
     (['abcdefgh',3],'The first block abcdef becomes cbadef. Only gh remains, fewer than k characters, so reverse both: cbadefhg.')],
    [[s,k] for s,k in (('a',1),('a',5),('ab',1),('ab',2),('ab',3),('abc',2),('abcd',2),
        ('abcde',2),('abcdef',2),('abcdefghi',2),('abc',3),('abcd',3),('abcde',3),
        ('abcdef',3),('aaaaa',2),('zyxwv',10))],
    REVERSE,[REVERSE.replace('right=min(start+k,len(chars))-1','right=min(start+2*k,len(chars))-1'),
             REVERSE.replace('range(0,len(chars),2*k)','range(0,len(chars),k)')],
    ['Reverses the entire 2k block instead of only its first half.', 'Reverses every k-sized block, including halves that must stay unchanged.'],
    reverse_oracle,random_reverse,
    ['The decision to reverse alternates by k-sized regions, starting with a reversed region.',
     'Visit starts 0,2k,4k,... and swap inward across at most k available characters.',
     'For each start in steps of 2k, use left=start and right=min(start+k,n)-1; swap until left>=right.',
     'The final short region needs no special extra loop: the clipped right endpoint handles it. Do not reverse the second half of any 2k block.'],
    'Each character lies in exactly one 2k block. Swapping its first min(k,remaining) '
    'characters realizes the required reversal while leaving the rest untouched. '
    'The mutable character buffer and returned string take O(n) space; all swaps '
    'together take O(n) time. The oracle independently computes the source index '
    'for each output position rather than swapping or slicing blocks.',
    'O(n)','O(n)',difficulty=3,
    stress=[([LONG_TEXT,k],reverse_oracle([LONG_TEXT,k])) for k in (1,2,4999,9999,10000)]),
}
