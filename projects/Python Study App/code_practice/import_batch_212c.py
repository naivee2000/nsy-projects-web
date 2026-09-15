"""Bit-count blocks, shortcut distances, keypad assignment, and square chains."""
from collections import Counter
from functools import lru_cache

from .import_batch_055 import entry


def sortable_oracle(args):
    nums = args[0]; transformed = []; start = 0
    while start < len(nums):
        end = start + 1
        while end < len(nums) and nums[end].bit_count() == nums[start].bit_count():
            end += 1
        transformed.extend(sorted(nums[start:end])); start = end
    return transformed == sorted(nums)


def random_sortable(rng):
    return [[rng.randint(1, 255) for _ in range(rng.randint(1, 20))]]


def houses_oracle(args):
    size, first, second = args; answer = [0] * size
    for left in range(1, size + 1):
        for right in range(1, size + 1):
            if left == right:
                continue
            distance = min(abs(left - right), abs(left - first) + 1 + abs(right - second),
                           abs(left - second) + 1 + abs(right - first))
            answer[distance - 1] += 1
    return answer


def random_houses(rng):
    size = rng.randint(2, 32)
    return [size, rng.randint(1, size), rng.randint(1, size)]


def pushes_oracle(args):
    frequencies = list(Counter(args[0]).values())

    @lru_cache(None)
    def assign(index, first, second, third, fourth):
        if index == len(frequencies):
            return 0
        used = (first, second, third, fourth); best = 10**18
        for level, capacity in enumerate((8, 8, 8, 2)):
            if used[level] < capacity:
                following = list(used); following[level] += 1
                best = min(best, (level + 1) * frequencies[index] + assign(index + 1, *following))
        return best

    return assign(0, 0, 0, 0, 0)


def random_pushes(rng):
    return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1, 60)))]


def square_chain_oracle(args):
    counts = Counter(args[0]); answer = 1
    if counts[1]:
        answer = counts[1] if counts[1] % 2 else counts[1] - 1
    for base in counts:
        if base == 1:
            continue
        value = base; length = 1
        while counts[value] >= 2:
            following = value * value
            if counts[following] == 0:
                break
            length += 2; value = following
        if counts[value] < 1:
            length -= 2
        answer = max(answer, length)
    return answer


def random_square_chain(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(2, 25))]]


SORTABLE = '''def can_sort_by_popcount_swaps(nums):
    previous_max=0;start=0
    while start<len(nums):
        bits=nums[start].bit_count();end=start+1;minimum=maximum=nums[start]
        while end<len(nums) and nums[end].bit_count()==bits:
            minimum=min(minimum,nums[end]);maximum=max(maximum,nums[end]);end+=1
        if previous_max>minimum:return False
        previous_max=maximum;start=end
    return True
'''


GLOBAL_BITS = '''def can_sort_by_popcount_swaps(nums):
    groups={}
    for index,value in enumerate(nums):groups.setdefault(value.bit_count(),[]).append((index,value))
    changed=list(nums)
    for entries in groups.values():
        for (index,_),value in zip(entries,sorted(value for _,value in entries)):changed[index]=value
    return changed==sorted(nums)
'''


LOCAL_INVERSIONS = '''def can_sort_by_popcount_swaps(nums):
    return all(nums[i]<=nums[i+1] or nums[i].bit_count()==nums[i+1].bit_count() for i in range(len(nums)-1))
'''


HOUSES_SMALL = '''def count_house_pair_distances_small(n,x,y):
    answer=[0]*n
    for left in range(1,n+1):
        for right in range(left+1,n+1):
            distance=min(right-left,abs(left-x)+1+abs(right-y),abs(left-y)+1+abs(right-x))
            answer[distance-1]+=2
    return answer
'''


HOUSES_LARGE = '''def count_house_pair_distances_large(n,x,y):
    if abs(x-y)<=1:return [2*value for value in reversed(range(n))]
    cycle=abs(x-y)+1;reduced=n-cycle+2
    answer=[2*value for value in reversed(range(reduced))]+[0]*(n-reduced)
    cycle_counts=[cycle*2]*(cycle//2)
    if cycle%2==0:cycle_counts[-1]=cycle
    cycle_counts[0]-=2
    for index,value in enumerate(cycle_counts):answer[index]+=value
    if x>y:x,y=y,x
    for tail in (x-1,n-y):
        if not tail:continue
        length=tail+cycle//2;maximum=4*min((cycle-3)//2,tail);mirror=length-(1-cycle%2)
        extra=[maximum]*length;extra[0]=extra[1]=0
        if cycle%2==0:extra[-1]=0
        for index,value in enumerate(range(4,maximum,4)):
            extra[index+2]=value;extra[mirror-index-1]=value
        for index in range(1,tail+1):extra[index]+=2
        if cycle%2==0:
            for index in range(cycle//2,cycle//2+tail):extra[index]+=2
        for index,value in enumerate(extra):answer[index]+=value
    return answer
'''


PUSHES = '''def minimum_keypad_pushes(word):
    counts=sorted(Counter(word).values(),reverse=True)
    return sum((index//8+1)*frequency for index,frequency in enumerate(counts))
'''


SQUARE_CHAIN = '''def longest_square_chain_subset(nums):
    counts=Counter(nums);answer=counts[1]-(counts[1]%2==0) if counts[1] else 1
    for start in counts:
        if start==1:continue
        value=start;length=0
        while counts[value]>1:
            value*=value;length+=2
        length+=1 if counts[value] else -1
        answer=max(answer,length)
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


HOUSE_CASES = [[n,x,y] for n,x,y in [(2,1,1),(2,1,2),(2,2,1),(3,2,2),(4,1,1),(4,1,4),(5,2,4),(6,1,6),(6,2,5),(7,3,6),(8,2,7),(9,4,5),(10,3,8),(12,1,7),(15,5,12)]]


BATCH = {
3011: entry('can_sort_by_popcount_swaps',[('nums','list[int]')],'bool',['bit manipulation','arrays','sorting'],['nums is a nonempty array of positive integers.','Only adjacent values with equal set-bit counts may be swapped.','Return whether repeated legal swaps can put nums in nondecreasing order.'],[([[8,4,2,30,15]],'The one-bit block can become 2,4,8 and the four-bit block can become 15,30, yielding sorted order.'),([[3,16,8,4,2]],'The leading two-bit value three cannot cross the following one-bit block, so sorting is impossible.')],[[n] for n in [[1],[1,2,3,4,5],[2,1],[4,3,1],[3,5],[7,3,1],[1,3,2],[5,3,7,10],[10,5,3,7],[2,8,4,3],[6,3,5,9],[15,30,7,8],[9,3,12,10],[16,8,4,2,1],[12,10,3,5,6]]],SORTABLE,[GLOBAL_BITS,LOCAL_INVERSIONS],['Allows equal-popcount values to cross intervening blocks, which adjacent swaps cannot do.','Checks only current adjacent inversions and misses values that remain out of order after a legal block is internally sorted.'],sortable_oracle,random_sortable,lesson('Legal swaps permute values only within each maximal contiguous block of one popcount.','For every block, compare its minimum with the maximum of all preceding blocks.','Scan blocks, track min/max, reject when previous_max>block_min, then update previous_max.','Each block can be internally sorted arbitrarily, but blocks cannot cross; the boundary inequality is therefore necessary and sufficient for their sorted concatenation.'),'O(n)','O(1)',5),
3015: entry('count_house_pair_distances_small',[('n','int'),('x','int'),('y','int')],'list[int]',['graphs','enumeration','shortest paths'],['Houses one through n form a path, plus one extra undirected street between x and y; x may equal y.','Count ordered pairs of distinct houses by their shortest-path distance.','Return n counts where index d-1 stores the number of ordered pairs at distance d.'],[([3,1,3],'All six ordered pairs are one street apart after adding the endpoint shortcut.'),([5,2,4],'The counts by distances one, two, and three are ten, eight, and two; larger distances have zero pairs.')],HOUSE_CASES,HOUSES_SMALL,[HOUSES_SMALL.replace('answer[distance-1]+=2','answer[distance-1]+=1'),HOUSES_SMALL.replace('abs(left-y)+1+abs(right-x)','abs(left-y)+abs(right-x)')],['Counts unordered pairs only once instead of both travel directions.','Treats the added x-y street as having zero length.'],houses_oracle,random_houses,lesson('Any shortest route either stays on the path or uses the extra street in one of two directions.','Enumerate unordered endpoint pairs, take the minimum of those three route lengths, and add both orientations.','For i<j compute min(j-i,|i-x|+1+|j-y|,|i-y|+1+|j-x|); add two to its bucket.','A shortest path never benefits from traversing the one extra edge more than once, so the three cases exhaust all routes.'),'O(n^2)','O(n)',5),
3016: entry('minimum_keypad_pushes',[('word','str')],'int',['greedy','counting','sorting'],['word is a nonempty lowercase string.','Eight keys are available; the first assigned letter on a key costs one push, the second two, and so on.','Remap all letters to minimize the total pushes needed to type word.'],[(['abcde'],'Five distinct letters fit in one-push slots, so the five-character word costs five.'),(['xyzxyzxyzxyz'],'The three letters each occupy a one-push slot and occur four times, totaling twelve.')],[[w] for w in ['a','aaaaaaaa','abcdefghi','abcdefghijklmnopqrstuvwxyz','aabbccdd','aabbccdde','zzzyyyxxxwwwvvv','thequickbrownfox','mississippi','leetcode','aabbccddeeffgghhiiiiii','abababababababab','abcdefghijklmnopq','frequencyassignment']],PUSHES,[PUSHES.replace('index//8','index//9'),PUSHES.replace('*frequency','')],['Uses nine keys instead of the available eight, assigning too many letters one-push positions.','Charges each distinct letter once and ignores how often it occurs in the word.'],pushes_oracle,random_pushes,lesson('The keypad offers eight slots at each push depth, and frequent letters should take cheaper slots.','Sort letter frequencies descending and assign them to costs 1 repeated eight times, then 2 repeated eight times, and so on.','For sorted frequency at index i, add frequency*(i//8+1).','An exchange placing a higher frequency in a cheaper slot never increases cost, so descending frequencies paired with ascending slot costs is optimal.'),'O(n+26 log 26)','O(26)',5),
3017: entry('count_house_pair_distances_large',[('n','int'),('x','int'),('y','int')],'list[int]',['graphs','prefix counting','combinatorics'],['Houses one through n form a path plus one extra undirected x-y street, with n up to 100,000 and x possibly equal to y.','Count ordered pairs of distinct houses by shortest-path distance.','Return n buckets in O(n) time; index d-1 corresponds to distance d.'],[([3,1,3],'The shortcut closes a three-house cycle, making all six ordered pairs adjacent.'),([5,2,4],'The shortcut yields ten ordered pairs at distance one, eight at distance two, and two at distance three.')],HOUSE_CASES,HOUSES_LARGE,[HOUSES_LARGE.replace('cycle=abs(x-y)+1','cycle=abs(x-y)'),HOUSES_LARGE.replace('cycle_counts[0]-=2','cycle_counts[0]-=1')],['Omits the shortcut edge itself from the cycle length.','Subtracts only one duplicated path edge instead of both ordered orientations.'],houses_oracle,random_houses,lesson('The graph is a cycle between x and y with up to two path tails attached.','Count path-only pairs, cycle pairs, and each tail-to-cycle correction by distance using symmetric arithmetic progressions.','Normalize x≤y; build the reduced path baseline, add cycle buckets, then add each tail’s symmetric distance contributions.','Every pair lies within the reduced path, within the cycle, or between a tail and the cycle; the corrections partition these cases and count both orientations exactly once.'),'O(n)','O(n)',8),
3020: entry('longest_square_chain_subset',[('nums','list[int]')],'int',['hash maps','enumeration','number theory'],['nums contains at least two positive integers.','Choose an odd-length multiset arrangeable symmetrically as x,x²,x⁴,...,peak,...,x⁴,x²,x.','Return the greatest possible selected length; duplicate copies are required on both sides of every non-peak level.'],[([[5,4,1,2,2]],'Two copies of two with one four form the valid arrangement [2,4,2] of length three.'),([[1,3,2,4]],'No nontrivial chain has duplicate endpoints and only one 1 may be used for odd length, so the answer is one.')],[[n] for n in [[1,1],[1,1,1],[1,1,1,1],[2,2],[2,2,4],[2,2,4,4,16],[3,3,9],[3,3,9,9,81],[2,2,4,4],[4,4,16,16,256],[5,5,25,625],[10,10,100,100,10000],[2,3,4,9,2,3],[1,2,2,4,4,16,1]]],SQUARE_CHAIN,[SQUARE_CHAIN.replace('counts[value]>1','counts[value]>0'),SQUARE_CHAIN.replace("answer=counts[1]-(counts[1]%2==0) if counts[1] else 1","answer=counts[1] if counts[1] else 1")],['Allows a chain level with only one copy even though both symmetric sides require it.','Uses an even number of ones even though every valid pattern has odd length.'],square_chain_oracle,random_square_chain,lesson('Every non-peak chain value needs two copies, while the final peak needs one; value one is a special fixed point.','Count values and try each non-one value as a base, repeatedly squaring while two copies exist.','Add two per paired level, then add one for an existing peak or remove the last pair if no peak exists; use the largest odd count of ones.','A base uniquely determines all later powers, so the count walk finds its longest feasible symmetric chain and checking every base is exhaustive.'),'O(n log log maxValue)','O(n)',5),
}
