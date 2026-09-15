"""Coin coverage, substring queries, edits, bounded windows, and modular powers."""
from itertools import combinations_with_replacement

from .import_batch_055 import entry


def coins_oracle(args):
    coins, target = args

    def covers(additions):
        reachable = {0}
        for value in coins + list(additions):
            reachable |= {total + value for total in tuple(reachable) if total + value <= target}
        return len(reachable) == target + 1

    for count in range(target.bit_length() + 1):
        if any(covers(extra) for extra in combinations_with_replacement(range(1, target + 1), count)):
            return count


def random_coins(rng):
    target = rng.randint(1, 14)
    return [[rng.randint(1, target) for _ in range(rng.randint(1, 8))], target]


def same_end_oracle(args):
    text, queries = args
    answer = []
    for left, right in queries:
        answer.append(sum(text[start] == text[end]
                          for start in range(left, right + 1)
                          for end in range(start, right + 1)))
    return answer


def random_same_end(rng):
    text = ''.join(rng.choice('abcd') for _ in range(rng.randint(2, 18)))
    queries = []
    for _ in range(rng.randint(1, 10)):
        left = rng.randrange(len(text)); right = rng.randrange(left, len(text))
        queries.append([left, right])
    return [text, queries]


def edits_oracle(args):
    word = args[0]
    previous = [int(char != chr(97 + letter)) for letter in range(26) for char in word[:1]]
    for char in word[1:]:
        following = [10**9] * 26
        for letter in range(26):
            following[letter] = (char != chr(97 + letter)) + min(
                previous[prior] for prior in range(26) if abs(letter - prior) >= 2
            )
        previous = following
    return min(previous)


def random_edits(rng):
    return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1, 20)))]


def longest_oracle(args):
    nums, limit = args
    answer = 0
    for left in range(len(nums)):
        counts = {}
        for right in range(left, len(nums)):
            counts[nums[right]] = counts.get(nums[right], 0) + 1
            if max(counts.values()) <= limit:
                answer = max(answer, right - left + 1)
    return answer


def random_longest(rng):
    nums = [rng.randint(1, 7) for _ in range(rng.randint(1, 24))]
    return [nums, rng.randint(1, len(nums))]


def modular_oracle(args):
    variables, target = args

    def power(base, exponent, modulus):
        value = 1 % modulus
        for _ in range(exponent):
            value = value * base % modulus
        return value

    return [index for index, (a, b, c, modulus) in enumerate(variables)
            if power(power(a, b, 10), c, modulus) == target]


def random_modular(rng):
    rows = [[rng.randint(1, 20), rng.randint(1, 12), rng.randint(1, 12), rng.randint(1, 20)]
            for _ in range(rng.randint(1, 10))]
    return [rows, rng.randint(0, 20)]


COINS = '''def minimum_added_coins(coins,target):
    coins=sorted(coins);reach=1;index=answer=0
    while reach<=target:
        if index<len(coins) and coins[index]<=reach:
            reach+=coins[index];index+=1
        else:
            reach*=2;answer+=1
    return answer
'''


SAME_END = '''def same_end_substring_counts(s,queries):
    prefix=[[0]*26]
    for char in s:
        row=prefix[-1].copy();row[ord(char)-97]+=1;prefix.append(row)
    answer=[]
    for left,right in queries:
        counts=[prefix[right+1][letter]-prefix[left][letter] for letter in range(26)]
        answer.append(sum(count*(count+1)//2 for count in counts))
    return answer
'''


EDITS = '''def minimum_almost_equal_edits(word):
    answer=0;index=1
    while index<len(word):
        if abs(ord(word[index])-ord(word[index-1]))<=1:
            answer+=1;index+=2
        else:index+=1
    return answer
'''


LONGEST = '''def longest_frequency_bounded_subarray(nums,k):
    counts={};left=answer=0
    for right,value in enumerate(nums):
        counts[value]=counts.get(value,0)+1
        while counts[value]>k:
            counts[nums[left]]-=1;left+=1
        answer=max(answer,right-left+1)
    return answer
'''


MODULAR = '''def double_modular_good_indices(variables,target):
    return [index for index,(a,b,c,modulus) in enumerate(variables) if pow(pow(a,b,10),c,modulus)==target]
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
2952: entry('minimum_added_coins',[('coins','list[int]'),('target','int')],'int',['greedy','sorting','arrays'],['coins is nonempty, all values are positive, and target is positive.','Each coin may be selected at most once; added coins may have any positive value.','Return the fewest additions needed so every sum from one through target is obtainable.'],[([[1,4,10],19],'Adding values two and eight gives complete coverage through nineteen, and one addition cannot bridge both gaps.'),([[1,1,1],20],'The existing coins cover through three; adding four, eight, and sixteen extends coverage through twenty.')],[[c,t] for c,t in [([1],1),([2],1),([2],2),([3],6),([1,2],3),([1,3],6),([2,4],10),([1,4,10,5,7,19],19),([1,2,2],10),([5,7],12),([1,1,3,9],25),([2,2,2],8),([1,6,11],30),([4,8,16],20)]],COINS,[COINS.replace('coins[index]<=reach','coins[index]<reach'),COINS.replace('reach*=2','reach=2*reach+1')],['Rejects a coin equal to the first unreachable sum even though it closes the gap exactly.','Overstates the new coverage after adding the optimal coin at the coverage boundary.'],coins_oracle,random_coins,lesson('If all sums below reach are possible, only a coin no larger than reach can extend coverage without a gap.','Sort coins; consume any usable coin, otherwise add a coin worth exactly reach.','Maintain the first unreachable sum; consuming value v advances it by v, while adding reach doubles it.','A value above reach cannot form reach, so adding reach is forced-optimal at every gap and maximally extends the invariant interval.'),'O(n log n)','O(n)',5),
2955: entry('same_end_substring_counts',[('s','str'),('queries','list[list[int]]')],'list[int]',['prefix sums','strings','counting'],['s has at least two lowercase letters and every query is an inclusive valid index pair.','A nonempty substring is same-end when its first and last characters match.','Return one count for each query range in the given order.'],[(['abcaab',[[0,0],[1,4],[2,5],[0,5]]],'The four ranges contain respectively 1, 5, 5, and 10 same-end substrings.'),(['abcd',[[0,3],[1,2]]],'All characters are distinct in either range, so only the four and two one-letter substrings qualify.')],[[s,q] for s,q in [('aa',[[0,1]]),('ab',[[0,1]]),('aaa',[[0,2],[1,1]]),('aba',[[0,2]]),('abcabc',[[0,5]]),('zzzz',[[0,3],[1,2]]),('aabb',[[0,1],[2,3],[0,3]]),('leetcode',[[0,7],[1,6]]),('racecar',[[0,6],[1,5]]),('abababa',[[0,6],[2,4]]),('xyzzy',[[0,4]]),('mississippi',[[0,10],[1,9]]),('abcdeabcde',[[0,9],[3,8]]),('qwertyq',[[0,6],[2,2]])]],SAME_END,[SAME_END.replace('count*(count+1)//2','count*(count-1)//2'),SAME_END.replace('prefix[right+1]','prefix[right]')],['Counts only length-at-least-two matches and omits all one-character substrings.','Uses an exclusive right boundary even though query endpoints are inclusive.'],same_end_oracle,random_same_end,lesson('For one character appearing c times in a range, choosing equal endpoints with repetition gives c(c+1)/2 substrings.','Build per-letter prefix counts, recover each query frequency vector, and sum the formula.','For every letter compute c=prefix[r+1]-prefix[l], then add c(c+1)/2.','Every same-end substring is uniquely identified by its endpoint character and ordered endpoint positions, including the same position twice.'),'O(26*(n+q))','O(26n)',5),
2957: entry('minimum_almost_equal_edits',[('word','str')],'int',['greedy','strings'],['word is a nonempty lowercase string.','Adjacent letters are almost equal when their alphabet positions differ by at most one.','One operation changes any character; return the minimum operations eliminating every almost-equal adjacent pair.'],[(['aaaaa'],'Changing the second and fourth letters to c removes all conflicts in two operations.'),(['abddez'],'The pairs ab and dd can be broken with two changes; no one change touches both separated conflicts.')],[[w] for w in ['a','aa','ab','ac','az','abc','aaa','abab','zyx','zyxyxyz','aceg','bcdef','aazaa','algorithm']],EDITS,[EDITS.replace('<=1','==0'),EDITS.replace('answer+=1;index+=2','answer+=1;index+=1')],['Treats identical letters as the only conflict and misses alphabet neighbors.','Rechecks the next pair after changing a character, double-counting conflicts one edit can break.'],edits_oracle,random_edits,lesson('Changing one endpoint of a conflicting adjacent pair can also neutralize the next pair.','Scan left to right; upon a conflict, change the right endpoint conceptually and skip the following comparison.','If abs(word[i]-word[i-1])<=1, add one and advance by two; otherwise advance by one.','The leftmost remaining conflict requires an edit at one endpoint, and choosing its right endpoint never harms the already-clean prefix while covering the maximum future edge.'),'O(n)','O(1)',5),
2958: entry('longest_frequency_bounded_subarray',[('nums','list[int]'),('k','int')],'int',['sliding window','hash maps','arrays'],['nums is nonempty and k is a positive integer no larger than nums length.','A subarray is good when no value occurs more than k times.','Return the maximum length of a contiguous good subarray.'],[([[1,2,3,1,2,3,1,2],2],'The first six values contain each number exactly twice, and every longer window overuses one or two.'),([[5,5,5,5,5,5,5],4],'Any four consecutive values are valid, while a fifth copy exceeds the limit.')],[[n,k] for n,k in [([1],1),([1,1],1),([1,1],2),([1,2,3],1),([1,2,1,2],1),([1,2,1,2],2),([1,1,2,2,3,3],1),([1,2,1,3,1,4],2),([2,2,2,1,2],3),([1,2,3,4,5],5),([7,7,8,8,7,8],2),([1,2,1,3,2,3,3],2),([9,8,9,8,9,7,8],2),([4,4,1,2,4,3,4],2)]],LONGEST,[LONGEST.replace('while counts[value]>k','if counts[value]>k'),LONGEST.replace('counts[nums[left]]-=1;left+=1','counts[value]-=1;left+=1')],['Shrinks only once even when multiple excess copies remain in the window.','Decrements the incoming value instead of the value removed from the left edge.'],longest_oracle,random_longest,lesson('After adding the right value, only that value can newly violate the frequency cap.','Maintain counts in a sliding window and advance left until the new value is within its limit.','Increment nums[right]; while its count exceeds k, decrement nums[left] and move left; maximize width.','The left boundary stops at the earliest valid start for each right endpoint, so that window is the longest valid one ending there.'),'O(n)','O(distinct values)',5),
2961: entry('double_modular_good_indices',[('variables','list[list[int]]'),('target','int')],'list[int]',['modular arithmetic','arrays','simulation'],['Each row is [a,b,c,m] with positive integers, and target is nonnegative.','Index i is good when ((a^b mod 10)^c) mod m equals target.','Return all good zero-based indices in any order.'],[([[[2,3,3,10],[3,3,3,1],[6,1,1,4]],2],'Rows zero and two evaluate to two; row one evaluates to zero.'),([[[39,3,1000,1000]],17],'The inner remainder is nine and nine to the thousandth modulo one thousand is one, so no index qualifies.')],[[v,t] for v,t in [([[1,1,1,1]],0),([[1,1,1,2]],1),([[2,1,1,3]],2),([[2,3,1,10]],8),([[2,3,2,10]],4),([[10,1,1,7]],0),([[3,2,2,5]],1),([[9,2,3,7]],1),([[5,5,5,6]],5),([[7,4,3,11]],3),([[2,10,10,13]],3),([[4,3,2,9],[2,4,3,5]],7),([[6,2,3,8],[8,2,2,9]],0),([[12,5,4,17],[3,7,2,11]],4)]],MODULAR,[MODULAR.replace('pow(a,b,10)','pow(a,b)'),MODULAR.replace('==target','==target%modulus')],['Omits the required inner modulo ten before the second exponentiation.','Reduces the target modulo each row modulus, accepting rows whose result is not literally target.'],modular_oracle,random_modular,lesson('Modular exponentiation must be applied in two separate stages, with modulus ten first.','Use three-argument pow for both exponentiations and retain matching row indices.','For each [a,b,c,m], compute inner=pow(a,b,10), then pow(inner,c,m), and compare with target.','Each computation matches the formula exactly while modular exponentiation avoids constructing enormous powers.'),'O(rows*log(b+c))','O(1) excluding output',5),
}
