"""Bouncing ball, complete-day pairs, divisibility edits, paired averages, and XOR parity."""
from .import_batch_055 import entry

def child_oracle(a):
    n,k=a;position=0;direction=1
    for _ in range(k):
        if position+direction not in range(n):direction=-direction
        position+=direction
    return position
def random_child(r):return [r.randint(2,50),r.randint(0,1000)]
def day_oracle(a):return sum((a[0][i]+a[0][j])%24==0 for i in range(len(a[0])) for j in range(i+1,len(a[0])))
def random_day(r):return [[r.randint(1,1000) for _ in range(r.randint(1,40))]]
def divisible_oracle(a):return sum(min(value%3,3-value%3) for value in a[0])
def random_divisible(r):return [[r.randint(1,100) for _ in range(r.randint(1,50))]]
def average_oracle(a):
    values=a[0][:];answers=[]
    while values:
        low=min(values);values.remove(low);high=max(values);values.remove(high);answers.append((low+high)/2)
    return min(answers)
def random_average(r):return [[r.randint(1,100) for _ in range(2*r.randint(1,20))]]
def parity_oracle(a):return sum((x^y^z).bit_count()%2==0 for x in a[0] for y in a[1] for z in a[2])
def random_parity(r):return [[r.randint(0,100) for _ in range(r.randint(1,8))] for _ in range(3)]

CHILD='''\
def child_with_ball_after_seconds(n,k):
    period=2*(n-1);step=k%period
    return step if step<n else period-step
'''
DAY='''\
def count_complete_day_pairs(hours):
    counts=[0]*24;answer=0
    for value in hours:
        remainder=value%24;answer+=counts[-remainder%24];counts[remainder]+=1
    return answer
'''
DIVISIBLE='''\
def operations_to_multiples_of_three(nums):
    return sum(value%3!=0 for value in nums)
'''
AVERAGE='''\
def minimum_removed_extremes_average(nums):
    values=sorted(nums);answer=float('inf')
    for left,right in zip(values,values[::-1]):answer=min(answer,(left+right)/2)
    return answer
'''
PARITY='''\
def count_even_popcount_xor_triplets(a,b,c):
    return sum((x^y^z).bit_count()%2==0 for x in a for y in b for z in c)
'''

BATCH={
3178:entry('child_with_ball_after_seconds',[('n','int'),('k','int')],'int',['math','simulation','cycles'],['Children are indexed zero through n-1 in a line and child zero starts with the ball.','The ball moves one child per second and reverses direction at each endpoint.','Return the holder after k seconds.'],[([3,5],'The holders are 1,2,1,0,1, so child one has the ball.'),([5,6],'The ball reaches child four then returns to child two.')],[[n,k] for n,k in [(2,0),(2,1),(2,2),(3,1),(3,2),(3,3),(3,4),(3,5),(5,6),(5,8),(5,9),(10,9),(10,10),(4,100)]],CHILD,[CHILD.replace('2*(n-1)','n'),CHILD.replace('period-step','step-period')],['Uses n as the cycle length instead of the out-and-back period.','Reflects the second half in the wrong direction.'],child_oracle,random_child,['The holder sequence repeats after traveling from zero to n-1 and back.','Its period is 2*(n-1).','Reduce k by that period; positions before n move right, and later positions reflect back as period-step.','Modulo locates the same phase in the repeated deterministic motion.'],'O(1)','O(1)',3),
3184:entry('count_complete_day_pairs',[('hours','list[int]')],'int',['arrays','modular arithmetic','counting'],['Choose index pairs i<j.','A pair forms complete days when hours[i]+hours[j] is divisible by 24.','Return the number of qualifying pairs.'],[([[12,12,30,24,24]],'The two twelves pair, and the two multiples of 24 pair, giving two.'),([[72,48,24,3]],'The three multiples of 24 form three index pairs.')],[[x] for x in [[1],[12,12],[24,24],[1,23],[12,12,30,24,24],[72,48,24,3],[6,18,30],[1,2,3],[23,25,47],[0,24,48],[5,19,5,19],[8,16,32,40],[10,14,34],[100,20,44]]],DAY,[DAY.replace('%24','%12'),DAY.replace('counts[-remainder%24]','counts[remainder]')],['Counts sums divisible by twelve rather than by twenty-four.','Pairs equal remainders instead of complementary remainders.'],day_oracle,random_day,['Only each duration’s remainder modulo 24 matters.','Before storing a remainder r, count earlier values with remainder -r modulo 24.','Then increment the current remainder count.','Each earlier-later qualifying pair is counted exactly when its later endpoint is processed.'],'O(n)','O(1)',3),
3190:entry('operations_to_multiples_of_three',[('nums','list[int]')],'int',['arrays','modular arithmetic'],['One operation increments or decrements one array value by one.','Make every value divisible by three using the fewest operations.','Return the total number of operations.'],[([[1,2,3,4]],'One, two, and four each need one move; three needs none, totaling three.'),([[3,6,9]],'Every value is already divisible, so zero operations are needed.')],[[x] for x in [[1],[2],[3],[1,2,3,4],[3,6,9],[4,5,6],[10,11,12],[1,1,1],[2,2,2],[99,100],[7,8,9],[13,14,15],[20,21,22],[5,10,15]]],DIVISIBLE,[DIVISIBLE.replace('!=0','==0'),DIVISIBLE.replace('value%3','value%2')],['Counts already-divisible values instead of values needing a move.','Tests divisibility by two rather than three.'],divisible_oracle,random_divisible,['A remainder zero costs no operation.','Remainders one and two each cost exactly one by decrementing or incrementing.','Therefore count values whose remainder modulo three is nonzero.','Operations on separate values do not interact, so summing their individual minima is globally minimal.'],'O(n)','O(1)',3),
3194:entry('minimum_removed_extremes_average',[('nums','list[int]')],'float',['arrays','sorting'],['Repeatedly remove the smallest and largest remaining elements and record their average.','nums has even length.','Return the minimum recorded average.'],[([[7,8,3,4,15,13,4,1]],'Sorted extreme pairs average to 8, 8.5, 6, and 5.5; the minimum is 5.5.'),([[1,9]],'The only average is five.')],[[x] for x in [[1,9],[1,1],[1,2,3,4],[7,8,3,4,15,13,4,1],[5,5,5,5],[1,100,2,99],[10,20,30,40],[3,8,4,7,5,6],[1,2,100,101],[9,2,8,3],[4,1,7,2,6,3],[20,10],[6,6,1,1],[100,50,25,75]]],AVERAGE,[AVERAGE.replace('answer=min','answer=max'),AVERAGE.replace('(left+right)/2','(left-right)/2')],['Returns the maximum recorded average instead of the minimum.','Subtracts extremes rather than averaging their sum.'],average_oracle,random_average,['Sorting reveals the exact sequence of repeated minimum/maximum removals.','Pair the first with last, second with second-last, and so on.','Compute each pair’s average and retain the smallest.','Those symmetric sorted pairs are precisely the forced removal pairs, so their minimum is the requested result.'],'O(n log n)','O(n)',3),
3199:entry('count_even_popcount_xor_triplets',[('a','list[int]'),('b','list[int]'),('c','list[int]')],'int',['arrays','bit manipulation','enumeration'],['Choose one value from each of arrays a, b, and c.','XOR the three values and count the one bits in the result.','Return the number of triplets whose XOR has an even set-bit count.'],[([[1],[2],[3]],'One XOR two XOR three is zero, whose set-bit count is even, so one triplet qualifies.'),([[1,1],[2],[3]],'Both index-distinct choices from a produce zero XOR, so two triplets qualify.')],[[a,b,c] for a,b,c in [([1],[2],[3]),([0],[0],[0]),([1],[1],[1]),([1,1],[2],[3]),([1,2],[3],[4]),([0,1],[0,1],[0,1]),([7],[8],[15]),([2,4],[1,3],[5]),([10,20],[30],[40]),([1],[2,3],[4,5]),([3,3],[3,3],[3]),([8,16],[4,2],[1]),([5,6,7],[1],[2]),([100],[50],[25])]],PARITY,[PARITY.replace('%2==0','%2==1'),PARITY.replace('x^y^z','x|y|z')],['Counts odd set-bit parity instead of even.','Combines values with OR instead of XOR.'],parity_oracle,random_parity,['The source-I limits permit direct Cartesian enumeration.','For each triplet compute XOR and integer bit_count.','Count it when that count modulo two is zero.','Every index triplet appears once in the three nested loops and is classified by the exact predicate.'],'O(|a||b||c|)','O(1)',3),
}
BATCH[3194]['comparator']='float'
BATCH[3194]['wrong'][0]=AVERAGE.replace("answer=float('inf')","answer=float('-inf')").replace('answer=min','answer=max')
