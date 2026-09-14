"""Equal triples, three-value expressions, binary symmetry, digit products, and bit reflection."""
from collections import defaultdict
from .import_batch_055 import entry

def triple_oracle(a):
    positions=defaultdict(list)
    for i,v in enumerate(a[0]):positions[v].append(i)
    return min((2*(p[i+2]-p[i]) for p in positions.values() for i in range(len(p)-2)),default=-1)
def random_triple(r):return [[r.randint(1,10) for _ in range(r.randint(3,40))]]
def expression_oracle(a):
    nums=a[0];return max(nums[i]+nums[j]-nums[k] for i in range(len(nums)) for j in range(len(nums)) for k in range(len(nums)) if len({i,j,k})==3)
def random_expression(r):return [[r.randint(-30,50) for _ in range(r.randint(3,12))]]
def flips_oracle(a):
    s=bin(a[0])[2:];return sum(x!=y for x,y in zip(s,s[::-1]))//2
def random_flips(r):return [r.randint(1,10**9)]
def concatenate_oracle(a):
    digits=[int(c) for c in str(a[0]) if c!='0'];x=int(''.join(map(str,digits))) if digits else 0;return x*sum(digits)
def random_concatenate(r):return [r.randint(0,10**12)]
def reflected(v):return int(bin(v)[2:][::-1],2)
def reflection_oracle(a):return sorted(a[0],key=lambda v:(reflected(v),v))
def random_reflection(r):return [[r.randint(1,1000) for _ in range(r.randint(1,40))]]
def mirror_oracle(a):return abs(a[0]-int(str(a[0])[::-1]))
def random_mirror(r):return [r.randint(0,10**12)]

TRIPLE='''def minimum_equal_triplet_distance(nums):
    positions={}
    answer=None
    for index,value in enumerate(nums):positions.setdefault(value,[]).append(index)
    for group in positions.values():
        for i in range(len(group)-2):
            distance=2*(group[i+2]-group[i])
            answer=distance if answer is None else min(answer,distance)
    return -1 if answer is None else answer
'''
EXPRESSION='''def maximum_three_element_expression(nums):
    values=sorted(nums)
    return values[-1]+values[-2]-values[0]
'''
FLIPS='''def minimum_binary_reverse_flips(n):
    bits=bin(n)[2:]
    return sum(bits[i]!=bits[-1-i] for i in range(len(bits)//2))
'''
CONCATENATE='''def concatenate_nonzero_digits_times_sum(n):
    digits=[int(char) for char in str(n) if char!='0']
    if not digits:return 0
    value=int(''.join(str(digit) for digit in digits))
    return value*sum(digits)
'''
REFLECTION='''def sort_by_binary_reflection(nums):
    def reflected(value):return int(bin(value)[2:][::-1],2)
    return sorted(nums,key=lambda value:(reflected(value),value))
'''
MIRROR='''def decimal_mirror_distance(n):
    return abs(n-int(str(n)[::-1]))
'''

BATCH={
3740:entry('minimum_equal_triplet_distance',[('nums','list[int]')],'int',['arrays','hash maps','indices'],['Choose three increasing indices containing the same value.','Their distance is the sum of all three pairwise index distances.','Return the minimum distance, or -1 if no equal-value triplet exists.'],[([[1,2,1,1,3]],'Indices zero, two, and three hold one; their pairwise distances total six.'),([[1,2,3]],'No value occurs three times, so return -1.')],[[x] for x in [[1,2,3],[1,1,1],[1,2,1,1,3],[2,2,1,2],[1,1,2,1,1],[3,3],[4,4,4,4],[1,2,3,1,2,1],[5,0,5,0,5],[7,7,8,7],[1,2,2,2,1],[9,8,9,9,8,8],[3,1,3,2,3],[6,6,1,1,6],[1,2,3,4,5,1,1,1]]],TRIPLE,[TRIPLE.replace('2*(group[i+2]-group[i])','group[i+2]-group[i]'),TRIPLE.replace('range(len(group)-2)','range(1)')],['Counts only the outer index gap rather than all pairwise distances.','Checks only the earliest triplet for each value.'],triple_oracle,random_triple,['Group occurrence indices by value.','For ordered i<j<k, pairwise distance simplifies to 2*(k-i).','For one value, only consecutive triples can minimize the outer span.','Evaluate those triples across groups and return the smallest result.'],'O(n)','O(n)',3),
3745:entry('maximum_three_element_expression',[('nums','list[int]')],'int',['arrays','greedy','sorting'],['Choose three distinct array indices assigned to a, b, and c.','Maximize a+b-c.','Return the greatest achievable value.'],[([[1,4,2,5]],'Choose five and four as positive terms and one as c, giving eight.'),([[-5,-2,-3]],'Use negative two and negative three, then subtract negative five, giving zero.')],[[x] for x in [[1,2,3],[1,4,2,5],[-5,-2,-3],[0,0,0],[5,5,1],[10,1,2],[-1,0,1],[9,8,7,6],[2,2,2,1],[100,-100,0],[3,1,4,1,5],[-10,-9,20],[6,5,4],[1,10,10]]],EXPRESSION,[EXPRESSION.replace('values[-2]','values[0]'),EXPRESSION.replace('-values[0]','-values[-1]')],['Reuses the minimum as both a positive term and c choice pattern.','Subtracts the maximum instead of the minimum.'],expression_oracle,random_expression,['The two positive terms should use the two largest occurrences.','The subtracted term should use the smallest remaining occurrence.','Sorting exposes these three positions while respecting duplicate multiplicity.','Any exchange toward larger positive or smaller negative terms cannot reduce the expression.'],'O(n log n)','O(n)',3),
3750:entry('minimum_binary_reverse_flips',[('n','int')],'int',['bit manipulation','strings'],['Write positive n in binary without leading zeros.','Flip individual bits until the string equals its reversal.','Return the minimum number of flips.'],[([7],'Binary 111 is already symmetric, so zero flips are required.'),([10],'Binary 1010 has two mismatched mirrored pairs, requiring two flips.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,15,16,21,42]],FLIPS,[FLIPS.replace('range(len(bits)//2)','range(len(bits))'),FLIPS.replace('!=','==')],['Counts each mismatched mirrored pair twice.','Counts matching pairs rather than mismatches.'],flips_oracle,random_flips,['Compare mirrored positions only through half the bit string.','A matching pair needs no work.','A mismatched pair needs exactly one flip on either side.','Different mirrored pairs are independent, so their mismatch count is minimal.'],'O(bits)','O(bits)',3),
3754:entry('concatenate_nonzero_digits_times_sum',[('n','int')],'int',['math','digits','strings'],['Keep the nonzero decimal digits of n in their original order and concatenate them into x.','Compute the sum of those retained digits.','Return x multiplied by the digit sum; use zero if no nonzero digit exists.'],[([10203004],'The retained digits form 1234 with sum ten, producing 12340.'),([100],'The retained value and digit sum are both one, producing one.')],[[n] for n in [0,1,10,100,10203004,909,1002,5005,123,100000,70809,1110,987654,400040]],CONCATENATE,[CONCATENATE.replace("if char!='0'",'if True'),CONCATENATE.replace('value*sum(digits)','value+sum(digits)')],['Keeps zero digits in the concatenated integer.','Adds x and its digit sum instead of multiplying.'],concatenate_oracle,random_concatenate,['Filter decimal digits while preserving order.','Join retained digits to form x.','Their list also provides the required sum.','Multiply the two computed quantities, with an explicit empty result of zero.'],'O(digits)','O(digits)',3),
3769:entry('sort_by_binary_reflection',[('nums','list[int]')],'list[int]',['arrays','bit manipulation','sorting'],['Reflect a positive integer by reversing the digits of its binary representation, then interpreting that result as binary.','Sort values by increasing reflected value.','Break reflected-value ties by the smaller original integer.'],[([[4,5,4]],'Four reflects to one while five reflects to five, so both fours precede five.'),([[3,6,5]],'Their reflected keys are three, three, and five; the tie places three before six.')],[[x] for x in [[1],[1,2],[4,5,4],[3,6,5],[2,4,8],[7,3,1],[10,5,2],[9,12,6],[15,16],[1,3,7],[20,10,5],[6,3,12],[100,50,25],[8,4,2,1]]],REFLECTION,[REFLECTION.replace('[2:][::-1]','[2:]'),REFLECTION.replace('(reflected(value),value)','(reflected(value),-value)')],['Uses the ordinary value instead of reversing its binary digits.','Breaks reflected-key ties toward the larger original value.'],reflection_oracle,random_reflection,['Convert each value to binary without its prefix.','Reverse those bits and parse them in base two.','Use reflected value as the primary sort key and original value as the secondary key.','Tuple sorting implements both ascending rules deterministically.'],'O(n log n * bits)','O(n)',3),
3783:entry('decimal_mirror_distance',[('n','int')],'int',['math','digits','strings'],['Reverse the decimal digits of n, dropping any leading zeros created in the reversed form.','Return the absolute difference between n and that reversed integer.','A decimal palindrome therefore has distance zero.'],[([25],'The reverse is 52, whose absolute difference from 25 is 27.'),([120],'The reverse is 21, so the distance is 99.')],[[n] for n in [0,1,10,11,25,120,101,909,1000,1234,9876,1001,5005,1000002]],MIRROR,[MIRROR.replace('abs(','('),MIRROR.replace("[::-1]","[1:]")],['Returns a signed difference rather than its absolute value.','Drops the first digit instead of reversing digits.'],mirror_oracle,random_mirror,['Convert n to decimal text and reverse it.','Integer parsing removes any new leading zeros.','Subtract the two integers.','Absolute value makes the distance independent of which integer is larger.'],'O(digits)','O(digits)',3),
}
