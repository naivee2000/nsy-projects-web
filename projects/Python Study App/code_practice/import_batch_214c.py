"""Suffix trie, score split, bitwise window, subsequence power, and bottle exchange."""
from itertools import combinations

from .import_batch_055 import entry


def suffix_oracle(args):
    container, queries = args; answer = []
    for query in queries:
        best = None
        for index, word in enumerate(container):
            common = 0
            while common < min(len(word), len(query)) and word[-1-common] == query[-1-common]:
                common += 1
            candidate = (-common, len(word), index)
            if best is None or candidate < best:
                best = candidate
        answer.append(best[2])
    return answer


def random_suffix(rng):
    container = [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 8)))
                 for _ in range(rng.randint(1, 8))]
    queries = [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 8)))
               for _ in range(rng.randint(1, 8))]
    return [container, queries]


def levels_oracle(args):
    scores = [1 if value else -1 for value in args[0]]
    for split in range(1, len(scores)):
        if sum(scores[:split]) > sum(scores[split:]):
            return split
    return -1


def random_levels(rng):
    return [[rng.randrange(2) for _ in range(rng.randint(2, 20))]]


def or_oracle(args):
    nums, target = args; answer = len(nums) + 1
    for left in range(len(nums)):
        value = 0
        for right in range(left, len(nums)):
            value |= nums[right]
            if value >= target:
                answer = min(answer, right - left + 1); break
    return -1 if answer > len(nums) else answer


def random_or(rng):
    return [[rng.randint(0, 255) for _ in range(rng.randint(1, 18))], rng.randint(0, 300)]


def powers_oracle(args):
    nums, count = args; answer = 0
    for chosen in combinations(nums, count):
        ordered = sorted(chosen)
        answer += min(ordered[index + 1] - ordered[index] for index in range(count - 1))
    return answer % 1_000_000_007


def random_powers(rng):
    size = rng.randint(2, 9)
    return [[rng.randint(-15, 20) for _ in range(size)], rng.randint(2, size)]


def bottles_oracle(args):
    full, requirement = args; empty = 0; consumed = 0
    while full:
        consumed += full; empty += full; full = 0
        if empty >= requirement:
            empty -= requirement; requirement += 1; full = 1
    return consumed


def random_bottles(rng):
    return [rng.randint(1, 100), rng.randint(1, 30)]


SUFFIX = '''def longest_common_suffix_indices(words_container,words_query):
    trie={};best={id(trie):(10**30,10**30)}
    def improve(node,word,index):
        key=id(node);best[key]=min(best.get(key,(10**30,10**30)),(len(word),index))
    for index,word in enumerate(words_container):
        node=trie;improve(node,word,index)
        for char in reversed(word):
            node=node.setdefault(char,{})
            improve(node,word,index)
    answer=[]
    for query in words_query:
        node=trie
        for char in reversed(query):
            if char not in node:break
            node=node[char]
        answer.append(best[id(node)][1])
    return answer
'''


LEVELS = '''def minimum_winning_level_split(possible):
    total=sum(1 if value else -1 for value in possible);left=0
    for index,value in enumerate(possible[:-1],1):
        left+=1 if value else -1
        if left>total-left:return index
    return -1
'''


OR_WINDOW = '''def shortest_or_subarray(nums,k):
    counts=[0]*32;current=0;left=0;answer=len(nums)+1
    for right,value in enumerate(nums):
        current|=value
        for bit in range(32):
            if value>>bit&1:counts[bit]+=1
        while left<=right and current>=k:
            answer=min(answer,right-left+1);removed=nums[left];left+=1
            for bit in range(32):
                if removed>>bit&1:
                    counts[bit]-=1
                    if counts[bit]==0:current^=1<<bit
    return -1 if answer>len(nums) else answer
'''


POWERS = '''def sum_of_minimum_difference_powers(nums,k):
    from functools import lru_cache
    values=sorted(nums);size=len(values);modulo=1000000007;infinity=10**30
    @lru_cache(None)
    def search(index,previous,remaining,minimum):
        if remaining==0:return minimum
        if size-index<remaining:return 0
        answer=search(index+1,previous,remaining,minimum)
        difference=minimum if previous==size else min(minimum,values[index]-values[previous])
        answer+=search(index+1,index,remaining-1,difference)
        return answer%modulo
    return search(0,size,k,infinity)
'''


BOTTLES = '''def maximum_incremental_exchange_drinks(num_bottles,num_exchange):
    consumed=num_bottles;empties=num_bottles
    while empties>=num_exchange:
        empties-=num_exchange;num_exchange+=1
        consumed+=1;empties+=1
    return consumed
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3093: entry('longest_common_suffix_indices',[('words_container','list[str]'),('words_query','list[str]')],'list[int]',['tries','strings','queries'],['Both arrays contain nonempty lowercase strings.','For each query, maximize common suffix length with a container word, then prefer shorter container length and finally smaller index.','Return the selected container index for every query; a zero-length suffix still uses the length/index tie-breaks.'],[([['abcd','bcd','xbcd'],['cd','bcd','xyz']],'Cd chooses index one by shortest length; bcd exactly matches index one; xyz has no suffix match and also chooses the shortest word at index one.'),([['a','ba','ca'],['za','x']],'Za shares suffix a with all entries and chooses the shortest word at index zero; x shares nothing and also chooses index zero.')],[[c,q] for c,q in [(['a'],['a']),(['a'],['b']),(['a','b'],['c']),(['ab','cb'],['xb']),(['abcd','bcd','xbcd'],['cd','bcd','xyz']),(['a','ba','ca'],['za','x']),(['long','ng'],['thing']),(['aa','baa','caa'],['daa']),(['abc','xbc','bc'],['zzbc']),(['z','az','baz'],['qz']),(['cat','dog'],['fog','hat']),(['same','same'],['same']),(['prefix','suffix','fix'],['affix']),(['abcde','cde','de','e'],['xxcde','none'])]],SUFFIX,[SUFFIX.replace('(len(word),index)','(-len(word),index)'),SUFFIX.replace('for char in reversed(query)','for char in query')],['Breaks suffix ties toward the longest container word instead of the shortest.','Traverses query prefixes through a suffix trie and therefore matches the wrong end.'],suffix_oracle,random_suffix,lesson('Reversing every string turns common suffixes into ordinary trie prefixes.','At each trie node store the best container by (length,index); answer a query at its deepest reachable reversed prefix.','Insert reversed words while minimizing metadata at every node, then walk each reversed query until the first missing edge.','Trie depth is the common suffix length, and node metadata applies the two remaining tie-breaks among every word sharing that suffix.'),'O(total characters)','O(total container characters)',8),
3096: entry('minimum_winning_level_split',[('possible','list[int]')],'int',['prefix sums','arrays'],['possible is a binary array of length at least two.','A cleared level scores +1 and an uncleared level scores -1; Alice receives a nonempty prefix and Bob the nonempty suffix.','Return the smallest split where Alice scores strictly more, or -1.'],[([[1,0,1,0]],'After the first level Alice has one point while Bob has negative one, so the minimum split is one.'),([[1,1,1,1,1]],'After three levels Alice has three points and Bob two, so the answer is three.')],[[p] for p in [[0,0],[1,1],[1,0],[0,1],[1,0,1,0],[1,1,1,1,1],[0,0,1,1],[1,0,0,1],[1,1,0,0],[0,1,1,0,1],[1,0,1,1,0],[0,0,0,1,1],[1,1,0,1,0,0],[0,1,0,1,0,1]]],LEVELS,[LEVELS.replace('left>total-left','left>=total-left'),LEVELS.replace('possible[:-1]','possible')],['Accepts a tied score even though Alice must score strictly more.','Allows Alice to take every level, leaving Bob with an empty suffix.'],levels_oracle,random_levels,lesson('Encoding outcomes as +1 and -1 turns each player score into a range sum.','Compute the total once, scan proper prefixes, and compare prefix score with total minus prefix score.','Accumulate left through index n-2; return the first index count where left>total-left.','Every legal division is visited in increasing prefix length, and the two scores partition the encoded total exactly.'),'O(n)','O(1)',5),
3097: entry('shortest_or_subarray',[('nums','list[int]'),('k','int')],'int',['bit manipulation','sliding window','arrays'],['nums contains nonnegative 32-bit integers and k is nonnegative.','Find a nonempty contiguous subarray whose bitwise OR is at least k.','Return its minimum length, or -1 if no qualifying subarray exists.'],[([[1,2,3],2],'The one-element subarray [2] already has OR two, so the answer is one.'),([[1,1,1],8],'Every subarray OR is one, so no qualifying subarray exists.')],[[a,k] for a,k in [([0],0),([0],1),([1],1),([1,2,3],2),([1,1,1],8),([1,2],3),([1,2],4),([8,1,2],10),([4,2,1],7),([0,0,8],8),([5,1,2,7],6),([1,4,2,8],12),([3,3,3],3),([16,1,2,4,8],15)]],OR_WINDOW,[OR_WINDOW.replace('current>=k','current>k'),OR_WINDOW.replace('if counts[bit]==0:current^=1<<bit','current^=1<<bit')],['Requires OR to be strictly greater than k instead of allowing equality.','Clears a removed value’s bits even when other window elements still contribute them.'],or_oracle,random_or,lesson('OR is monotone when extending right, while per-bit counts make removing the left value reversible.','Maintain a sliding window, its OR, and counts of how many elements contribute each bit.','Add right bits; while OR≥k record length and remove left, clearing a bit only when its count reaches zero.','For each right endpoint, shrinking to the first invalid window yields its shortest valid suffix, and all candidate endpoints are considered.'),'O(32*n)','O(32)',5),
3098: entry('sum_of_minimum_difference_powers',[('nums','list[int]'),('k','int')],'int',['dynamic programming','sorting','subsequences'],['nums contains integers and 2≤k≤its length.','The power of a chosen length-k subsequence is the minimum absolute difference between any two selected values.','Sum the powers of all index subsequences modulo 1,000,000,007.'],[([[1,2,3,4],3],'The four triples have minimum gaps one, one, one, and one, so their powers sum to four.'),([[1,1,2],2],'The three index pairs have differences zero, one, and one, summing to two.')],[[a,k] for a,k in [([1,2],2),([1,1],2),([1,2,3],2),([1,2,3],3),([1,2,3,4],3),([1,1,2],2),([-2,0,3],2),([5,1,9,3],2),([0,0,0,1],3),([10,-10,5,-5],3),([2,4,8,16],2),([3,1,4,1,5],3),([-3,-1,2,2,7],4),([9,7,5,3,1],3)]],POWERS,[POWERS.replace('min(minimum,values[index]-values[previous])','values[index]-values[previous]'),POWERS.replace('return search(0,size,k,infinity)','return search(0,size,k,0)')],['Uses only the most recent adjacent selected gap rather than the minimum over every selected gap.','Initializes the running minimum to zero, forcing every subsequence power to zero.'],powers_oracle,random_powers,lesson('After sorting selected values, the minimum pairwise difference occurs between adjacent selected values.','Memoize by scan index, previous selected index, remaining selections, and minimum gap so far.','Skip or take each value; on take update minGap with current-previous; return minGap after exactly k takes.','The recursion enumerates every index subset once, and adjacent-gap updates maintain precisely its power under sorted order.'),'O(states)','O(states)',8),
3100: entry('maximum_incremental_exchange_drinks',[('num_bottles','int'),('num_exchange','int')],'int',['simulation','math'],['num_bottles and num_exchange are positive integers.','Drinking a full bottle creates one empty bottle; exchanging the current required number of empties produces one full bottle.','After each exchange the requirement increases by one; return the maximum total bottles drunk.'],[([13,6],'Drink thirteen, exchange six empties for one drink, then exchange seven of the eight empties for one more, totaling fifteen.'),([10,3],'Successive requirements three, four, and five allow three additional bottles, for thirteen total.')],[[a,b] for a,b in [(1,1),(1,2),(2,1),(3,3),(3,4),(5,2),(6,3),(10,3),(13,6),(20,5),(25,1),(30,10),(50,7),(100,15)]],BOTTLES,[BOTTLES.replace('num_exchange+=1','num_exchange+=2'),BOTTLES.replace('empties+=1','')],['Increases the exchange requirement by two after each trade instead of one.','Forgets that drinking the newly exchanged full bottle produces another empty bottle.'],bottles_oracle,random_bottles,lesson('Drinking immediately never hurts because full bottles only become the empties required for future exchanges.','Track empties, total consumed, and the increasing exchange requirement; perform one exchange whenever affordable.','Initialize consumed=empties=numBottles; while empties≥requirement: pay requirement, increment it, drink the new bottle, and add its empty.','Each exchange is forced and increases resources only through its returned empty, so the loop performs every possible exchange and stops exactly when none remains affordable.'),'O(number of exchanges)','O(1)',5),
}
