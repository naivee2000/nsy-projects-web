"""Bit supersets, uniqueness median, end edits, periodic blocks, and anagram blocks."""
from collections import Counter

from .import_batch_055 import entry


def array_end_oracle(args):
    count, required = args; value = required; seen = 0
    while True:
        if value & required == required:
            seen += 1
            if seen == count:return value
        value += 1


def random_array_end(rng):
    return [rng.randint(1, 30), rng.randint(1, 63)]


def uniqueness_oracle(args):
    nums = args[0]; values = []
    for left in range(len(nums)):
        distinct = set()
        for right in range(left, len(nums)):
            distinct.add(nums[right]); values.append(len(distinct))
    values.sort(); return values[(len(values) - 1) // 2]


def random_uniqueness(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(1, 15))]]


def end_edits_oracle(args):
    initial, target = args; common = 0
    for left in range(len(initial)):
        for right in range(len(target)):
            length = 0
            while left + length < len(initial) and right + length < len(target) and initial[left+length] == target[right+length]:
                length += 1
            common = max(common, length)
    return len(initial) + len(target) - 2 * common


def random_end_edits(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(0, 10))),
            ''.join(rng.choice('abcd') for _ in range(rng.randint(0, 10)))]


def periodic_oracle(args):
    word, size = args; blocks = [word[index:index+size] for index in range(0, len(word), size)]
    return len(blocks) - max(Counter(blocks).values())


def random_periodic(rng):
    block = rng.randint(1, 5); count = rng.randint(1, 8)
    return [''.join(rng.choice('abcd') for _ in range(block * count)), block]


def anagram_oracle(args):
    text = args[0]
    for size in range(1, len(text) + 1):
        if len(text) % size:
            continue
        signatures = [sorted(text[index:index+size]) for index in range(0, len(text), size)]
        if all(signature == signatures[0] for signature in signatures):return size


def random_anagram(rng):
    size = rng.randint(1, 5); block = [rng.choice('abcd') for _ in range(size)]; parts = []
    for _ in range(rng.randint(1, 6)):
        copy = block[:]; rng.shuffle(copy); parts.extend(copy)
    return [''.join(parts)]


ARRAY_END = '''def minimum_increasing_array_end(n,x):
    remaining=n-1;answer=x;bit=0
    while remaining:
        if not (x>>bit&1):
            answer|=(remaining&1)<<bit;remaining>>=1
        bit+=1
    return answer
'''


UNIQUENESS = '''def lower_median_subarray_uniqueness(nums):
    def at_most(limit):
        counts={};left=0;total=0
        for right,value in enumerate(nums):
            counts[value]=counts.get(value,0)+1
            while len(counts)>limit:
                removed=nums[left];left+=1;counts[removed]-=1
                if counts[removed]==0:del counts[removed]
            total+=right-left+1
        return total
    subarrays=len(nums)*(len(nums)+1)//2;rank=(subarrays+1)//2;low,high=1,len(set(nums))
    while low<high:
        middle=(low+high)//2
        if at_most(middle)>=rank:high=middle
        else:low=middle+1
    return low
'''


END_EDITS = '''def minimum_end_edit_operations(initial,target):
    rows=len(initial);columns=len(target);previous=[0]*(columns+1);longest=0
    for row in range(1,rows+1):
        current=[0]*(columns+1)
        for column in range(1,columns+1):
            if initial[row-1]==target[column-1]:
                current[column]=previous[column-1]+1;longest=max(longest,current[column])
        previous=current
    return rows+columns-2*longest
'''


PERIODIC = '''def minimum_k_periodic_replacements(word,k):
    from collections import Counter
    blocks=[word[index:index+k] for index in range(0,len(word),k)]
    return len(blocks)-max(Counter(blocks).values())
'''


ANAGRAM = '''def minimum_anagram_block_length(s):
    from collections import Counter
    for size in range(1,len(s)+1):
        if len(s)%size:continue
        target=Counter(s[:size])
        if all(Counter(s[index:index+size])==target for index in range(0,len(s),size)):return size
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3133: entry('minimum_increasing_array_end',[('n','int'),('x','int')],'int',['bit manipulation','construction'],['n and x are positive integers.','Construct n strictly increasing positive values whose bitwise AND is x.','Return the smallest possible final value; the array itself is not returned.'],[([3,4],'The three smallest supersets of binary 100 are 4,5,6, so the minimum final value is six.'),([2,7],'Seven has all low bits set, so the next superset is fifteen and the answer is fifteen.')],[[n,x] for n,x in [(1,1),(1,7),(2,1),(2,7),(3,4),(4,1),(5,2),(6,5),(10,3),(8,8),(16,15),(7,21),(20,32),(30,63)]],ARRAY_END,[ARRAY_END.replace('remaining=n-1','remaining=n'),ARRAY_END.replace('if not (x>>bit&1)','if not (x>>bit&1) or bit==0')],['Embeds n instead of the zero-based offset n-1, skipping the true n-th superset.','Always consumes an offset bit at bit zero, even when x already fixes that position to one.'],array_end_oracle,random_array_end,lesson('Every array element must contain all one-bits of x; including x itself ensures their AND has no additional forced bit.','Enumerate supersets of x by embedding the binary digits of n-1 into x’s zero-bit positions.','Scan bit positions; whenever x has zero, place the next low bit of n-1 into the answer.','Numeric order among x-supersets matches binary order of the bits inserted into the available positions, so offset n-1 yields the smallest possible n-th value.'),'O(log answer)','O(1)',5),
3134: entry('lower_median_subarray_uniqueness',[('nums','list[int]')],'int',['binary search','sliding window','subarrays'],['nums is a nonempty integer array.','The uniqueness array contains the number of distinct values in every nonempty contiguous subarray.','Sort those counts and return the lower median, using the smaller middle value when their number is even.'],[([[1,2,3]],'The uniqueness counts are 1,1,1,2,2,3; the lower median is one.'),([[1,1,2]],'Counts 1,1,1,1,2,2 sort to the same order, whose lower median is one.')],[[n] for n in [[1],[1,1],[1,2],[1,2,3],[1,1,2],[1,2,1],[1,2,2,3],[3,3,3,3],[1,2,3,4],[4,1,4,2,4],[1,2,1,3,2],[5,4,3,2,1],[1,1,2,2,3,3],[7,1,7,2,7,3]]],UNIQUENESS,[UNIQUENESS.replace('(subarrays+1)//2','subarrays//2+1'),UNIQUENESS.replace('total+=right-left+1','total+=right-left')],['Uses the upper median rank when the number of subarrays is even.','Omits every one-element window from the at-most count.'],uniqueness_oracle,random_uniqueness,lesson('For a candidate d, the number of subarrays with at most d distinct values is monotone in d.','Binary-search the first d whose at-most count reaches the lower-median rank; compute counts by sliding window.','Shrink while distinct>d and add window length at every right endpoint; compare the total with ceil(subarrayCount/2).','The at-most count is the sorted uniqueness-array prefix length, so its first value reaching the target rank is exactly that order statistic.'),'O(n log n)','O(n)',8),
3135: entry('minimum_end_edit_operations',[('initial','str'),('target','str')],'int',['dynamic programming','strings','longest common substring'],['initial and target are strings and may be empty.','One operation adds or removes one character at either end of the current string.','Return the minimum operations required to transform initial into target.'],[(['abcde','cdef'],'Keep the common contiguous block cde, remove ab, and add f, totaling three operations.'),(['abc','xyz'],'No nonempty block can remain in place, so remove three characters and add three, totaling six.')],[[a,b] for a,b in [('', ''),('a',''),('','abc'),('a','a'),('a','b'),('abcde','cdef'),('abc','xyz'),('abcd','bc'),('banana','ananas'),('aaaa','aa'),('abc','zabcx'),('racecar','ace'),('hello','yellow'),('ababa','babab')]],END_EDITS,[END_EDITS.replace('previous[column-1]+1','previous[column]+1'),END_EDITS.replace('rows+columns-2*longest','rows+columns-longest')],['Uses a same-column transition and computes a common subsequence-like value instead of a contiguous match.','Credits each retained common character for only one saved operation instead of one removal and one addition.'],end_edits_oracle,random_end_edits,lesson('Characters not removed from the original must form one contiguous block, and the same block must be the contiguous portion retained in the target.','Find the longest common substring; remove everything around it from initial and add everything around it for target.','Use rolling DP where equal characters extend the previous diagonal; answer=m+n-2*longest.','Any transformation preserves at most one contiguous middle block, and retaining the longest such block saves exactly two operations per character.'),'O(len(initial)*len(target))','O(len(target))',5),
3137: entry('minimum_k_periodic_replacements',[('word','str'),('k','int')],'int',['strings','counting','blocks'],['word is nonempty, k is positive, and its length is divisible by k.','One operation replaces any aligned length-k block with a copy of another aligned block.','Return the minimum operations needed to make every block equal.'],[(['leetcodeleet',4],'The blocks are leet, code, and leet; replacing code once makes the word periodic.'),(['ababab',2],'All three blocks are already ab, so no operation is needed.')],[[w,k] for w,k in [('a',1),('aa',1),('ab',1),('ababab',2),('leetcodeleet',4),('abcabc',3),('abcabd',3),('aaaa',2),('abcd',2),('xyzxyzxyz',3),('0101',2),('ababcdab',2),('zzzzzz',1),('catdogcatdog',3)]],PERIODIC,[PERIODIC.replace('max(Counter(blocks).values())','min(Counter(blocks).values())'),PERIODIC.replace('range(0,len(word),k)','range(1,len(word),k)')],['Keeps the least frequent block instead of the most frequent one.','Starts block slicing at index one and compares misaligned substrings.'],periodic_oracle,random_periodic,lesson('The final period must equal one of the existing aligned blocks, because operations only copy blocks.','Count block frequencies and retain the most common block, replacing every other block once.','Split at multiples of k; return numberOfBlocks-maximumFrequency.','Choosing a block with frequency f costs total-f, so maximizing f minimizes operations and is achievable by copying that block.'),'O(n)','O(n)',5),
3138: entry('minimum_anagram_block_length',[('s','str')],'int',['strings','counting','divisors'],['s is a nonempty lowercase string known to be a concatenation of anagrams of some block.','Each aligned block must have the same character multiset, though its internal order may differ.','Return the smallest possible block length.'],[(['abba'],'Blocks ab and ba are anagrams, so the minimum length is two.'),(['abcabcabc'],'Each length-three block is abc, and no smaller divisor works, so the answer is three.')],[[s] for s in ['a','aa','ab','abba','abab','abcabcabc','aabb','abcacb','zzzzzz','aabbccccbbaa','abcd','baba','xyzzyx','aaabbbababab']],ANAGRAM,[ANAGRAM.replace('Counter(s[index:index+size])==target','set(s[index:index+size])==set(target)'),ANAGRAM.replace('range(1,len(s)+1)','range(2,len(s)+1)')],['Compares only distinct character sets and ignores multiplicities.','Never considers a one-character block, failing uniform strings.'],anagram_oracle,random_anagram,lesson('A feasible block length must divide the total length, and all aligned blocks must share one frequency signature.','Test divisors from smallest upward against the first block’s character counts.','For each dividing size, compare Counter of every aligned slice with Counter(s[:size]); return the first success.','Divisor order guarantees minimality, and equal multisets are exactly the condition for every slice to be an anagram of one common block.'),'O(n*number of divisors)','O(alphabet)',5),
}
