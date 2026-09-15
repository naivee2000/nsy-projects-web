"""Frequency deletion, one collection, anti-palindromes, growth, and ID streams."""
from collections import Counter
from itertools import permutations, product

from .import_batch_055 import entry


def special_oracle(args):
    word, gap = args; counts = list(Counter(word).values()); best = len(word)
    for kept in product(*(range(count + 1) for count in counts)):
        positive = [count for count in kept if count]
        if not positive or max(positive) - min(positive) <= gap:
            best = min(best, len(word) - sum(kept))
    return best


def random_special(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 10))), rng.randint(0, 5)]


def pick_oracle(args):
    nums, count, changes = args; answer = 10**9
    for position in range(len(nums)):
        costs = ([abs(index - position) for index, value in enumerate(nums) if value] +
                 [2] * changes)
        if len(costs) >= count:
            answer = min(answer, sum(sorted(costs)[:count]))
    return answer


def random_pick(rng):
    size = rng.randint(1, 12); nums = [rng.randrange(2) for _ in range(size)]
    changes = rng.randint(0, 5)
    if sum(nums) + changes == 0:
        nums[rng.randrange(size)] = 1
    return [nums, rng.randint(1, sum(nums) + changes), changes]


def anti_oracle(args):
    text = args[0]; size = len(text)
    for candidate in sorted(set(permutations(text))):
        if all(candidate[index] != candidate[size - 1 - index] for index in range(size // 2)):
            return ''.join(candidate)
    return '-1'


def random_anti(rng):
    size = rng.choice((2, 4, 6))
    return [''.join(rng.choice('abcd') for _ in range(size))]


def growth_oracle(args):
    target = args[0]; answer = target - 1
    for increments in range(target):
        value = 1 + increments
        for duplicates in range(target):
            if value * (duplicates + 1) >= target:
                answer = min(answer, increments + duplicates)
                break
    return answer


def random_growth(rng):
    return [rng.randint(1, 100)]


def ids_oracle(args):
    ids, changes = args; counts = {}; answer = []
    for identifier, change in zip(ids, changes):
        counts[identifier] = counts.get(identifier, 0) + change
        answer.append(max(counts.values(), default=0))
    return answer


def random_ids(rng):
    counts = {}; ids = []; changes = []
    for _ in range(rng.randint(1, 15)):
        identifier = rng.randint(1, 6); current = counts.get(identifier, 0)
        change = rng.randint(-current, 8) if current else rng.randint(0, 8)
        counts[identifier] = current + change
        ids.append(identifier); changes.append(change)
    return [ids, changes]


SPECIAL = '''def minimum_k_special_deletions(word,k):
    from collections import Counter
    counts=list(Counter(word).values());answer=len(word)
    for minimum in range(len(word)+1):
        deletions=0
        for count in counts:
            if count<minimum:deletions+=count
            elif count>minimum+k:deletions+=count-minimum-k
        answer=min(answer,deletions)
    return answer
'''


PICK = '''def minimum_moves_to_pick_ones(nums,k,max_changes):
    size=len(nums);counts=[0]*(size+1);positions=[0]*(size+1)
    for index,value in enumerate(nums,1):
        counts[index]=counts[index-1]+value
        positions[index]=positions[index-1]+index*value
    answer=10**30
    for center,value in enumerate(nums,1):
        moves=0;needed=k-value
        for neighbor in (center-1,center+1):
            if needed and 1<=neighbor<=size and nums[neighbor-1]:needed-=1;moves+=1
        created=min(needed,max_changes);needed-=created;moves+=2*created
        if needed<=0:answer=min(answer,moves);continue
        low,high=2,max(center-1,size-center)
        while low<=high:
            radius=(low+high)//2
            left_start=max(1,center-radius);left_end=max(0,center-2)
            right_start=min(size+1,center+2);right_end=min(size,center+radius)
            left_count=counts[left_end]-counts[left_start-1]
            right_count=counts[right_end]-counts[right_start-1]
            if left_count+right_count>=needed:
                cost=(left_count*center-(positions[left_end]-positions[left_start-1])+
                    positions[right_end]-positions[right_start-1]-right_count*center)
                answer=min(answer,moves+cost);high=radius-1
            else:low=radius+1
    return answer
'''


ANTI = '''def lexicographically_smallest_antipalindrome(s):
    chars=sorted(s);size=len(chars);middle=size//2
    if chars[middle]==chars[middle-1]:
        replacement=middle
        while replacement<size and chars[replacement]==chars[replacement-1]:replacement+=1
        index=middle
        while index<size and chars[index]==chars[size-index-1]:
            if replacement>=size:return '-1'
            chars[replacement],chars[index]=chars[index],chars[replacement]
            replacement+=1;index+=1
    return ''.join(chars)
'''


GROWTH = '''def minimum_array_sum_operations(k):
    answer=k-1
    for increments in range(k):
        value=increments+1
        duplicates=(k+value-1)//value-1
        answer=min(answer,increments+duplicates)
    return answer
'''


IDS = '''def most_frequent_id_counts(nums,freq):
    from heapq import heappop,heappush
    counts={};heap=[];answer=[]
    for identifier,change in zip(nums,freq):
        counts[identifier]=counts.get(identifier,0)+change
        heappush(heap,(-counts[identifier],identifier))
        while heap and -heap[0][0]!=counts[heap[0][1]]:heappop(heap)
        answer.append(-heap[0][0] if heap else 0)
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3085: entry('minimum_k_special_deletions',[('word','str'),('k','int')],'int',['strings','counting','greedy'],['word is a nonempty lowercase string and k is nonnegative.','After deletions, the frequencies of any two characters still present may differ by at most k.','Return the minimum number of deleted characters; deleting every occurrence removes that character from comparison.'],[(['aabcaba',0],'The frequencies are a=4, b=2, c=1; deleting one c and one a twice can leave a and b both twice, requiring three deletions.'),(['dabdcbdcdcd',2],'Keeping frequencies within a two-count band requires two deletions.')],[[w,k] for w,k in [('a',0),('aa',0),('ab',0),('aab',0),('aab',1),('aaaabb',0),('aaaabb',2),('abcde',0),('aaaabbbbcc',1),('aabcaba',0),('dabdcbdcdcd',2),('zzzyyx',1),('aaaaabcc',2),('mississippi',1)]],SPECIAL,[SPECIAL.replace('if count<minimum:deletions+=count','if count<minimum:deletions+=minimum-count'),SPECIAL.replace('minimum+k','minimum+k+1')],['Adds missing characters up to the candidate minimum even though only deletion is allowed.','Allows frequency differences of k+1 instead of at most k.'],special_oracle,random_special,lesson('In an optimal nonempty frequency band, its lower bound can be chosen from zero through the word length.','For each candidate minimum v, delete entire smaller groups and trim larger groups to v+k.','Cost(v)=sum(count when count<v; count-v-k when count>v+k); minimize over v.','For fixed v these deletions are individually necessary and sufficient, and every feasible final set has some minimum frequency represented by one candidate.'),'O(alphabet*length)','O(alphabet)',5),
3086: entry('minimum_moves_to_pick_ones',[('nums','list[int]'),('k','int'),('max_changes','int')],'int',['prefix sums','binary search','greedy'],['nums is a nonempty binary array; 1≤k≤number of existing ones plus max_changes.','Choose any collection index; an existing one costs its adjacent-swap distance to reach it, while creating and collecting a reusable adjacent one costs two moves.','Use at most max_changes creations and return the minimum moves needed to collect exactly k ones.'],[([[1,1,0,0,0,1,1,0,0,1],3,1],'Stand at index one, collect its one for free, move the adjacent one once, and create then move one for two more moves, totaling three.'),([[0,0,0,0],2,3],'Stand anywhere with an adjacent cell available and create then collect twice, costing four moves.')],[[a,k,c] for a,k,c in [([1],1,0),([0],1,1),([1,1],2,0),([1,0,1],2,0),([1,0,0,1],2,0),([0,0,0,0],2,3),([1,0,0,0],2,1),([1,1,1],2,0),([1,0,1,0,1],3,0),([1,0,0,0,1],3,1),([0,1,0,1,0],3,1),([1,1,0,0,0,1,1,0,0,1],3,1),([1,0,0,1,0,0,1],2,2),([0,1,1,0,0,1],4,1)]],PICK,[PICK.replace('moves+=2*created','moves+=created'),PICK.replace('created=min(needed,max_changes)','created=max(needed,max_changes)')],['Counts a creation but omits the adjacent swap needed to collect that new one.','Uses at least max_changes creations rather than at most the needed number.'],pick_oracle,random_pick,lesson('For a fixed collection index, costs are zero for its own one, one for adjacent ones, two per permitted creation, then increasing distances for farther originals.','Take the cheap local choices first; use prefix counts and position sums plus a radius binary search for remaining originals.','For every center consume center/adjacent ones, then creations; binary-search the smallest radius containing enough other ones and compute their distance sum.','The choices are ordered by nondecreasing cost, and the prefix formulas sum every original one within the first sufficient radius, so minimizing over centers is global.'),'O(n log n)','O(n)',8),
3088: entry('lexicographically_smallest_antipalindrome',[('s','str')],'str',['strings','greedy','sorting'],['s has positive even length and contains lowercase letters.','Rearrange its existing characters so every mirrored pair contains different characters.','Return the lexicographically smallest valid rearrangement, or -1 when none exists.'],[(['abca'],'Sorted aabc already has different mirrored pairs and is the lexicographically smallest answer.'),(['aaaa'],'Every arrangement pairs an a with a, so transformation is impossible.')],[[s] for s in ['ab','aa','aabb','abca','aaaa','aabc','aabbcc','aabbcd','aaabbb','aaaabc','abcdabcd','zzxxyy','aaaabbbb','aabbccdd','abcabcab']],ANTI,["""def lexicographically_smallest_antipalindrome(s):
    candidate=''.join(sorted(s))
    return candidate if all(candidate[i]!=candidate[-i-1] for i in range(len(s)//2)) else '-1'
""",ANTI.replace('replacement=middle','replacement=size-1')],['Returns impossible whenever the fully sorted arrangement conflicts, even when swaps within the second half can repair it.','Repairs a conflict with the latest available character instead of the earliest, losing the lexicographically smallest result.'],anti_oracle,random_anti,lesson('Sorting is lexicographically best; conflicts can only occur where the same high-frequency character straddles the midpoint.','Start sorted and swap the conflicting second-half positions with the earliest later different characters.','Locate the first character after the midpoint run; while mirrored values match, swap it into the current second-half position, or return -1 if unavailable.','Each repair uses the earliest possible larger character, preserves all earlier positions, and failure means one character occupies more than half the multiset.'),'O(n log n)','O(n)',8),
3091: entry('minimum_array_sum_operations',[('k','int')],'int',['math','enumeration','greedy'],['k is a positive integer; begin with the one-element array [1].','One operation either increments one array value by one or appends a duplicate of an existing value.','Return the minimum operations required to make the array sum at least k.'],[([11],'Raise one to four using three increments, then duplicate it twice; three copies sum to twelve after five operations.'),([1],'The initial sum already reaches one, so zero operations are needed.')],[[k] for k in [1,2,3,4,5,6,7,8,9,10,11,16,25,37]],GROWTH,[GROWTH.replace('(k+value-1)//value','k//value'),GROWTH.replace('duplicates=(k+value-1)//value-1','duplicates=(k+value-1)//value')],['Uses floor division and may stop with a sum below k.','Counts one extra duplication by forgetting the initial array element.'],growth_oracle,random_growth,lesson('After increments create a maximum value x, every duplication should copy x because no smaller copy improves the sum.','Enumerate the number of increments a, then compute how many total copies of value a+1 are needed.','For a=0..k-1, operations=a+ceil(k/(a+1))-1; take the minimum.','Any operation sequence has a largest built value and number of elements, requiring at least x-1 increments and elements-1 duplications; enumeration realizes every such bound.'),'O(k)','O(1)',5),
3092: entry('most_frequent_id_counts',[('nums','list[int]'),('freq','list[int]')],'list[int]',['heaps','hash maps','streaming'],['nums and freq have equal positive length; each step adds freq[i] to that ID count.','Updates never make an ID count negative, and a zero count represents absence.','Return the greatest current count after each update, or zero when every count is zero.'],[([[2,3,2,1],[3,2,-3,1]],'The maximum frequencies after the four updates are three, three, two, and two.'),([[5,5,5],[4,-4,2]],'The same ID changes from four to zero to two, producing [4,0,2].')],[[a,f] for a,f in [([1],[0]),([1],[5]),([1,1],[5,-5]),([1,2],[1,2]),([1,2,1],[3,2,-1]),([5,5,5],[4,-4,2]),([2,3,2,1],[3,2,-3,1]),([1,2,3],[0,0,0]),([1,2,1,2],[2,3,2,-1]),([9,8,9,7],[10,5,-4,8]),([1,1,2,2],[1,1,2,-1]),([4,5,4,5,4],[3,7,5,-2,-8]),([10,20,30,10],[1,1,1,5]),([3,3,3,4,4],[6,-2,-4,1,-1])]],IDS,[IDS.replace('while heap and -heap[0][0]!=counts[heap[0][1]]:heappop(heap)',''),IDS.replace('counts.get(identifier,0)+change','counts.get(identifier,0)+max(change,0)')],['Never removes stale heap entries, so an old maximum can survive decreases.','Ignores removal updates and therefore leaves frequencies too high.'],ids_oracle,random_ids,lesson('Each update invalidates the prior heap entry for one ID, but removing arbitrary heap entries eagerly is unnecessary.','Push every new count and lazily pop while the heap top disagrees with the authoritative count map.','Update count[id], push (-count,id), discard stale tops, and append the current top count.','The map is authoritative; after stale tops are removed, no valid count exceeds the maximum-heap top, so it is exactly the current maximum.'),'O(n log n)','O(n)',5),
}
