"""Candy counts, required letters, access windows, paired swaps, and binary separation."""
from .import_batch_055 import entry


def candies_oracle(args):
    total,limit=args
    return sum(first+second<=total and total-first-second<=limit for first in range(limit+1) for second in range(limit+1))


def random_candies(rng):return [rng.randint(1,40),rng.randint(1,20)]


def string_count_oracle(args):
    length=args[0];mod=1_000_000_007
    power=lambda base,exponent:pow(base,exponent,mod)
    e_short=(power(25,length)+(length*power(25,length-1) if length else 0))%mod
    pair=(power(24,length)+(length*power(24,length-1) if length else 0))%mod
    triple=(power(23,length)+(length*power(23,length-1) if length else 0))%mod
    return (power(26,length)-2*power(25,length)-e_short+power(24,length)+2*pair-triple)%mod


def random_string_count(rng):return [rng.randint(1,1000)]


def access_oracle(args):
    records=args[0];names=sorted({name for name,_ in records});answer=[]
    for name in names:
        times=sorted(int(value[:2])*60+int(value[2:]) for employee,value in records if employee==name)
        if any(times[right]-times[left]<60 for left in range(len(times)) for right in range(left+2,len(times))):answer.append(name)
    return answer


def minute_text(value):return f'{value//60:02d}{value%60:02d}'


def random_access(rng):
    names=['a','b','c'];records=[]
    for _ in range(rng.randint(1,20)):records.append([rng.choice(names),minute_text(rng.randint(0,1439))])
    return [records]


def last_elements_oracle(args):
    first,second=args;best=len(first)+1
    for mask in range(1<<len(first)):
        a=first.copy();b=second.copy()
        for index in range(len(first)):
            if mask>>index&1:a[index],b[index]=b[index],a[index]
        if a[-1]==max(a) and b[-1]==max(b):best=min(best,mask.bit_count())
    return -1 if best>len(first) else best


def random_last_elements(rng):
    size=rng.randint(1,8)
    return [[rng.randint(1,15) for _ in range(size)],[rng.randint(1,15) for _ in range(size)]]


def separate_oracle(args):
    values=list(args[0]);moves=0;changed=True
    while changed:
        changed=False
        for index in range(len(values)-1):
            if values[index:index+2]==['1','0']:
                values[index],values[index+1]=values[index+1],values[index];moves+=1;changed=True
    return moves


def random_separate(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,25)))]


CANDIES='''def distribute_candies_three_children(n,limit):
    if n>3*limit:return 0
    def choose2(value):return value*(value-1)//2 if value>=2 else 0
    answer=choose2(n+2)-3*choose2(n-limit+1)+3*choose2(n-2*limit)
    return max(0,answer)
'''


STRING_COUNT='''def count_rearrangeable_leet_strings(n):
    mod=1000000007;states={(0,0,0):1}
    for _ in range(n):
        following={}
        for (has_l,e_count,has_t),count in states.items():
            options=[((has_l,e_count,has_t),23),((1,e_count,has_t),1),((has_l,min(2,e_count+1),has_t),1),((has_l,e_count,1),1)]
            for state,multiplier in options:following[state]=(following.get(state,0)+count*multiplier)%mod
        states=following
    return states.get((1,2,1),0)
'''


ACCESS='''def high_access_employees(access_times):
    from collections import defaultdict
    grouped=defaultdict(list)
    for name,text in access_times:grouped[name].append(int(text[:2])*60+int(text[2:]))
    answer=[]
    for name,times in grouped.items():
        times.sort()
        if any(times[index]-times[index-2]<60 for index in range(2,len(times))):answer.append(name)
    return answer
'''


LAST_ELEMENTS='''def minimum_last_element_swaps(nums1,nums2):
    def evaluate(last1,last2):
        operations=0
        for first,second in zip(nums1[:-1],nums2[:-1]):
            if first<=last1 and second<=last2:continue
            if first<=last2 and second<=last1:operations+=1
            else:return float('inf')
        return operations
    answer=min(evaluate(nums1[-1],nums2[-1]),1+evaluate(nums2[-1],nums1[-1]))
    return -1 if answer==float('inf') else answer
'''


SEPARATE='''def minimum_black_white_swaps(s):
    black=0;answer=0
    for char in s:
        if char=='1':black+=1
        else:answer+=black
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2929:entry('distribute_candies_three_children',[('n','int'),('limit','int')],'int',['combinatorics','inclusion-exclusion','math'],['n and limit are positive integers.','Distribute all n identical candies among three distinct children.','Count assignments where every child receives at most limit candies.'],[([5,2],'The valid distributions are the three permutations of (1,2,2).'),([3,3],'All ten nonnegative three-part compositions of three respect the limit.')],[[n,l] for n,l in [(1,1),(2,1),(3,1),(4,1),(2,2),(4,2),(6,2),(7,2),(5,3),(9,3),(10,3),(10,10),(20,7),(30,9)]],CANDIES,[CANDIES.replace('-3*choose2(n-limit+1)','-choose2(n-limit+1)'),CANDIES.replace('+3*choose2(n-2*limit)','')],['Subtracts only one child-limit violation instead of all three symmetric cases.','Omits the overlap correction for two children exceeding the limit.'],candies_oracle,random_candies,lesson('Unbounded three-child distributions are counted by stars and bars.','Apply inclusion-exclusion to assignments where one or more children exceed limit.','Compute C(n+2,2)-3C(n-limit+1,2)+3C(n-2limit,2), treating invalid combinations as zero.','Shifting an over-limit child down by limit+1 maps violations to smaller unrestricted compositions; inclusion-exclusion corrects their overlaps exactly.'),'O(1)','O(1)',5),
2930:entry('count_rearrangeable_leet_strings',[('n','int')],'int',['dynamic programming','combinatorics','strings'],['n is a positive integer.','Count lowercase strings whose multiset contains at least one l, two e characters, and one t, allowing rearrangement to contain leet.','Return the count modulo 1,000,000,007.'],[([4],'Exactly the twelve distinct permutations of the multiset e,e,l,t qualify.'),([10],'The qualifying count modulo 1,000,000,007 is 83,943,898.')],[[n] for n in [1,2,3,5,6,7,8,9,11,12,20,50,100,1000]],STRING_COUNT,[STRING_COUNT.replace('min(2,e_count+1)','min(1,e_count+1)').replace('(1,2,1)','(1,1,1)'),STRING_COUNT.replace('),23)', '),24)')],['Requires only one e rather than two.','Treats twenty-four ordinary letters as distinct options instead of twenty-three.'],string_count_oracle,random_string_count,lesson('Only capped counts of l, e, and t matter; every other letter shares one transition.','Track an eight-ish state space with l and t capped at one and e capped at two.','For each position, add transitions for 23 other letters, l, e, and t modulo the limit.','The capped state records exactly whether the final multiset meets each requirement, and grouping the irrelevant letters preserves their multiplicity.'),'O(n)','O(1)',5),
2933:entry('high_access_employees',[('access_times','list[list[str]]')],'list[str]',['sorting','hash maps','sliding windows'],['Each record contains a lowercase employee name and a same-day four-digit 24-hour time.','An employee qualifies after at least three accesses spanning strictly less than sixty minutes.','Do not wrap across midnight; return qualifying names in any order.'],[([[['a','0549'],['b','0457'],['a','0532'],['a','0621'],['b','0540']]],'Employee a has three accesses from 05:32 through 06:21.'),([[['d','0002'],['c','0808'],['c','0829'],['e','0215'],['d','1508'],['d','1444'],['d','1410'],['c','0809']]],'Both c and d have a three-access window shorter than one hour.')],[[r] for r in [[['a','0000']],[['a','0000'],['a','0030'],['a','0059']],[['a','0000'],['a','0030'],['a','0100']],[['a','2350'],['a','0005'],['a','0010']],[['a','1200'],['a','1200'],['a','1200']],[['a','1000'],['b','1000'],['a','1020'],['b','1020'],['a','1040'],['b','1100']],[['x','0800'],['x','0859'],['x','0900']],[['x','0800'],['x','0830'],['x','0859'],['x','1200']],[['a','0100'],['b','0200'],['c','0300']],[['q','2300'],['q','2330'],['q','2359']],[['q','2300'],['q','2330'],['q','0000']],[['m','0615'],['m','0645'],['m','0714']],[['m','0615'],['m','0645'],['m','0715']],[['a','1111'],['b','1111'],['a','1122'],['b','1122'],['a','1133'],['b','1133']]]],ACCESS,[ACCESS.replace('<60','<=60'),ACCESS.replace('times[index]-times[index-2]','times[index]-times[index-1]')],['Includes accesses exactly sixty minutes apart.','Checks only the latest adjacent pair rather than the span across three accesses.'],access_oracle,random_access,lesson('After sorting one employee’s times, any qualifying group contains three consecutive accesses within the sorted list.','Convert times to minutes, group by name, and compare each time with the one two positions earlier.','Qualify when times[i]-times[i-2]<60 for any i.','If any three accesses fit, their earliest three consecutive representatives fit; conversely every detected triple directly witnesses the condition.'),'O(n log n)','O(n)',5),
2934:entry('minimum_last_element_swaps',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','enumeration','greedy'],['Both positive-integer arrays have equal nonzero length.','One operation swaps values at the same index across arrays.','Minimize operations so each final last element is a maximum of its array, or return -1.'],[([[1,2,7],[4,5,3]],'Swapping the last pair makes final maxima three and seven in one operation.'),([[2,3,4,5,9],[8,8,4,4,4]],'Swap the last pair and index three to satisfy both arrays in two operations.')],[[a,b] for a,b in [([1],[2]),([1,2],[2,1]),([1,2],[1,2]),([2,1],[1,2]),([1,5,4],[2,5,3]),([3,3,3],[3,3,3]),([1,4,2],[3,2,5]),([5,1,5],[1,5,1]),([2,8,4,6],[7,3,5,9]),([9,1,2],[3,8,7]),([1,10,5,6],[2,9,7,8]),([4,2,6,3],[1,5,2,7]),([7,6,5,4],[1,2,3,8]),([2,2,9,1],[8,3,4,10])]],LAST_ELEMENTS,[LAST_ELEMENTS.replace('1+evaluate(nums2[-1],nums1[-1])','evaluate(nums2[-1],nums1[-1])'),LAST_ELEMENTS.replace('first<=last2 and second<=last1','first<last2 and second<last1')],['Forgets to count swapping the final pair in the second orientation.','Uses strict limits for swapped earlier pairs and rejects values equal to the final maximum.'],last_elements_oracle,random_last_elements,lesson('Only two final-value orientations are possible: keep or swap the last pair.','For each orientation, every earlier pair is independently kept if it fits or swapped if that fits.','Count forced swaps, reject a pair fitting neither orientation, and include the last swap cost when applicable.','Once final bounds are fixed, choosing keep whenever possible is never worse; evaluating both exhaustive final orientations yields the global minimum.'),'O(n)','O(1)',5),
2938:entry('minimum_black_white_swaps',[('s','str')],'int',['greedy','strings','counting'],['s is a nonempty binary string where one is black and zero is white.','One operation swaps adjacent balls.','Return the minimum swaps needed to place every zero before every one.'],[(['101'],'The leading black ball crosses the middle white ball once.'),(['100'],'The black ball crosses both following white balls in two swaps.')],[[s] for s in ['0','1','01','10','00','11','101','010','1100','0011','111000','10001','010101','101010']],SEPARATE,[SEPARATE.replace("if char=='1'","if char=='0'"),SEPARATE.replace('answer+=black','answer+=1')],['Counts white-before-black pairs, the already-correct orientation.','Adds one per encountered white ball instead of one per preceding black inversion.'],separate_oracle,random_separate,lesson('Each black-before-white inversion must cross once under adjacent swaps.','Scan left to right, counting prior black balls; every white ball contributes that count.','Increment black on one, otherwise add black to the answer.','An adjacent swap fixes exactly one inversion, and bubble movement can fix all inversions in that many swaps, so the inversion count is both lower bound and attainable.'),'O(n)','O(1)',5),
}
BATCH[2933]['comparator']='unordered'
