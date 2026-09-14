"""First slice of workbook batch 131."""

from collections import Counter
from math import gcd

from .import_batch_055 import entry


def equal_frequency_oracle(args):
    word=args[0]
    for index in range(len(word)):
        counts=Counter(word[:index]+word[index+1:])
        if not counts or len(set(counts.values()))==1:return True
    return False


def random_equal_frequency(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(2,18)))]


def factors_oracle(args):
    a,b=args
    return sum(a%value==0 and b%value==0 for value in range(1,min(a,b)+1))


def random_factors(rng): return [rng.randint(1,100),rng.randint(1,100)]


def employee_oracle(args):
    _,logs=args;previous=0;best_time=-1;answer=0
    for employee,end in logs:
        duration=end-previous;previous=end
        if duration>best_time or duration==best_time and employee<answer:best_time=duration;answer=employee
    return answer


def random_employee(rng):
    n=rng.randint(1,15);time=0;logs=[]
    for _ in range(rng.randint(1,15)):
        time+=rng.randint(1,10);logs.append([rng.randrange(n),time])
    return [n,logs]


def clock_oracle(args):
    pattern=args[0];answer=0
    for hour in range(24):
        for minute in range(60):
            candidate=f'{hour:02d}:{minute:02d}'
            if all(a=='?' or a==b for a,b in zip(pattern,candidate)):answer+=1
    return answer


def random_clock(rng):
    candidate=f'{rng.randrange(24):02d}:{rng.randrange(60):02d}'
    return [''.join('?' if char!=':' and rng.random()<.5 else char for char in candidate)]


def positive_oracle(args):
    values=set(args[0]);possible=[value for value in values if value>0 and -value in values]
    return max(possible,default=-1)


def random_positive(rng):
    return [[rng.randint(-20,20) for _ in range(rng.randint(1,25))]]


FREQUENCY='''\
def can_equalize_frequency_by_removal(word):
    from collections import Counter
    counts=Counter(word)
    for char in list(counts):
        counts[char]-=1
        remaining=[value for value in counts.values() if value]
        if len(set(remaining))<=1:return True
        counts[char]+=1
    return False
'''

FACTORS='''\
def number_of_common_factors(a,b):
    common=__import__('math').gcd(a,b)
    return sum(common%value==0 for value in range(1,common+1))
'''

EMPLOYEE='''\
def longest_working_employee(n,logs):
    previous=0;best=-1;answer=n
    for employee,end in logs:
        duration=end-previous;previous=end
        if duration>best or duration==best and employee<answer:best=duration;answer=employee
    return answer
'''

CLOCK='''\
def count_valid_clock_times(time):
    answer=0
    for hour in range(24):
        for minute in range(60):
            candidate=f'{hour:02d}:{minute:02d}'
            if all(given=='?' or given==actual for given,actual in zip(time,candidate)):answer+=1
    return answer
'''

POSITIVE='''\
def largest_positive_with_negative(nums):
    values=set(nums)
    return max((value for value in values if value>0 and -value in values),default=-1)
'''


BATCH={
2423:entry('can_equalize_frequency_by_removal',[('word','str')],'bool',['strings','counting','enumeration'],['Remove exactly one occurrence from the lowercase string.','After removal, every remaining distinct letter must have the same positive frequency.','A one-letter remainder is valid.'],[(['abcc'],'Removing one c leaves a, b, and c each occurring once.'),(['aazz'],'Any removal leaves frequencies one and two, so equality is impossible.')],[[s] for s in ['aa','ab','aaa','aab','abb','abc','aabb','aaab','aaabb','abcdd','zzzz','abbbc','aabbcc','aaaabbbb']],FREQUENCY,[FREQUENCY.replace('if len(set(remaining))<=1','if len(set(counts.values()))<=1'),FREQUENCY.replace('for char in list(counts)','for char in list(counts)[:1]')],['Keeps the removed letter’s zero frequency in the comparison.','Tries removing only the first distinct letter instead of every possible frequency group.'],equal_frequency_oracle,random_equal_frequency,['Count the frequency of each distinct letter.','Try decrementing one occurrence from each possible letter in turn.','Ignore a resulting zero count and test whether all remaining positive counts are equal; then restore the count.','Every legal removal chooses one letter, so enumerating distinct letters covers all outcomes and accepts exactly an equal-frequency remainder.'],'O(n+alphabet^2)','O(alphabet)',3),
2427:entry('number_of_common_factors',[('a','int'),('b','int')],'int',['math','number theory'],['A common factor is a positive integer dividing both a and b.','Count distinct factor values, including one and the numbers themselves when applicable.','a and b are positive integers.'],[([12,6],'The common factors are one, two, three, and six.'),([25,30],'Only one and five divide both values.')],[[a,b] for a,b in [(1,1),(1,10),(2,4),(6,6),(8,12),(7,13),(36,48),(100,10),(17,34),(49,14),(81,27),(64,96),(99,66),(13,13)]],FACTORS,[FACTORS.replace('common+1','common'),FACTORS.replace("gcd(a,b)",'min(a,b)')],['Stops before testing the gcd itself, omitting one guaranteed common factor.','Tests divisors of the smaller input even when they do not divide the other input.'],factors_oracle,random_factors,['Every common factor divides gcd(a,b), and every divisor of the gcd divides both inputs.','Compute the greatest common divisor first.','Count integers from one through the gcd that divide it evenly.','The divisor equivalence makes this count exactly the set of common factors.'],'O(gcd(a,b))','O(1)',3),
2432:entry('longest_working_employee',[('n','int'),('logs','list[list[int]]')],'int',['arrays','simulation'],['Tasks occur consecutively in log order; each log is [employee_id,end_time].','A task duration is its end time minus the preceding task end, or minus zero for the first task.','Return the employee with the longest single task, breaking ties by smaller id.'],[([10,[[0,3],[2,5],[0,9],[1,15]]],'Durations are three, two, four, and six; employee one owns the longest task.'),([26,[[1,1],[3,7],[2,12],[7,17]]],'The last three durations are six, five, and five, so employee three wins.')],[[n,l] for n,l in [(1,[[0,1]]),(2,[[1,5]]),(3,[[2,2],[1,5]]),(4,[[3,4],[2,8]]),(5,[[4,2],[1,4],[3,6]]),(3,[[2,3],[1,6],[0,9]]),(10,[[9,10],[1,11]]),(4,[[2,1],[3,10]]),(6,[[5,2],[4,3],[3,9]]),(3,[[1,4],[2,5],[1,10]]),(8,[[7,7],[0,8],[6,9]]),(5,[[3,3],[2,7],[1,8]]),(9,[[8,1],[7,3],[6,6],[5,10]]),(2,[[1,2],[0,4]])]],EMPLOYEE,[EMPLOYEE.replace('duration=end-previous','duration=end'),EMPLOYEE.replace('employee<answer','employee>answer')],['Uses cumulative end times as durations instead of subtracting the prior end.','Breaks equal-duration ties in favor of the larger employee id.'],employee_oracle,random_employee,['Keep the previous task’s ending time.','For each log compute duration=end-previous, then advance previous.','Replace the answer for a longer duration or an equal duration with smaller employee id.','Each duration is computed once from consecutive endpoints and the comparison implements the exact maximum and tie rules.'],'O(logs)','O(1)',3),
2437:entry('count_valid_clock_times',[('time','str')],'int',['strings','enumeration'],['The pattern has HH:MM format and each question mark may be any digit.','A valid time has hours 00 through 23 and minutes 00 through 59.','Count all valid replacements matching every fixed character.'],[(['?5:00'],'Only hours 05 and 15 match, giving two valid times.'),(['0?:0?'],'Ten hour choices and ten minute-unit choices give one hundred valid times.')],[[s] for s in ['??:??','00:00','23:59','24:00','?0:00','1?:30','2?:00','??:59','12:??','??:0?','0?:??','?3:?5','22:6?','1?:?0']],CLOCK,[CLOCK.replace('range(24)','range(23)'),CLOCK.replace('range(60)','range(59)')],['Omits hour 23 from enumeration.','Omits minute 59 from enumeration.'],clock_oracle,random_clock,['There are only 24*60 valid concrete times.','Enumerate each hour and minute and format it with leading zeroes as HH:MM.','A candidate matches when every pattern position is ? or equals the candidate character.','Enumeration visits every valid clock time exactly once, so counting matches is complete and duplicate-free.'],'O(1)','O(1)',3),
2441:entry('largest_positive_with_negative',[('nums','list[int]')],'int',['arrays','hash sets'],['Find a positive integer k for which both k and -k occur in nums.','Return the greatest such k.','Return -1 when no positive/negative pair exists; zero does not qualify.'],[([[-1,2,-3,3]],'Both three and negative three occur, and three is the greatest qualifying value.'),([[-1,10,6,7,-7,1]],'One and seven have negatives present, so seven is returned.')],[[a] for a in [[1],[-1],[1,-1],[2,-2,3,-3],[0,0],[-5,5,10],[-10,10,-20,20],[1,2,3],[-1,-2,-3],[4,-4,4],[100,-100,99,-99],[7,-8,8],[-2,1,2,-1],[0,6,-6,5,-5]]],POSITIVE,[POSITIVE.replace('value>0','value>=0'),POSITIVE.replace('max(','min(',1)],['Allows zero to qualify when both occurrences are the same numeric value.','Returns the smallest qualifying positive value instead of the largest.'],positive_oracle,random_positive,['Put all input values in a set.','Inspect positive values whose negation is also in the set.','Return the maximum qualifying value, using -1 when the candidate set is empty.','Set membership checks both signs directly, and maximizing the complete candidate set applies the requested choice.'],'O(n)','O(n)',3),
}

BATCH[2427]['wrong'][1] = '''\
def number_of_common_factors(a,b):
    common=min(a,b)
    return sum(common%value==0 for value in range(1,common+1))
'''
BATCH[2427]['wrong_reasons'][1] = 'Counts every divisor of the smaller input even when it does not divide the other input.'
