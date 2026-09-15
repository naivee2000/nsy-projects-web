"""Binary run minimization, cyclic matches, split pieces, and product subsequences."""
from collections import defaultdict
from itertools import combinations
from math import gcd

from .import_batch_055 import entry


def longest_run(text):
    best = current = 0; previous = None
    for char in text:
        current = current + 1 if char == previous else 1
        best = max(best, current); previous = char
    return best


def binary_oracle(args):
    text, operations = args; answer = len(text)
    for mask in range(1 << len(text)):
        if mask.bit_count() <= operations:
            changed = ''.join(str(int(char) ^ (mask >> index & 1)) for index, char in enumerate(text))
            answer = min(answer, longest_run(changed))
    return answer


def random_binary(rng):
    text = ''.join(rng.choice('01') for _ in range(rng.randint(1, 10)))
    return [text, rng.randint(0, len(text))]


def matching_oracle(args):
    first, second = args; size = len(first)
    rotations = [first[-shift:] + first[:-shift] if shift else first[:] for shift in range(size)]
    return max(sum(left == right for left, right in zip(rotation, second)) for rotation in rotations)


def random_matching(rng):
    size = rng.randint(1, 10)
    return [[rng.randint(1, 5) for _ in range(size)], [rng.randint(1, 5) for _ in range(size)]]


def box_oracle(args):
    word, friends = args
    if friends == 1: return word
    pieces = []
    for cuts in combinations(range(1, len(word)), friends - 1):
        points = (0,) + cuts + (len(word),)
        pieces.extend(word[points[index]:points[index + 1]] for index in range(friends))
    return max(pieces)


def random_box(rng):
    size = rng.randint(1, 9)
    return [''.join(rng.choice('abcd') for _ in range(size)), rng.randint(1, size)]


def special_oracle(args):
    nums = args[0]; answer = 0
    for p, q, r, s in combinations(range(len(nums)), 4):
        if q - p > 1 and r - q > 1 and s - r > 1 and nums[p] * nums[r] == nums[q] * nums[s]:
            answer += 1
    return answer


def random_special(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(7, 13))]]


BINARY = '''def minimum_longest_binary_run(s,num_ops):
    n=len(s)
    def possible(limit):
        if limit==1:
            first=sum(char!=('0' if index%2==0 else '1') for index,char in enumerate(s))
            return min(first,n-first)<=num_ops
        needed=run=0
        for index,char in enumerate(s):
            run+=1
            if index==n-1 or char!=s[index+1]:needed+=run//(limit+1);run=0
        return needed<=num_ops
    low=1;high=n
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
'''

MATCHING = '''def maximum_cyclic_matching_indices(nums1,nums2):
    size=len(nums1);answer=0
    for shift in range(size):
        answer=max(answer,sum(nums1[(index-shift)%size]==value for index,value in enumerate(nums2)))
    return answer
'''

BOX = '''def largest_string_from_box(word,num_friends):
    if num_friends==1:return word
    maximum_length=len(word)-num_friends+1
    return max(word[start:start+maximum_length] for start in range(len(word)))
'''

SPECIAL = '''def count_special_product_subsequences(nums):
    from collections import defaultdict
    from math import gcd
    count=defaultdict(int);n=len(nums)
    for third in range(4,n-2):
        c=nums[third]
        for fourth in range(third+2,n):
            d=nums[fourth];factor=gcd(c,d);count[(d//factor,c//factor)]+=1
    answer=0
    for second in range(2,n-4):
        b=nums[second]
        for first in range(second-1):
            a=nums[first];factor=gcd(a,b);answer+=count[(a//factor,b//factor)]
        third=second+2;c=nums[third]
        for fourth in range(second+4,n):
            d=nums[fourth];factor=gcd(c,d);count[(d//factor,c//factor)]-=1
    return answer
'''


def lesson(a,b,c,d): return [a,b,c,d]


BINARY_CASES=[[text,ops] for text,ops in [
    ('000001',1),('0',0),('1',1),('01',0),('00',0),('00',1),('000',1),
    ('1111',1),('010101',0),('001100',1),('000111',2),('1011101',1),
    ('00000000',2),('1100110011',2)]]
MATCH_CASES=[[a,b] for a,b in [
    ([3,1,2,3,1,2],[1,2,3,1,2,3]),([1],[1]),([1],[2]),([1,2],[1,2]),
    ([1,2],[2,1]),([1,1,2],[1,2,1]),([1,2,3],[3,2,1]),([1,2,3,4],[3,4,1,2]),
    ([1,1,1],[1,2,1]),([5,4,3,2,1],[1,5,4,3,2]),([2,3,2,3],[3,2,3,2]),
    ([1,2,1,3],[1,3,1,2]),([9,8,7],[8,7,9]),([1,2,3,1],[1,1,2,3])]]
BOX_CASES=[[word,friends] for word,friends in [
    ('dbca',2),('a',1),('abc',1),('abc',2),('abc',3),('aaaa',2),('zabc',2),
    ('azby',3),('leetcode',4),('banana',2),('cabaa',4),('xyzxyz',3),('baca',2),('zzza',3)]]
SPECIAL_CASES=[[[v for v in values]] for values in [
    [1,2,3,4,3,6,1],[1,1,1,1,1,1,1],[1,2,3,4,5,6,7],
    [2,9,3,8,4,7,6],[1,2,1,2,1,2,1,2],[2,3,4,6,8,12,16],
    [3,1,2,3,2,1,3,2,3],[5,4,3,2,1,2,3,4,5],
    [1,3,2,6,4,12,8,24],[2,5,3,7,6,10,4,8],
    [4,1,2,2,1,4,2,8,4],[7,7,7,7,7,7,7,7],
    [1,4,2,8,4,16,8,32,16],[6,2,3,9,6,18,12,4,2,1]]]


BATCH={
3398:entry('minimum_longest_binary_run',[('s','str'),('num_ops','int')],'int',['strings','binary search','greedy'],['s has 1–1,000 binary characters and 0 <= num_ops <= len(s).','Flip at most num_ops individual bits.','Minimize the maximum length of any consecutive equal-character run.'],[(['000001',1],'Flipping an interior zero can split the five-zero run so the longest remaining run has length two.'),(['010101',0],'The string already alternates, so its longest equal run has length one.')],BINARY_CASES,BINARY,[BINARY.replace("return min(first,n-first)<=num_ops","return first<=num_ops"),BINARY.replace('needed+=run//(limit+1)','needed+=(run+limit)//(limit+1)')],['Checks only the alternating pattern beginning with zero.','Rounds the flips per run upward and rejects feasible limits.'],binary_oracle,random_binary,lesson('For a proposed run limit, each original run has an independent minimum number of splitting flips except at limit one.','Binary-search the limit; count floor(run/(limit+1)) flips, with a separate alternating-pattern check for one.','Test both alternating starts for limit one; otherwise scan run lengths and compare their required flips with the budget.','For limits at least two, optimally spaced flips split each run without merging neighboring runs; feasibility is monotone.'),'O(n log n)','O(1)',8),
3399:entry('minimum_longest_binary_run_large',[('s','str'),('num_ops','int')],'int',['strings','binary search','greedy'],['s has 1–100,000 binary characters and 0 <= num_ops <= len(s).','Flip at most num_ops individual bits.','Return the smallest possible longest equal-character run length.'],[(['000001',1],'One well-placed flip reduces the longest run from five to two.'),(['1111',1],'Flipping either middle bit leaves no run longer than two.')],BINARY_CASES,BINARY.replace('minimum_longest_binary_run','minimum_longest_binary_run_large'),[BINARY.replace('minimum_longest_binary_run','minimum_longest_binary_run_large').replace("return min(first,n-first)<=num_ops","return first<=num_ops"),BINARY.replace('minimum_longest_binary_run','minimum_longest_binary_run_large').replace('needed+=run//(limit+1)','needed+=(run+limit)//(limit+1)')],['Checks only one of the two alternating targets.','Uses ceiling rather than the exact number of separators required per run.'],binary_oracle,random_binary,lesson('The larger constraint still reduces to a monotone feasibility test on the desired run length.','Binary-search the answer and count necessary flips in one scan per candidate.','Handle limit one with alternating mismatch counts; for larger limits sum floor(run/(limit+1)).','Every smaller feasible limit implies every larger limit is feasible, enabling logarithmic search.'),'O(n log n)','O(1)',8),
3400:entry('maximum_cyclic_matching_indices',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','enumeration','simulation'],['nums1 and nums2 have equal length up to 3,000 and contain positive integers.','Right-shift nums1 any number of positions with wraparound.','Return the maximum count of equal values at matching indices.'],[([[3,1,2,3,1,2],[1,2,3,1,2,3]],'A two-position right shift aligns all six entries.'),([[1,2,3],[3,2,1]],'No rotation matches more than one index.')],MATCH_CASES,MATCHING,[MATCHING.replace('(index-shift)%size','index-shift').replace('sum(nums1[index-shift]==value','sum(index>=shift and nums1[index-shift]==value'),MATCHING.replace('for shift in range(size)','for shift in range(1)')],['Drops wrapped entries instead of rotating them to the front.','Checks only the original alignment.'],matching_oracle,random_matching,lesson('There are exactly n distinct cyclic alignments.','Evaluate every shift and compare all paired indices with modular indexing.','For shift 0 through n-1, count nums1[(i-shift) mod n] equal to nums2[i].','Every number of right shifts is congruent to one enumerated shift modulo n.'),'O(n²)','O(1)',5),
3403:entry('largest_string_from_box',[('word','str'),('num_friends','int')],'str',['strings','greedy','enumeration'],['word has 1–5,000 lowercase letters and 1 <= num_friends <= len(word).','Across all splits into num_friends nonempty consecutive parts, every produced part is placed in the box.','Return the lexicographically largest part that can appear.'],[(['dbca',2],'The prefix dbc can appear while leaving a for the second friend, and it is lexicographically largest.'),(['abc',1],'With one friend the only part is the full word.')],BOX_CASES,BOX,[BOX.replace('maximum_length=len(word)-num_friends+1','maximum_length=len(word)'),BOX.replace('+1','')],['Ignores the characters that must remain for other nonempty parts.','Uses a maximum length one character too short.'],box_oracle,random_box,lesson('A part beginning at any index can use at most n-numFriends+1 characters.','For every start, take its longest feasible slice; a shorter prefix cannot beat its own longer version.','Special-case one friend, then return the maximum slice word[i:i+limit].','Every feasible part is a prefix of one candidate slice, and lexicographic order favors the candidate when that prefix ties.'),'O(n²)','O(n)',5),
3404:entry('count_special_product_subsequences',[('nums','list[int]')],'int',['arrays','hash maps','number theory'],['nums has 7–1,000 positive values up to 1,000.','Choose p<q<r<s with at least one unused index between each consecutive pair.','Count choices satisfying nums[p]*nums[r] == nums[q]*nums[s].'],[([[1,2,3,4,3,6,1]],'Indices 0,2,4,6 satisfy the gaps and products 1×3 = 3×1.'),([[1,1,1,1,1,1,1]],'Only indices 0,2,4,6 meet all three spacing requirements, producing one valid subsequence.')],SPECIAL_CASES,SPECIAL,[SPECIAL.replace('(d//factor,c//factor)','(c//factor,d//factor)',1),SPECIAL.replace('range(third+2,n)','range(third+1,n)')],['Stores the right-hand ratio in reversed order.','Allows the last two selected indices to be adjacent.'],special_oracle,random_special,lesson('The product equality is equivalent to the reduced ratio nums[p]/nums[q] equaling nums[s]/nums[r].','Sweep the second index while a frequency map holds eligible future third/fourth ratios.','Query all spaced first indices, then remove pairs whose third index will become too close for the next sweep step.','The map contains exactly the suffix pairs satisfying both future gaps, so each valid quadruple is counted at its unique second index.'),'O(n²)','O(n²)',6),
}
