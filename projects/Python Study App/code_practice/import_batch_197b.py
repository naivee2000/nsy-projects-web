"""Digit adjacency, zero movement, digit scores, set-bit runs, and compatible ranges."""
from .import_batch_055 import entry

def adjacent_oracle(a):return all(abs(int(a[0][i])-int(a[0][i+1]))<=2 for i in range(len(a[0])-1))
def random_adjacent(r):return [''.join(r.choice('0123456789') for _ in range(r.randint(2,60)))]
def swaps_oracle(a):
    nums=a[0];z=sum(x==0 for x in nums);return sum(x==0 for x in nums[:len(nums)-z])
def random_swaps(r):return [[r.choice([0,0,1,2,3]) for _ in range(r.randint(1,60))]]
def digit_score_oracle(a):return sum(map(int,str(a[0])))
def random_digit_score(r):return [r.randint(1,10**9)]
def pair_bits_oracle(a):return bin(a[0])[2:].count('11')==1
def random_pair_bits(r):return [r.randint(1,10**9)]
def compatible_oracle(a):
    n,k=a;return sum(x for x in range(max(1,n-k),n+k+1) if n&x==0)
def random_compatible(r):return [r.randint(1,100),r.randint(1,100)]

ADJACENT='''def adjacent_digit_differences_at_most_two(s):
    return all(abs(int(s[i])-int(s[i+1]))<=2 for i in range(len(s)-1))
'''
SWAPS='''def minimum_swaps_zeros_to_end(nums):
    zeros=sum(x==0 for x in nums)
    return sum(x==0 for x in nums[:len(nums)-zeros])
'''
DIGIT_SCORE='''def digit_frequency_score(n):
    return sum(int(digit) for digit in str(n))
'''
PAIR_BITS='''def has_exactly_one_consecutive_set_bit_pair(n):
    return bin(n)[2:].count('11')==1
'''
COMPATIBLE='''def sum_compatible_numbers(n,k):
    return sum(x for x in range(max(1,n-k),n+k+1) if n&x==0)
'''

BATCH={
3931:entry('adjacent_digit_differences_at_most_two',[('s','str')],'bool',['strings','adjacent pairs'],['s contains at least two decimal digits.','Every neighboring digit pair must differ by at most two.','Return whether all pairs meet the inclusive bound.'],[(['132'],'The differences are two and one, both within the limit.'),(['129'],'The final difference is seven, so the condition fails.')],[[s] for s in ['00','01','02','03','10','132','129','975','8642','2468','1111','909','3210','56765']],ADJACENT,[ADJACENT.replace('<=2','<2'),ADJACENT.replace('int(s[i+1])','int(s[i+2]) if i+2<len(s) else int(s[i+1])')],['Rejects adjacent digits whose difference is exactly two.','Compares some digits two positions apart.'],adjacent_oracle,random_adjacent,['Walk every neighboring pair.','Convert both digit characters to integers.','Reject a difference greater than two.','All pairs must pass, including the final pair.'],'O(n)','O(1)',3),
3936:entry('minimum_swaps_zeros_to_end',[('nums','list[int]')],'int',['arrays','two pointers'],['One operation swaps any two distinct positions.','Move every zero into a suffix of the array.','Return the minimum number of swaps; relative order need not be preserved.'],[([[0,1,0,3,12]],'Two zeros occupy the first three positions, so two swaps move them behind all nonzeros.'),([[1,2,0,0]],'Zeros already form the suffix, so no swap is needed.')],[[x] for x in [[0],[1],[0,1],[1,0],[0,1,0,3,12],[1,2,0,0],[0,0,1,1],[1,0,1,0],[0,0,0],[1,2,3],[0,2,3,0,4],[5,0,0,6],[0,1,2,3],[1,0,0,0,2]]],SWAPS,[SWAPS.replace('nums[:len(nums)-zeros]','nums[-zeros:]'),SWAPS.replace('x==0','x!=0',1)],['Counts zeros already in the target suffix.','Counts nonzeros rather than misplaced zeros.'],swaps_oracle,random_swaps,['The final suffix has length equal to the zero count.','Each zero before that suffix is misplaced.','One arbitrary swap pairs one misplaced zero with one misplaced nonzero.','Thus the misplaced-zero count is both necessary and sufficient.'],'O(n)','O(1)',3),
3945:entry('digit_frequency_score',[('n','int')],'int',['math','digits'],['For each distinct decimal digit d, add d times its frequency in n.','Repeated occurrences contribute repeatedly and zero contributes nothing.','Return the resulting score.'],[([122],'One contributes one and two contributes four, for total five.'),([101],'The two ones contribute two and zero contributes nothing.')],[[n] for n in [1,9,10,11,101,122,909,1000,987654321,55555,2024,70007,444,123456789]],DIGIT_SCORE,[DIGIT_SCORE.replace('sum','max'),DIGIT_SCORE.replace('str(n)','str(n)[:-1]')],['Returns only the largest digit.','Drops the final decimal digit from the score.'],digit_score_oracle,random_digit_score,['Expanding d*frequency(d) is the same as summing every digit occurrence.','Convert n to its decimal digits.','Add their integer values.','This counts repeats exactly as their frequency multipliers require.'],'O(digits)','O(digits)',3),
3950:entry('has_exactly_one_consecutive_set_bit_pair',[('n','int')],'bool',['bit manipulation','strings'],['Inspect adjacent positions in the binary representation of positive n.','Count each occurrence of the substring 11, including overlapping occurrences.','Return true only when the count is exactly one.'],[([6],'Six is binary 110, which contains exactly one adjacent 11 pair.'),([7],'Seven is binary 111, whose two overlapping 11 pairs make it invalid.')],[[n] for n in [1,2,3,4,5,6,7,8,11,12,13,14,15,27,42,63]],PAIR_BITS,[PAIR_BITS.replace("==1",">=1"),PAIR_BITS.replace("count('11')","count('111')")],['Accepts numbers with two or more adjacent set-bit pairs.','Searches for triples rather than counting adjacent pairs.'],pair_bits_oracle,random_pair_bits,['Write n in binary without the 0b prefix.','Each adjacent set-bit pair appears as substring 11.','Use a substring count that includes the relevant starts.','Require the final count to equal one, not merely be positive.'],'O(log n)','O(log n)',3),
3954:entry('sum_compatible_numbers',[('n','int'),('k','int')],'int',['bit manipulation','enumeration'],['A compatible x is positive and satisfies abs(n-x)<=k.','It must also satisfy the bitwise condition n & x == 0.','Return the sum of every compatible integer.'],[([2,3],'The compatible values are one, four, and five, whose sum is ten.'),([5,1],'Neither four nor six has bitwise AND zero with five, so return zero.')],[[n,k] for n,k in [(1,1),(2,3),(5,1),(3,5),(8,2),(7,10),(10,10),(1,100),(100,1),(16,16),(6,3),(12,5),(31,4),(4,8),(9,7)]],COMPATIBLE,[COMPATIBLE.replace('n&x==0','n&x!=0'),COMPATIBLE.replace('max(1,n-k)','n-k')],['Sums incompatible values whose bits overlap n.','Includes nonpositive integers when the interval crosses zero.'],compatible_oracle,random_compatible,['Enumerate the closed distance interval around n.','Clamp its lower endpoint to one.','Test n & x for every candidate.','Add exactly the candidates whose shared set-bit mask is zero.'],'O(k)','O(1)',3),
}
