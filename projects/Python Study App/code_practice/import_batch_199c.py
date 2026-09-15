"""Substring counts, bitwise range AND, reward DP, vowel game, and prefix equalization."""
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

def substring_oracle(a):
    s,c=a;return sum(s[i]==c and s[j-1]==c for i in range(len(s)) for j in range(i+1,len(s)+1))
def random_substring(r):
    s=''.join(r.choice('abc') for _ in range(r.randint(1,50)));return [s,r.choice('abc')]
def and_oracle(a):
    n=a[0]
    for x in range(n,-1,-1):
        value=n
        for y in range(x,n):value&=y
        if value==0:return x
def random_and(r):return [r.randint(1,1000)]
def reward_oracle(a):
    values=a[0]
    @lru_cache(None)
    def best(total,mask):return max([total]+[best(total+x,mask|1<<i) for i,x in enumerate(values) if not mask>>i&1 and x>total])
    return best(0,0)
def random_reward(r):return [[r.randint(1,20) for _ in range(r.randint(1,10))]]
def vowel_game_oracle(a):
    s=a[0]
    @lru_cache(None)
    def win(text,alice):
        for i in range(len(text)):
            for j in range(i+1,len(text)+1):
                count=sum(c in 'aeiou' for c in text[i:j])
                if count%2==(1 if alice else 0) and not win(text[:i]+text[j:],not alice):return True
        return False
    return win(s,True)
def random_vowel_game(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,7)))]
def prefix_oracle(a):return max(0,len([1 for x,y in zip(a[0],a[0][1:]) if x!=y]))
def random_prefix(r):return [[r.randint(-5,5) for _ in range(r.randint(1,50))]]

SUBSTRINGS='''def count_substrings_bounded_by_character(s,c):
    count=s.count(c)
    return count*(count+1)//2
'''
RANGE_AND='''def largest_zero_range_and_start(n):
    return (1<<(n.bit_length()-1))-1
'''
REWARD='''def maximum_total_reward(rewardValues):
    reachable=1
    for value in sorted(set(rewardValues)):
        reachable|=(reachable&((1<<value)-1))<<value
    return reachable.bit_length()-1
'''
VOWEL_GAME='''def alice_wins_vowel_game(s):
    return any(c in 'aeiou' for c in s)
'''
PREFIX='''def minimum_prefix_equalization_operations(nums):
    return sum(nums[i]!=nums[i-1] for i in range(1,len(nums)))
'''

BATCH={
3084:entry('count_substrings_bounded_by_character',[('s','str'),('c','str')],'int',['strings','combinatorics'],['Count nonempty substrings whose first and last characters both equal c.','Every occurrence of c forms a one-character substring.','Return the total count.'],[(['abada','a'],'Three a positions give three singletons and three pairs of endpoints, totaling six.'),(['xyz','a'],'With no a occurrence, no substring qualifies.')],[[s,c] for s,c in [('a','a'),('abada','a'),('xyz','a'),('aaa','a'),('abc','b'),('ccddc','c'),('abab','b'),('x','y'),('mississippi','i'),('banana','a'),('leetcode','e'),('zzzz','z'),('abcabc','c'),('01010','0')]],SUBSTRINGS,[SUBSTRINGS.replace('count*(count+1)','count*(count-1)'),SUBSTRINGS.replace('s.count(c)','s.find(c)')],['Omits all one-character substrings.','Uses the first index instead of the number of occurrences.'],substring_oracle,random_substring,['Only the positions containing c matter as endpoints.','Choose one occurrence twice for a singleton or two ordered-by-position distinct occurrences.','For m occurrences the count is m(m+1)/2.','Every valid substring corresponds uniquely to its endpoint occurrence pair.'],'O(n)','O(1)',3),
3125:entry('largest_zero_range_and_start',[('n','int')],'int',['bit manipulation','math'],['Choose the largest integer x<=n.','The bitwise AND of every integer from x through n inclusive must be zero.','Return that largest x.'],[([7],'Starting at three gives 3&4&5&6&7=0, while any larger start keeps a set bit.'),([8],'Seven and eight already AND to zero, so seven is maximal.')],[[n] for n in [1,2,3,4,5,6,7,8,9,15,16,31,32,100]],RANGE_AND,[RANGE_AND.replace('-1',''),RANGE_AND.replace('n.bit_length()-1','n.bit_length()-2')],['Returns the next power of two, which can exceed n.','Uses one fewer bit and produces a start that is not maximal.'],and_oracle,random_and,['Let 2^b be the highest power of two no greater than n.','The number 2^b-1 is immediately below that boundary and shares no high bit with n.','Any larger x retains the high bit across the whole interval until n.','Thus the all-ones value below the top bit is the largest feasible start.'],'O(1)','O(1)',5),
3181:entry('maximum_total_reward',[('rewardValues','list[int]')],'int',['dynamic programming','bitsets'],['Start with total zero and use each index at most once.','A reward may be taken only when its value is strictly greater than the current total.','Return the greatest attainable total.'],[([[1,1,3,3]],'Take one then three to reach four; no remaining value exceeds four.'),([[1,6,4,3,2]],'An optimal increasing-threshold order reaches eleven.')],[[x] for x in [[1],[1,1,3,3],[1,6,4,3,2],[2,2],[1,2,4,8],[3,5,7],[1,3,6,10],[5,1,1],[2,3,9],[10,20,30],[1,5,6],[4,7,15],[2,2,5,11],[1,2,3,4,5]]],REWARD,[REWARD.replace('sorted(set(rewardValues))','sorted(rewardValues,reverse=True)'),REWARD.replace('(1<<value)-1','(1<<value)')],['Processes rewards in descending order, blocking useful small totals.','Keeps only one reachable total below value rather than every eligible total.'],reward_oracle,random_reward,['Track reachable totals as set bits of one integer.','Before taking value v, only totals below v are eligible.','Mask those bits, shift them by v, and OR them into the reachable set.','Processing distinct values increasingly preserves every legal sequence and the highest set bit is the optimum.'],'O(unique values*maximum reward/word size)','O(maximum total bits)',8),
3227:entry('alice_wins_vowel_game',[('s','str')],'bool',['strings','game theory'],['Alice removes a nonempty substring with an odd vowel count.','Bob removes one with an even vowel count; a player without a move loses.','Return whether Alice wins with optimal play.'],[(['leetcoder'],'The string contains vowels, allowing Alice to force a win.'),(['bcdf'],'Alice has no substring with an odd vowel count and loses immediately.')],[[s] for s in ['a','b','leetcoder','bcdf','ae','ab','ba','aaa','bbb','abcde','rhythm','queue','xax','education']],VOWEL_GAME,[VOWEL_GAME.replace('any(','all('),VOWEL_GAME.replace("'aeiou'","'a'" )],['Requires every character to be a vowel.','Recognizes only a as a vowel.'],vowel_game_oracle,random_vowel_game,['Alice has a legal first move exactly when at least one vowel exists.','If a vowel exists, game parity lets Alice remove an odd-vowel segment and answer Bob’s even-vowel removals.','Test whether any character is in the vowel set.','With no vowel Alice loses immediately; with one she has the standard winning strategy.'],'O(n)','O(1)',5),
3353:entry('minimum_prefix_equalization_operations',[('nums','list[int]')],'int',['arrays','greedy'],['One operation adds any integer k to every value in a nonempty prefix.','Make all elements equal.','Return the minimum number of operations.'],[([[1,4,2]],'The two adjacent boundaries differ, and two right-to-left prefix adjustments make all values equal.'),([[5,5,5]],'The array is already equal and needs no operation.')],[[x] for x in [[1],[1,4,2],[5,5,5],[1,2],[2,1],[1,1,2],[1,2,2],[3,1,3],[0,0,1,1],[5,4,3,2,1],[-1,0,-1],[2,2,3,3,2],[9,1,9,1],[1,3,3,1]]],PREFIX,[PREFIX.replace('!=','=='),PREFIX.replace('range(1,len(nums))','range(2,len(nums))')],['Counts equal boundaries instead of unequal ones.','Ignores the first adjacent boundary.'],prefix_oracle,random_prefix,['Work from right to left.','A prefix operation is required exactly where adjacent values differ; it can fix that boundary without disturbing values to its right.','Count unequal adjacent pairs.','Each differing boundary is a lower bound and one matching prefix adjustment per boundary attains it.'],'O(n)','O(1)',3),
}
