"""Replacement slot for the probability candidate retained in quarantine."""
from collections import Counter
from functools import lru_cache
from .import_batch_055 import entry

def minimum_length_oracle(a):
    @lru_cache(None)
    def best(s):
        answer=len(s)
        for center,char in enumerate(s):
            left=next((i for i in range(center-1,-1,-1) if s[i]==char),None)
            right=next((i for i in range(center+1,len(s)) if s[i]==char),None)
            if left is not None and right is not None:answer=min(answer,best(s[:left]+s[left+1:right]+s[right+1:]))
        return answer
    return best(a[0])
def random_minimum_length(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,9)))]

REFERENCE='''def minimum_length_after_symmetric_deletions(s):
    from collections import Counter
    return sum(1 if count%2 else 2 for count in Counter(s).values())
'''

BATCH={
3223:entry('minimum_length_after_symmetric_deletions',[('s','str')],'int',['strings','counting','greedy'],['Choose a center character that has the same character somewhere on both sides.','Delete the nearest matching character on each side while keeping the center.','Return the minimum length after any number of operations.'],[(['abaacbcbb'],'Repeated deletions reduce the character counts to a total length of five.'),(['aaa'],'Delete the two outer a characters around the middle one, leaving length one.')],[[s] for s in ['a','aa','aaa','aaaa','abaacbcbb','abc','abca','aabaa','abbba','aaabbb','abcabc','cccccc','abacaba','aabbcc']],REFERENCE,[REFERENCE.replace('1 if count%2 else 2','2 if count%2 else 1'),REFERENCE.replace('Counter(s).values()','set(Counter(s).values())')],['Keeps two copies for odd counts and one for even counts.','Deduplicates equal frequency values and loses character groups.'],minimum_length_oracle,random_minimum_length,['Each operation removes two copies of one character, preserving its count parity.','A positive odd count can be reduced to one; a positive even count can be reduced to two.','Sum one for odd frequencies and two for even frequencies.','Available centers permit these pair deletions independently for each character until the parity minimum remains.'],'O(n)','O(alphabet)',5),
}
