"""Dynamic gaps, bounded compression, divisible pairs, update DP, and count parsing."""
import bisect
from collections import Counter

from .import_batch_055 import entry


def blocks_oracle(args):
    obstacles = [0]; answer = []
    for query in args[0]:
        if query[0] == 1:
            bisect.insort(obstacles, query[1])
        else:
            _, end, size = query; points = [value for value in obstacles if value <= end] + [end]
            answer.append(any(points[index+1]-points[index] >= size for index in range(len(points)-1)))
    return answer


def random_blocks(rng):
    queries = []; used = set()
    for _ in range(rng.randint(1, 24)):
        if rng.random() < .45:
            value = rng.randint(1, 30)
            if value not in used:used.add(value);queries.append([1,value]);continue
        queries.append([2,rng.randint(1,35),rng.randint(1,15)])
    if not any(query[0] == 2 for query in queries):queries.append([2,10,3])
    return [queries]


def compression_oracle(args):
    word = args[0]; output = []; index = 0
    while index < len(word):
        end = index
        while end < len(word) and word[end] == word[index] and end-index < 9:end += 1
        output.append(str(end-index)+word[index]);index=end
    return ''.join(output)


def random_compression(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,40)))]


def pairs_oracle(args):
    first, second, factor = args
    return sum(left % (right*factor) == 0 for left in first for right in second)


def random_pairs(rng):
    return [[rng.randint(1,80) for _ in range(rng.randint(1,12))],
            [rng.randint(1,20) for _ in range(rng.randint(1,10))],rng.randint(1,8)]


def nonadjacent(nums):
    skip = take = 0
    for value in nums:skip,take=max(skip,take),skip+value
    return max(skip,take)


def subsequence_oracle(args):
    nums, queries = args; nums = nums[:]; total = 0
    for position, value in queries:nums[position]=value;total+=nonadjacent(nums)
    return total % 1_000_000_007


def random_subsequence(rng):
    nums = [rng.randint(-20,30) for _ in range(rng.randint(1,12))]
    return [nums,[[rng.randrange(len(nums)),rng.randint(-20,30)] for _ in range(rng.randint(1,12))]]


def better_oracle(args):
    text = args[0]; counts = Counter(); index = 0
    while index < len(text):
        letter = text[index]; index += 1; start = index
        while index < len(text) and text[index].isdigit():index += 1
        counts[letter] += int(text[start:index])
    return ''.join(letter+str(counts[letter]) for letter in sorted(counts))


def random_better(rng):
    parts = [rng.choice('abcdef')+str(rng.randint(1,100)) for _ in range(rng.randint(1,15))]
    return [''.join(parts)]


BLOCKS = '''def block_placement_results(queries):
    import bisect
    coordinates=sorted({0}|{query[1] for query in queries if query[0]==1});index={value:i for i,value in enumerate(coordinates)}
    size=1
    while size<len(coordinates):size*=2
    tree=[0]*(2*size)
    def update(position,value):
        position+=size;tree[position]=value
        while position>1:position//=2;tree[position]=max(tree[2*position],tree[2*position+1])
    def prefix(right):
        left=size;right+=size+1;answer=0
        while left<right:
            if left&1:answer=max(answer,tree[left]);left+=1
            if right&1:right-=1;answer=max(answer,tree[right])
            left//=2;right//=2
        return answer
    obstacles=[0];update(index[0],0);answer=[]
    for query in queries:
        if query[0]==1:
            point=query[1];place=bisect.bisect_left(obstacles,point);previous=obstacles[place-1]
            if place<len(obstacles):following=obstacles[place];update(index[following],following-point)
            obstacles.insert(place,point);update(index[point],point-previous)
        else:
            _,end,length=query;place=bisect.bisect_right(obstacles,end)-1;previous=obstacles[place]
            answer.append(max(prefix(index[previous]),end-previous)>=length)
    return answer
'''


COMPRESSION = '''def bounded_run_length_compression(word):
    answer=[];index=0
    while index<len(word):
        end=index
        while end<len(word) and word[end]==word[index] and end-index<9:end+=1
        answer.append(str(end-index)+word[index]);index=end
    return ''.join(answer)
'''


PAIRS = '''def count_scaled_divisible_pairs(nums1,nums2,k):
    counts={}
    for value in nums2:counts[value]=counts.get(value,0)+1
    answer=0
    for value in nums1:
        if value%k:continue
        quotient=value//k;divisor=1
        while divisor*divisor<=quotient:
            if quotient%divisor==0:
                answer+=counts.get(divisor,0)
                if divisor*divisor!=quotient:answer+=counts.get(quotient//divisor,0)
            divisor+=1
    return answer
'''


SUBSEQUENCE = '''def updated_nonadjacent_subsequence_sum(nums,queries):
    modulo=1000000007;n=len(nums);size=1
    while size<n:size*=2
    negative=-10**30;tree=[[[negative]*2 for _ in range(2)] for _ in range(2*size)]
    def leaf(value):return [[0,negative],[negative,value]]
    def merge(left,right):
        result=[[negative]*2 for _ in range(2)]
        for first in range(2):
            for last in range(2):
                for middle_left in range(2):
                    for middle_right in range(2):
                        if not (middle_left and middle_right):result[first][last]=max(result[first][last],left[first][middle_left]+right[middle_right][last])
        return result
    for index in range(size):tree[size+index]=leaf(nums[index]) if index<n else leaf(negative)
    for node in range(size-1,0,-1):tree[node]=merge(tree[2*node],tree[2*node+1])
    answer=0
    for position,value in queries:
        node=size+position;tree[node]=leaf(value);node//=2
        while node:tree[node]=merge(tree[2*node],tree[2*node+1]);node//=2
        answer=(answer+max(max(row) for row in tree[1]))%modulo
    return answer
'''


BETTER = '''def aggregate_compressed_counts(compressed):
    counts={};index=0
    while index<len(compressed):
        letter=compressed[index];index+=1;start=index
        while index<len(compressed) and compressed[index].isdigit():index+=1
        counts[letter]=counts.get(letter,0)+int(compressed[start:index])
    return ''.join(letter+str(counts[letter]) for letter in sorted(counts))
'''


def lesson(concept,strategy,pseudocode,proof):return [concept,strategy,pseudocode,proof]


BATCH = {
3161:entry('block_placement_results',[('queries','list[list[int]]')],'list[bool]',['segment trees','binary search','ordered sets'],['The number line begins at zero; type-one query [1,x] inserts a new obstacle at positive coordinate x.','Type-two query [2,x,size] asks whether a closed block of the given length fits somewhere in [0,x] without an obstacle strictly inside it.','Return answers only for type-two queries, preserving their order.'],[([[[1,2],[2,3,3],[2,3,1],[2,2,2]]],'After the obstacle at two, length three cannot fit by coordinate three, while lengths one and two can fit.'),([[[2,5,5],[1,3],[2,5,4],[2,5,3]]],'Before insertion the full length five fits; afterward the largest gaps are three and two, so only length three fits.')],[[q] for q in [[[2,1,1]],[[1,2],[2,3,3],[2,3,1],[2,2,2]],[[2,5,5],[1,3],[2,5,4],[2,5,3]],[[1,1],[2,1,1]],[[1,5],[2,4,4]],[[1,2],[1,4],[2,6,2]],[[1,2],[1,4],[2,6,3]],[[2,10,11]],[[1,10],[2,10,10]],[[1,3],[1,7],[2,8,4]],[[1,3],[1,7],[2,8,5]],[[1,5],[2,2,2],[2,7,2]],[[1,2],[1,8],[1,5],[2,10,3]],[[1,8],[1,2],[2,10,7]],[[2,100,100],[1,50],[2,100,50]]]],BLOCKS,[BLOCKS.replace('max(prefix(index[previous]),end-previous)','end-previous'),BLOCKS.replace('if place<len(obstacles):following=obstacles[place];update(index[following],following-point)','if place<len(obstacles):following=obstacles[place]')],['Checks only the trailing gap and ignores a larger completed gap earlier in the range.','Fails to shrink the following obstacle’s gap after inserting a point between two obstacles.'],blocks_oracle,random_blocks,lesson('An obstacle ends a gap whose length is its coordinate minus the preceding obstacle; a query also has an unfinished trailing gap ending at x.','Maintain obstacles in sorted order and gap lengths in a point-update, prefix-maximum segment tree.','On insert split one gap and update two endpoints; on query max(prefix gaps through predecessor, x-predecessor).','These are exactly all obstacle-free intervals inside [0,x], so their maximum decides whether a block fits.'),'O(queries log queries)','O(queries)',8),
3163:entry('bounded_run_length_compression',[('word','str')],'str',['strings','simulation'],['word is a nonempty string of lowercase letters.','Encode each maximal run in left-to-right chunks containing at most nine equal characters.','For every chunk append its one-digit length followed by its character.'],[(['abcde'],'Each character forms a run of length one, producing 1a1b1c1d1e.'),(['aaaaaaaaaaaaaabb'],'Fourteen a characters split into 9a and 5a, followed by 2b.')],[[w] for w in ['a','abcde','aa','aaaaaaaaa','aaaaaaaaaa','aaaaaaaaaaaaaabb','abbccc','zzzzzzzzzzzzzzzzzz','abab','qqqqqqqqqrr','xxyyyyyyyyyy','leetcode','bbbbbbbbbbbbbbbbbbb','aabbaa']],COMPRESSION,[COMPRESSION.replace('end-index<9','end-index<=9'),COMPRESSION.replace("str(end-index)+word[index]","word[index]+str(end-index)")],['Allows a chunk of ten, violating the single-digit maximum count.','Writes character before count instead of the required count-character format.'],compression_oracle,random_compression,lesson('A run longer than nine must be split even though its character does not change.','At each position extend only while the character matches and the chunk length remains below nine.','Emit length and character, then continue at the first unconsumed position.','Each iteration removes the longest legal prefix required by the specification, so concatenating emissions is deterministic.'),'O(n)','O(n)',5),
3164:entry('count_scaled_divisible_pairs',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'int',['number theory','hash tables','divisors'],['Both arrays are nonempty positive-integer arrays and k is positive.','Count index pairs (i,j) satisfying nums1[i] divisible by nums2[j]*k.','Duplicate values correspond to distinct indices and must contribute with their multiplicity.'],[([[1,3,4],[1,3,4],1],'The five valid index pairs use divisors of 1, 3, and 4 from the second array.'),([[8,12],[2,4],2],'Eight pairs with both second-array values; twelve pairs only with two, totaling three pairs.')],[[a,b,k] for a,b,k in [([1,3,4],[1,3,4],1),([8,12],[2,4],2),([1],[1],2),([5],[1],2),([6],[1,2,3,6],1),([6,6],[2,2],1),([10,20],[5],2),([7,14],[7,2],1),([16],[1,2,4,8,16],2),([9,18,27],[3],3),([100,25],[5,10],1),([12,24],[1,2,3,4,6],2),([5,10,15],[1,5],5),([36],[2,3,6,9],2),([48,64],[2,4,8],4)]],PAIRS,[PAIRS.replace('if value%k:continue',''),PAIRS.replace('answer+=counts.get(divisor,0)','answer+=1 if divisor in counts else 0')],['Floor-divides values not divisible by k and may count invalid pairs.','Counts distinct divisor values but ignores duplicate nums2 indices.'],pairs_oracle,random_pairs,lesson('After dividing nums1[i] by k, every valid nums2[j] is a divisor of the quotient.','Frequency-count nums2 and enumerate paired divisors up to the square root of each divisible nums1 value.','Skip values not divisible by k; for d*q=value/k add both stored frequencies, avoiding a square duplicate.','Divisors are enumerated exactly once per complementary pair, and frequency addition counts every eligible second-array index.'),'O(len(nums2)+sum sqrt(nums1/k))','O(distinct nums2)',5),
3165:entry('updated_nonadjacent_subsequence_sum',[('nums','list[int]'),('queries','list[list[int]]')],'int',['segment trees','dynamic programming'],['nums and queries are nonempty; each query [position,value] replaces one array value.','After every update, find the maximum sum of a subsequence containing no adjacent array positions; choosing no value is allowed.','Return the sum of all per-update maxima modulo 1,000,000,007.'],[([[3,5,9],[[1,-2],[0,-3]]],'The updated maxima are twelve and nine, so their required sum is twenty-one.'),([[-1,-2],[[0,5],[1,10]]],'The maxima after the updates are five and ten, totaling fifteen.')],[[n,q] for n,q in [([3,5,9],[[1,-2],[0,-3]]),([-1,-2],[[0,5],[1,10]]),([1],[[0,2]]),([1],[[0,-2]]),([1,2],[[0,3]]),([1,2,3],[[1,10]]),([5,1,5],[[1,9]]),([0,0,0],[[1,4],[2,5]]),([-5,-1,-3],[[1,-10]]),([2,7,9,3,1],[[2,-9]]),([4,-1,2,-1,4],[[2,10],[0,-5]]),([10,1,1,10],[[1,20]]),([1,2,3,4,5],[[4,-5],[0,10]]),([8,-2,6,-1,7],[[3,9],[1,5]])]],SUBSEQUENCE,[SUBSEQUENCE.replace('if not (middle_left and middle_right)','if True'),SUBSEQUENCE.replace('answer=(answer+max(max(row) for row in tree[1]))','answer=max(max(row) for row in tree[1])')],['Allows selecting adjacent boundary elements while merging child intervals.','Returns only the last update’s optimum instead of summing every update result.'],subsequence_oracle,random_subsequence,lesson('An interval can be summarized by whether its first and last positions are selected.','Store four endpoint states per segment and merge pairs unless both touching middle endpoints are selected.','Point-update a leaf, rebuild ancestors, add the maximum root state after every query.','Endpoint states contain all information needed across a boundary; induction on the segment tree proves each state is the best valid subsequence with those endpoints.'),'O((n+queries) log n)','O(n)',8),
3167:entry('aggregate_compressed_counts',[('compressed','str')],'str',['strings','parsing','counting'],['compressed is a nonempty concatenation of lowercase letters followed by positive decimal counts.','A letter may occur in multiple groups and counts may contain multiple digits.','Combine equal letters and output each present letter once in alphabetical order followed by its total count.'],[(['a3c9b2c1'],'The two c groups total ten; sorted output is a3b2c10.'),(['z12a1z8'],'The z counts total twenty and a sorts first, producing a1z20.')],[[s] for s in ['a1','a3c9b2c1','z12a1z8','b2a3','a1a1','x100','c10b20a30','m5m15m80','a9b1a2','q7p6q5','d123c1d7','a10z10m10','f1e2d3c4b5a6','y99y1']],BETTER,[BETTER.replace('counts.get(letter,0)+',''),BETTER.replace('for letter in sorted(counts)','for letter in counts')],['Overwrites repeated letter counts instead of adding them.','Emits letters in encounter order instead of alphabetical order.'],better_oracle,random_better,lesson('Parsing must consume the entire consecutive digit run after each letter, then aggregate repeated letters.','Use an index scan and a frequency map, followed by sorted keys.','Read letter; advance through digits; add parsed integer; join sorted letter+total.','Every encoded group is consumed once and contributes exactly its count; sorting establishes the required canonical order.'),'O(n+alphabet log alphabet)','O(alphabet)',5),
}
