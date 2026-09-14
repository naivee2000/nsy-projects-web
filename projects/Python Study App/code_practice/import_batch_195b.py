"""Even OR, unequal word distance, decimal components, alternating sums, and score splits."""
from .import_batch_055 import entry

def even_oracle(a):
    out=0
    for v in a[0]:
        if v%2==0:out|=v
    return out
def random_even(r):return [[r.randint(0,1000) for _ in range(r.randint(1,50))]]
def distance_oracle(a):
    words=a[0];return max((j-i+1 for i in range(len(words)) for j in range(i+1,len(words)) if words[i]!=words[j]),default=0)
def random_distance(r):return [[r.choice(['a','b','c','aa']) for _ in range(r.randint(1,30))]]
def decimal_oracle(a):
    n=a[0];place=1;out=[]
    while n:
        if n%10:out.append((n%10)*place)
        n//=10;place*=10
    return out[::-1]
def random_decimal(r):return [r.randint(1,10**9)]
def alternating_oracle(a):return sum(v if i%2==0 else -v for i,v in enumerate(a[0]))
def random_alternating(r):return [[r.randint(-100,100) for _ in range(r.randint(1,50))]]
def score_oracle(a):
    vals=[ord(c)-96 for c in a[0]];return any(sum(vals[:i])==sum(vals[i:]) for i in range(1,len(vals)))
def random_score(r):return [''.join(r.choice('abcdef') for _ in range(r.randint(2,30)))]

EVEN='''def bitwise_or_of_even_values(nums):
    answer=0
    for value in nums:
        if value%2==0:answer|=value
    return answer
'''
DISTANCE='''def maximum_unequal_word_distance(words):
    answer=0
    for i in range(len(words)):
        for j in range(i+1,len(words)):
            if words[i]!=words[j]:answer=max(answer,j-i+1)
    return answer
'''
DECIMAL='''def decimal_place_components(n):
    components=[];place=1
    while n:
        digit=n%10
        if digit:components.append(digit*place)
        n//=10;place*=10
    return components[::-1]
'''
ALTERNATING='''def alternating_index_sum(nums):
    return sum(value if i%2==0 else -value for i,value in enumerate(nums))
'''
SCORE='''def has_equal_alphabet_score_split(s):
    total=sum(ord(char)-96 for char in s);left=0
    for char in s[:-1]:
        left+=ord(char)-96
        if left==total-left:return True
    return False
'''

BATCH={
3688:entry('bitwise_or_of_even_values',[('nums','list[int]')],'int',['arrays','bit manipulation'],['Select only even values from nums.','Return their cumulative bitwise OR.','Return zero when no even value exists.'],[([[1,2,3,4,5,6]],'The even values 2, 4, and 6 have bitwise OR six.'),([[1,3,5]],'No even values exist, so return zero.')],[[x] for x in [[0],[1],[2],[1,3,5],[1,2,3,4,5,6],[2,8],[4,6],[7,10,12],[0,1,2],[16,3,5],[14,2,1],[100,200],[9,8,7,6],[2,2,2]]],EVEN,[EVEN.replace('value%2==0','value%2==1'),EVEN.replace('answer|=value','answer+=value')],['Includes odd rather than even values.','Adds selected values instead of taking their bitwise OR.'],even_oracle,random_even,['Initialize the OR identity zero.','Inspect every value and retain only evens.','OR each retained value into the accumulator.','If none qualify, the untouched identity supplies the required zero.'],'O(n)','O(1)',3),
3696:entry('maximum_unequal_word_distance',[('words','list[str]')],'int',['arrays','strings','enumeration'],['Choose two indices holding different strings.','Their distance is the index difference plus one.','Return the maximum distance, or zero if every pair has equal strings.'],[([['leetcode','leetcode','codeforces']],'Indices zero and two differ, giving distance three.'),([['a','a']],'No pair contains unequal words, so return zero.')],[[x] for x in [['a'],['a','a'],['a','b'],['leetcode','leetcode','codeforces'],['a','b','a'],['x','x','y','x'],['a','b','c','d'],['same']*5,['p','q','q','p'],['one','two','one','three'],['z','a','z','a'],['aa','a'],['left','mid','right'],['x','y','x','x','z']]],DISTANCE,[DISTANCE.replace('j-i+1','j-i'),DISTANCE.replace('words[i]!=words[j]','words[i]==words[j]')],['Omits the plus one in the distance definition.','Measures pairs with equal strings.'],distance_oracle,random_distance,['Enumerate all index pairs in increasing order.','Ignore pairs whose strings match.','For each remaining pair compute j-i+1.','The maximum across all eligible pairs is the requested distance.'],'O(n^2)','O(1)',3),
3697:entry('decimal_place_components',[('n','int')],'list[int]',['math','digits'],['Represent positive n as nonzero decimal place-value components.','Each component is one digit from one to nine times a power of ten.','Return the fewest components in descending place order.'],[([537],'The nonzero place values are 500, 30, and 7.'),([1002],'Zero places are omitted, leaving 1000 and 2.')],[[n] for n in [1,9,10,11,100,101,537,1002,9090,12030,99999,40004,700,123456789]],DECIMAL,[DECIMAL.replace('if digit:','if True:'),DECIMAL.replace('components[::-1]','components')],['Includes zero-valued place components.','Returns components in ascending rather than descending order.'],decimal_oracle,random_decimal,['Read digits from least significant to most significant.','For each nonzero digit, multiply it by its current power of ten.','Omitting zero positions gives the fewest components.','Reverse the collected list to descending place order.'],'O(digits)','O(digits)',3),
3701:entry('alternating_index_sum',[('nums','list[int]')],'int',['arrays','sums'],['Add values at even zero-based indices.','Subtract values at odd indices.','Return the resulting alternating sum.'],[([[1,3,5,7]],'One minus three plus five minus seven equals negative four.'),([[10]],'The only value is at an even index, so return ten.')],[[x] for x in [[0],[10],[1,3,5,7],[1,2],[2,1],[-1,2,-3],[5,5,5],[1,-1,1,-1],[9,8,7],[3,0,3,0],[100,-100],[1,2,3,4,5],[7,6,5,4],[2,4,6,8]]],ALTERNATING,[ALTERNATING.replace('i%2==0','i%2==1'),ALTERNATING.replace('else -value','else value')],['Adds odd positions and subtracts even positions.','Adds every value instead of alternating signs.'],alternating_oracle,random_alternating,['Enumerate values with zero-based indices.','Use a positive sign on even indices and a negative sign on odd indices.','Add every signed contribution.','The parity rule directly matches the alternating-sum definition.'],'O(n)','O(1)',3),
3707:entry('has_equal_alphabet_score_split',[('s','str')],'bool',['strings','prefix sums'],['Score a through z as one through twenty-six.','Split s into two nonempty contiguous parts.','Return whether any split gives equal score sums.'],[(['adcb'],'Scores [1,4] and [3,2] both total five.'),(['abc'],'No nonempty split has equal scores.')],[[s] for s in ['aa','ab','abc','adcb','az','zz','abba','abcd','aazz','mnop','leetcode','baba','aceg','xyyx']],SCORE,[SCORE.replace('ord(char)-96','ord(char)-97'),SCORE.replace('left==total-left','left>=total-left')],['Uses zero-based alphabet scores instead of one-based scores.','Accepts unequal halves once the prefix reaches at least half.'],score_oracle,random_score,['Compute the total alphabet score.','Move characters one at a time into a prefix accumulator, stopping before the final character.','At each legal split compare prefix with total-prefix.','Equality at any point proves the required division.'],'O(n)','O(1)',3),
}
