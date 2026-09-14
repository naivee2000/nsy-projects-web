"""First slice of workbook batch 132."""

from fractions import Fraction
from itertools import combinations
from math import isqrt

from .import_batch_055 import entry


def temperature_oracle(args):
    c=Fraction(str(args[0]));return [float(c+Fraction(27315,100)),float(c*Fraction(9,5)+32)]


def random_temperature(rng): return [rng.randint(0,10000)/100]


def unequal_oracle(args):
    nums=args[0]
    return sum(len({nums[i],nums[j],nums[k]})==3 for i,j,k in combinations(range(len(nums)),3))


def random_unequal(rng): return [[rng.randint(1,8) for _ in range(rng.randint(3,18))]]


def cuts_oracle(args):
    n=args[0]
    if n==1:return 0
    # Enumerate whether diameters (two pieces) alone can make n equal sectors.
    return n//2 if n%2==0 else n


def random_cuts(rng): return [rng.randint(1,100)]


def pivot_oracle(args):
    n=args[0]
    for pivot in range(1,n+1):
        if sum(range(1,pivot+1))==sum(range(pivot,n+1)):return pivot
    return -1


def random_pivot(rng): return [rng.randint(1,1000)]


def circular_oracle(args):
    words=args[0].split()
    return all(words[index][-1]==words[(index+1)%len(words)][0] for index in range(len(words)))


def random_circular(rng):
    count=rng.randint(1,8);words=[];first=rng.choice('abcde');current=first
    for _ in range(count):
        end=rng.choice('abcde');words.append(current+rng.choice('abcde')+end);current=end
    if rng.random()<.5:words[-1]=words[-1][:-1]+first
    return [' '.join(words)]


TEMPERATURE='''\
def convert_temperature(celsius):
    return [celsius+273.15,celsius*1.8+32]
'''

UNEQUAL='''\
def count_unequal_triplets(nums):
    counts=__import__('collections').Counter(nums);left=0;right=len(nums);answer=0
    for frequency in counts.values():
        right-=frequency;answer+=left*frequency*right;left+=frequency
    return answer
'''

CUTS='''\
def minimum_circle_cuts(n):
    if n==1:return 0
    return n//2 if n%2==0 else n
'''

PIVOT='''\
def find_pivot_integer(n):
    total=n*(n+1)//2;root=__import__('math').isqrt(total)
    return root if root*root==total else -1
'''

CIRCULAR='''\
def is_circular_sentence(sentence):
    words=sentence.split()
    return all(words[index][-1]==words[(index+1)%len(words)][0] for index in range(len(words)))
'''


BATCH={
2469:entry('convert_temperature',[('celsius','float')],'list[float]',['math','simulation'],['Return [kelvin,fahrenheit] in that order.','Kelvin equals celsius+273.15.','Fahrenheit equals celsius*1.8+32; numeric answers use floating-point tolerance.'],[([36.5],'Thirty-six point five Celsius converts to 309.65 Kelvin and 97.7 Fahrenheit.'),([0.0],'Zero Celsius converts to 273.15 Kelvin and 32 Fahrenheit.')],[[c] for c in [1.0,100.0,37.0,25.5,10.25,99.99,273.15,50.0,12.34,75.75,0.01,42.42,18.0,88.8]],TEMPERATURE,[TEMPERATURE.replace('273.15','273'),TEMPERATURE.replace('1.8','1.6')],['Uses an imprecise Kelvin offset.','Uses the wrong Celsius-to-Fahrenheit scale factor.'],temperature_oracle,random_temperature,['Apply the two independent conversion formulas.','Add 273.15 for Kelvin.','Multiply by 1.8 and add 32 for Fahrenheit, returning Kelvin first.','Both entries are direct affine unit conversions, so evaluating the given formulas produces the unique result.'],'O(1)','O(1)',3),
2475:entry('count_unequal_triplets',[('nums','list[int]')],'int',['arrays','counting','combinatorics'],['Count index triples i<j<k whose three values are pairwise different.','Equal values at different indexes remain separate occurrences.','Return the number of valid triples.'],[([[4,4,2,4,3]],'Choosing one of three fours together with two and three gives three unequal triplets.'),([[1,1,1,1]],'No triple can contain three different values.')],[[a] for a in [[1,2,3],[1,1,2],[1,2,2],[1,2,3,4],[1,1,2,2,3,3],[1,2,1,3],[5,6,7,5],[1,1,1,2,3],[0,1,2],[9,8,9,7,8],[1,2,3,1,2,3],[4,5,4,6,7],[2,2,3,4,4],[1,1,2,3,4]]],UNEQUAL,[UNEQUAL.replace('left*frequency*right','left*right'),UNEQUAL.replace('right-=frequency','right-=1')],['Forgets the number of choices within the current value group.','Removes only one occurrence from the right side instead of the full equal-value group.'],unequal_oracle,random_unequal,['Group equal values by frequency.','Process each value group as the middle value of a triple.','Multiply occurrences already processed, the current frequency, and occurrences in later groups.','Every three-value choice has one uniquely ordered middle group, so it is counted exactly once with all index multiplicities.'],'O(n)','O(n)',3),
2481:entry('minimum_circle_cuts',[('n','int')],'int',['math','geometry'],['Cuts are straight lines across the circle.','Produce exactly n equal sectors.','Return the minimum number of cuts; one sector requires no cut.'],[([4],'Two perpendicular diameter cuts produce four equal sectors.'),([3],'Three radius cuts from the center are needed for three equal sectors.')],[[n] for n in [1,2,5,6,7,8,9,10,11,12,25,50,99,100]],CUTS,[CUTS.replace('if n==1:return 0','if n==1:return 1'),CUTS.replace('n//2','n')],['Uses one cut even when the untouched circle already forms one sector.','Fails to exploit that each diameter cut creates two equal sectors for even n.'],cuts_oracle,random_cuts,['Handle n=1 separately with zero cuts.','For even n, each diameter contributes two opposite sector boundaries.','For odd n, no boundary can be paired with an opposite one, so use n radii; return n/2 for even n.','Opposite boundaries coincide on one straight cut exactly in the even case, establishing both constructions and lower bounds.'],'O(1)','O(1)',3),
2485:entry('find_pivot_integer',[('n','int')],'int',['math','prefix sums'],['Find x from one through n such that 1+...+x equals x+...+n.','Return x when it exists, otherwise -1.','Both sums include x.'],[([8],'The sums one through six and six through eight both equal twenty-one, so the pivot is six.'),([4],'No integer from one through four balances the two inclusive sums.')],[[n] for n in [1,2,3,5,6,7,9,10,20,24,35,49,50,100]],PIVOT,[PIVOT.replace('total=n*(n+1)//2','total=n*(n-1)//2'),PIVOT.replace('root*root==total','root*root<=total')],['Uses the sum through n-1 instead of the sum through n.','Returns the floor square root even when the triangular total is not a perfect square.'],pivot_oracle,random_pivot,['Let T=n(n+1)/2 be the total sum.','Balancing inclusive sums gives x squared = T.','Take the integer square root of T and return it only when its square equals T.','The algebra is reversible, so a perfect-square triangular total is necessary and sufficient for an integer pivot.'],'O(1)','O(1)',3),
2490:entry('is_circular_sentence',[('sentence','str')],'bool',['strings','simulation'],['Words are separated by single spaces.','For every adjacent pair, the earlier word’s last character must equal the later word’s first.','The final word must also connect back to the first word.'],[(['leetcode exercises sound delightful'],'Each word ending matches the next beginning, and delightful ends with l, matching leetcode.'),(['Leetcode is cool'],'The first word ends with e while the next begins with i, so the sentence is not circular.')],[[s] for s in ['a','aa','ab ba','ab bc ca','ab bc cd','hello orange elephant tea','abc cba','x y','xy yx','level','ab ba ac','cat tiger rat','one eagle eel','az zebra apple']],CIRCULAR,[CIRCULAR.replace('%len(words)',''),CIRCULAR.replace('words[index][-1]','words[index][0]')],['Checks only consecutive pairs and indexes past the final word instead of wrapping to the first.','Compares first characters rather than each word’s ending to the next beginning.'],circular_oracle,random_circular,['Split the sentence into words.','For each index, compare its last character with the first character of the next word.','Use modulo word count so the word after the final word is the first word.','Those comparisons are exactly every edge in the required cycle, including the wraparound edge.'],'O(n)','O(words)',3),
}
BATCH[2469]['comparator']='float_list'
BATCH[2490]['wrong'][0]='''\
def is_circular_sentence(sentence):
    words=sentence.split()
    return all(words[index][-1]==words[index+1][0] for index in range(len(words)-1))
'''
BATCH[2490]['wrong_reasons'][0]='Checks adjacent words but omits the required final-to-first connection.'
