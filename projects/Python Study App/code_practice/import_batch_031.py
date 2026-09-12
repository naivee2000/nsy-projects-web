"""Strict in-place wiggles, variable windows, integer products and character swaps."""
from collections import Counter

from .import_batch_003 import entry


def strict_arrangement(values):
    counts = Counter(values)
    path = []
    def search():
        if len(path) == len(values):
            return list(path)
        for value in sorted(counts):
            if not counts[value]:
                continue
            if path and not (path[-1] < value if len(path)%2 else path[-1] > value):
                continue
            counts[value] -= 1
            path.append(value)
            answer = search()
            path.pop()
            counts[value] += 1
            if answer is not None:
                return answer
        return None
    return search()


def wiggle_oracle(args):
    result = strict_arrangement(args[0])
    if result is None:
        raise ValueError('Wiggle Sort II inputs must admit a strict arrangement')
    return result


def distinct_window_oracle(args):
    text, k = args
    return max((end-start for start in range(len(text)) for end in range(start+1,len(text)+1)
                if len(set(text[start:end])) <= k), default=0)


def power_four_oracle(args):
    return args[0] in {4**exponent for exponent in range(16)}


def integer_break_oracle(args):
    n = args[0]
    best = [0]*(n+1)
    for total in range(2,n+1):
        best[total] = max(max(first*(total-first), first*best[total-first]) for first in range(1,total))
    return best[n]


def reverse_characters_oracle(args):
    return list(reversed(args[0]))


def reverse_vowels_oracle(args):
    text = args[0]
    vowels = [letter for letter in text if letter in 'aeiouAEIOU']
    return ''.join(vowels.pop() if letter in 'aeiouAEIOU' else letter for letter in text)


def random_wiggle(rng):
    while True:
        values = [rng.randint(0,4) for _ in range(rng.randint(1,8))]
        if strict_arrangement(values) is not None:
            return [values]


def random_window(rng):
    return [''.join(rng.choice('abCD 19é') for _ in range(rng.randint(1,18))), rng.randint(0,9)]


def random_power_four(rng):
    return [rng.choice([4**rng.randrange(16), 2**rng.randrange(31), rng.randint(-(2**31),2**31-1)])]


def random_integer_break(rng):
    return [rng.randint(2,58)]


def random_characters(rng):
    return [[chr(rng.randint(32,126)) for _ in range(rng.randint(1,30))]]


def random_vowels(rng):
    return [''.join(rng.choice('aeiouAEIOUbcYZ 19!?') for _ in range(rng.randint(1,30)))]


STRICT_WIGGLE = '''\
def wiggle_sort_strict(nums):
    ordered = sorted(nums)
    middle = (len(nums)+1)//2
    nums[::2] = ordered[:middle][::-1]
    nums[1::2] = ordered[middle:][::-1]
'''

DISTINCT_WINDOW = '''\
def longest_k_distinct_substring(s, k):
    counts = {}
    left = best = 0
    for right, letter in enumerate(s):
        counts[letter] = counts.get(letter,0)+1
        while len(counts) > k:
            old = s[left]
            counts[old] -= 1
            if counts[old] == 0:
                del counts[old]
            left += 1
        best = max(best,right-left+1)
    return best
'''

POWER_FOUR = '''\
def is_power_of_four(n):
    return n > 0 and n & (n-1) == 0 and n & 0x55555555 != 0
'''

INTEGER_BREAK = '''\
def max_integer_break_product(n):
    if n <= 3:
        return n-1
    threes, remainder = divmod(n,3)
    if remainder == 0:
        return 3**threes
    if remainder == 1:
        return 3**(threes-1)*4
    return 3**threes*2
'''

REVERSE_CHARACTERS = '''\
def reverse_characters(s):
    left, right = 0,len(s)-1
    while left < right:
        s[left],s[right] = s[right],s[left]
        left += 1
        right -= 1
'''

REVERSE_VOWELS = '''\
def reverse_vowels(s):
    letters = list(s)
    vowels = set('aeiouAEIOU')
    left, right = 0,len(letters)-1
    while left < right:
        while left < right and letters[left] not in vowels:
            left += 1
        while left < right and letters[right] not in vowels:
            right -= 1
        letters[left],letters[right] = letters[right],letters[left]
        left += 1
        right -= 1
    return ''.join(letters)
'''

WEAK_WIGGLE = '''\
def wiggle_sort_strict(nums):
    for i in range(1,len(nums)):
        if (i%2 and nums[i-1] > nums[i]) or (i%2==0 and nums[i-1] < nums[i]):
            nums[i-1],nums[i] = nums[i],nums[i-1]
'''
FORWARD_HALVES = STRICT_WIGGLE.replace('ordered[:middle][::-1]', 'ordered[:middle]').replace('ordered[middle:][::-1]', 'ordered[middle:]')
EXACT_DISTINCT = DISTINCT_WINDOW.replace('        best = max(best,right-left+1)', '        if len(counts) == k:\n            best = max(best,right-left+1)')
PREFIX_WINDOW = '''\
def longest_k_distinct_substring(s, k):
    seen = set()
    for i,letter in enumerate(s):
        seen.add(letter)
        if len(seen) > k:
            return i
    return len(s)
'''
POWER_TWO_ONLY = '''\
def is_power_of_four(n):
    return n > 0 and n & (n-1) == 0
'''
DIVISIBLE_FOUR = '''\
def is_power_of_four(n):
    return n == 1 or (n > 0 and n%4 == 0)
'''
TWO_PARTS_ONLY = '''\
def max_integer_break_product(n):
    return (n//2)*(n-n//2)
'''
ONES_REMAINDER = INTEGER_BREAK.replace('return 3**(threes-1)*4', 'return 3**threes')
RETURN_COPY = '''\
def reverse_characters(s):
    return s[::-1]
'''
UNDO_REVERSE = '''\
def reverse_characters(s):
    for i in range(len(s)):
        s[i],s[-1-i] = s[-1-i],s[i]
'''
LOWERCASE_ONLY = REVERSE_VOWELS.replace('aeiouAEIOU','aeiou')
REVERSE_EVERYTHING = '''\
def reverse_vowels(s):
    return s[::-1]
'''

BATCH = {
    324: entry('wiggle_sort_strict',[('nums','list[int]')],'None',['arrays','sorting','in-place'],
        ['1 <= len(nums) <= 50000; 0 <= nums[i] <= 5000. A strict wiggle arrangement is guaranteed to exist.',
         'Modify the original list so nums[0] < nums[1] > nums[2] < nums[3] and so on. Keep every input occurrence exactly once; adjacent equality is NOT allowed. Return nothing. Any valid arrangement is accepted.',
         'The baseline target allows sorting with O(n) workspace. Linear-time and constant-extra-space partitioning are optional follow-ups.'],
        [([[1,5,1,1,6,4]],'One valid arrangement is [1,4,1,5,1,6]: each 1 is below its neighboring peaks. [1,6,1,5,1,4] is equally valid.'),
         ([[1,3,2,2,3,1]],'One valid arrangement is [2,3,1,3,1,2]. Simply interleaving sorted halves forward can place two 2s next to each other, which fails the strict rule.')],
        [[values] for values in ([0],[1],[1,2],[2,1],[1,1,2],[1,2,3],[3,2,1],
            [1,1,2,2],[1,1,1,2,2],[0,0,1,1,2],[1,2,2,3],[4,5,5,6],
            [0,5000,0,5000],[2,2,2,3,3,4],[0,1,2,3,4,5])],
        STRICT_WIGGLE,[WEAK_WIGGLE,FORWARD_HALVES],
        ['Repairs only non-strict inequalities and may leave equal neighbors.', 'Interleaves halves in ascending order, allowing repeated middle values to meet at a peak/valley boundary.'],
        wiggle_oracle,random_wiggle,
        ['Repeated values must be separated; the simple one-pass non-strict Wiggle Sort algorithm is insufficient.',
         'After sorting, place the smaller half at even valley positions and the larger half at odd peak positions, traversing BOTH halves backward.',
         'Let middle=(n+1)//2. Assign sorted[:middle] reversed to nums[::2], and sorted[middle:] reversed to nums[1::2].',
         'Backward placement separates repeated median values. Under the guaranteed-feasible input contract every adjacent peak is strictly larger than its valleys.'],
        'Split sorted values into a lower half (including the median for odd lengths) and an upper half. Fill even and odd positions from the ends of these halves. Upper values dominate lower values; reversing prevents equal median occurrences from becoming adjacent in feasible instances. The property judge checks both the complete multiset and strict alternation, so multiple arrangements pass. The independent oracle uses multiset backtracking to find a legal permutation on small inputs. This contract differs from Wiggle Sort, where equality is allowed.',
        'O(n log n)','O(n)',difficulty=6,
        stress=[([[0]*25000+[5000]*25000],[0,5000]*25000),([[1]*24999+[0]*25000],[0,1]*24999+[0])]),
    340: entry('longest_k_distinct_substring',[('s','str'),('k','int')],'int',['strings','sliding-window','hash-maps'],
        ['1 <= len(s) <= 50000; 0 <= k <= 50.',
         'Return the length of the longest contiguous substring containing AT MOST k distinct characters. Repeated occurrences count toward length; k=0 permits no nonempty substring.'],
        [(['eceba',2],'The substring ece has length 3 and uses only e and c. Extending it includes b, a third distinct character.'),
         (['abbbbb',1],'The best substring is bbbbb, of length 5. It starts after the beginning of the input.')],
        [[text,k] for text,k in (('a',0),('a',1),('aa',1),('abc',5),('abc',2),('aabbcc',2),
            ('abcabc',1),('abcabc',3),('abaccc',2),('a a a',1),('AaAa',1),('a1a1bb',2),
            ('ééaé',1),('abc',0),('aaabbbcccaaaa',2))],
        DISTINCT_WINDOW,[EXACT_DISTINCT,PREFIX_WINDOW],
        ['Requires exactly k distinct characters and rejects valid shorter alphabets.', 'Examines only a window starting at index zero and misses a better suffix window.'],
        distinct_window_oracle,random_window,
        ['Expand a contiguous window and count how many distinct characters it contains.',
         'When the count exceeds k, advance the left edge until the window is valid again.',
         'Add the right character; while distinct>k decrement counts at left and delete zero counts. Update best with right-left+1.',
         'Each index enters and leaves once. At most k+1 active character counts exist during an update, including k=0.'],
        'Maintain a valid sliding window with character frequencies. Shrinking only while there are too many distinct characters yields the longest valid window ending at each right position. Delete zero counts so dictionary size really counts distinct characters. The maximum across right endpoints is globally optimal. The oracle enumerates all substrings and measures explicit character sets.',
        'O(n)','O(min(n,k+1))',difficulty=6,
        stress=[(['a'*25000+'b'*25000,1],25000),(['ab'*25000,2],50000),(['x'*50000,0],0)]),
    342: entry('is_power_of_four',[('n','int')],'bool',['math','bit-manipulation'],
        ['-(2^31) <= n <= 2^31-1. Return whether n = 4^x for a nonnegative integer x.',
         '1 is a valid power. A power of two is a power of four only when its set bit has an even zero-based position.'],
        [([16],'16=4^2, so return true.'),([8],'8=2^3 is a power of two, but not a power of four. Return false.')],
        [[n] for n in (0,1,-1,2,3,4,5,12,32,64,256,1024,1073741824,2147483647,-2147483648)],
        POWER_FOUR,[POWER_TWO_ONLY,DIVISIBLE_FOUR],
        ['Checks for one set bit but accepts odd-exponent powers of two.', 'Accepts every positive multiple of four, even when other prime factors remain.'],
        power_four_oracle,random_power_four,
        ['Powers of four are powers of two with the single set bit in positions 0,2,4,... .',
         'First require n>0 and n&(n-1)==0; then check membership in the alternating-bit mask.',
         'Return n>0 and n&(n-1)==0 and n&0x55555555!=0 for the fixed 32-bit domain.',
         'The mask has ones at exactly the even bit positions. Repeated division by four is another valid approach.'],
        'Clearing the lowest set bit leaves zero exactly for positive powers of two. Intersecting with 0x55555555 then restricts the bit to an even position, corresponding to 2^(2x)=4^x. Positivity excludes zero and signed negatives. The independent oracle checks the full finite set of allowed powers directly.',
        'O(1) for 32-bit integers','O(1)',difficulty=3),
    343: entry('max_integer_break_product',[('n','int')],'int',['math','dynamic-programming','greedy'],
        ['2 <= n <= 58.', 'Split n into AT LEAST TWO positive integers summing to n. Return the maximum product; the parts need not be distinct or equal.'],
        [([2],'The only legal split is 1+1, whose product is 1. Keeping 2 unsplit is forbidden.'),
         ([10],'Split as 3+3+4 for product 36; a balanced two-part split 5+5 gives only 25.')],
        [[n] for n in (3,4,5,6,7,8,9,11,12,13,14,15,16,17,57,58)],
        INTEGER_BREAK,[TWO_PARTS_ONLY,ONES_REMAINDER],
        ['Uses exactly two balanced parts and misses products using three or more parts.', 'Leaves a remainder-one factor after taking threes instead of replacing 3+1 by 2+2.'],
        integer_break_oracle,random_integer_break,
        ['You may use more than two parts; first consider dynamic programming over all split points.',
         'For n>=4, factors of 3 are usually best, but a final 1 should be combined with a 3 to make 2+2.',
         'Handle n<=3 as n-1. Divide n by 3: remainder 0 gives 3^q, remainder 1 gives 4*3^(q-1), remainder 2 gives 2*3^q.',
         'Any part at least 5 improves when split into 3 and the rest; 3+1 yields product 3, worse than 2+2 giving 4.'],
        'For small n the requirement to split is decisive: 2 maps to 1 and 3 to 2. For larger n, parts of size at least 5 improve when split, ones are wasteful, and three 2s have product 8 while two 3s have product 9. Thus use threes except for a final remainder 1, which becomes two twos. The oracle independently maximizes products over every first split using dynamic programming, and tests cover every allowed n.',
        'O(1) for the bounded input domain','O(1)',difficulty=6),
    344: entry('reverse_characters',[('s','list[str]')],'None',['strings','two-pointers','in-place'],
        ['s contains 1–100000 one-character printable ASCII strings (codes 32–126).',
         'Reverse the original character list in place using O(1) extra memory. Return nothing; returning a reversed copy does not satisfy the contract.'],
        [([list('hello')],'The original list becomes [o,l,l,e,h]; the two outer pairs are swapped and the middle l stays put.'),
         ([list('Hannah')],'The result is [h,a,n,n,a,H]. Case stays with each character, so the uppercase H moves to the end.')],
        [[list(text)] for text in ('a','ab','abc','abcd','aa','aba','a b','!?','12 34','Aa','~!@#','racecar',' a ','xyzzy')],
        REVERSE_CHARACTERS,[RETURN_COPY,UNDO_REVERSE],
        ['Returns a new list while leaving the input unchanged.', 'Swaps every pair twice by scanning the entire list, undoing the reversal.'],
        reverse_characters_oracle,random_characters,
        ['The first character belongs at the last position, and the second at the second-last position.',
         'Use two indices moving inward; each outer pair is swapped once.',
         'Set left=0 and right=n-1. While left<right, swap s[left],s[right], then increment left and decrement right.',
         'Stop when the pointers meet or cross. A full-length swap loop reverses every pair twice.'],
        'After each swap, the finished prefix and suffix are already at their final reversed positions. Only the interior remains. Two indices suffice, and the middle character of an odd-length list needs no operation. The judge observes the mutated argument and ignores a returned copy. The independent oracle constructs the reversed list for expected values.',
        'O(n)','O(1)',difficulty=3,
        stress=[([list('a'*50000+'Z'*50000)],list('Z'*50000+'a'*50000))]),
    345: entry('reverse_vowels',[('s','str')],'str',['strings','two-pointers'],
        ['1 <= len(s) <= 300000; all characters are printable ASCII (codes 32–126).',
         'Reverse only the occurrences of a,e,i,o,u and A,E,I,O,U. Every non-vowel stays at its original index; each vowel keeps its own case when it moves.'],
        [(['IceCreAm'],'The vowel sequence I,e,e,A reverses to A,e,e,I, producing AceCreIm. Consonant positions are unchanged.'),
         (['leetcode'],'Vowels e,e,o,e reverse to e,o,e,e, producing leotcede.')],
        [[text] for text in ('a','b','ae','AE','aE','hello','rhythm','AaBbEe','a!e?i','uO','  A z e ',
            'aeiouAEIOU','123','yY','Education')],
        REVERSE_VOWELS,[LOWERCASE_ONLY,REVERSE_EVERYTHING],
        ['Ignores uppercase vowels and leaves them in the wrong positions.', 'Reverses consonants and punctuation as well as vowels.'],
        reverse_vowels_oracle,random_vowels,
        ['Only positions holding vowels may change.',
         'Move a left and right pointer past non-vowels, then swap the two vowel characters.',
         'Convert to a character list. Seek the next vowel at each end, swap them, move inward, and finally join the list.',
         'Use both uppercase and lowercase vowels in the membership set, and move the complete character without changing its case.'],
        'The leftmost vowel belongs at the rightmost vowel position and vice versa. Scanning past consonants preserves their positions, while swapping only vowels reverses that subsequence. Python strings are immutable, so the character list and output require linear space. The oracle independently extracts all vowels and refills vowel positions from the reversed extraction.',
        'O(n)','O(n)',difficulty=3,
        stress=[(['a'*150000+'E'*150000],'E'*150000+'a'*150000),(['b'*300000],'b'*300000)]),
}
for source_id in (324,344):
    BATCH[source_id]['result_mode'] = 'mutated_argument'
    BATCH[source_id]['mutated_parameter'] = 0
BATCH[324]['comparator'] = 'strict_wiggle'
BATCH[324]['statement'] = ('Reorder nums in place so adjacent comparisons alternate strictly less-than and greater-than, '
                           'beginning with nums[0] < nums[1] > nums[2]. '
                           'Keep every value occurrence and return nothing. A valid arrangement is guaranteed to exist.')
