"""Median grouping, cyclic letters, repeated subarrays, balanced deletion, and distinct starts."""
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

def medians_oracle(a):
    nums=tuple(a[0])
    @lru_cache(None)
    def best(state):
        if not state:return 0
        answer=0
        for group in combinations(range(len(state)),3):
            median=sorted(state[i] for i in group)[1];rest=tuple(x for i,x in enumerate(state) if i not in group)
            answer=max(answer,median+best(rest))
        return answer
    return best(nums)
def random_medians(r):return [[r.randint(1,20) for _ in range(3*r.randint(1,3))]]
def letters_oracle(a):return max([0]+[26-(ord(c)-97) for c in a[0] if c!='a'])
def random_letters(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,50)))]
def subarrays_oracle(a):
    nums,k=a;values=[max(nums[i:j])-min(nums[i:j]) for i in range(len(nums)) for j in range(i+1,len(nums)+1)]
    return k*max(values)
def random_subarrays(r):return [[r.randint(-50,50) for _ in range(r.randint(1,30))],r.randint(1,30)]
def removals_oracle(a):
    @lru_cache(None)
    def best(s):
        answer=len(s)
        for i in range(len(s)):
            ca=cb=0
            for j in range(i,len(s)):
                ca+=s[j]=='a';cb+=s[j]=='b'
                if ca==cb:answer=min(answer,best(s[:i]+s[j+1:]))
        return answer
    return best(a[0])
def random_removals(r):return [''.join(r.choice('ab') for _ in range(r.randint(1,10)))]
def distinct_oracle(a):return len({c for c in a[0]})
def random_distinct(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,100)))]
def final_oracle(a):return max(a[0][0],a[0][-1])
def random_final(r):return [[r.randint(-20,20) for _ in range(r.randint(1,12))]]

MEDIANS='''def maximum_triplet_median_sum(nums):
    nums=sorted(nums)
    return sum(nums[len(nums)//3::2])
'''
LETTERS='''def minimum_cyclic_letter_operations(s):
    return max([0]+[26-(ord(c)-ord('a')) for c in s if c!='a'])
'''
SUBARRAYS='''def maximum_total_subarray_value(nums,k):
    return k*(max(nums)-min(nums))
'''
REMOVALS='''def minimum_balanced_removal_length(s):
    return abs(s.count('a')-s.count('b'))
'''
DISTINCT='''def maximum_distinct_start_substrings(s):
    return len(set(s))
'''

BATCH={
3627:entry('maximum_triplet_median_sum',[('nums','list[int]')],'int',['arrays','greedy','sorting'],['nums length is divisible by three.','Partition all elements into triplets and sum each triplet’s median.','Return the maximum possible median sum.'],[([[2,1,3,2,1,3]],'Triplets can have medians three and two, producing five.'),([[1,2,3]],'The only triplet has median two.')],[[x] for x in [[1,2,3],[2,1,3,2,1,3],[1,1,1],[1,2,3,4,5,6],[6,5,4,3,2,1],[1,1,2,2,3,3],[5,5,5,1,1,1],[1,9,2,8,3,7],[4,2,6],[10,20,30,40,50,60],[3,3,4,4,5,5],[1,100,101],[2,8,9,3,7,10],[9,1,5,8,2,6]]],MEDIANS,[MEDIANS.replace('len(nums)//3','0'),MEDIANS.replace('::2','::3')],['Includes small values that should be reserved as triplet minima.','Selects every third rather than every second median candidate.'],medians_oracle,random_medians,['Sort the values.','Reserve the smallest third as unavoidable low members, then take every second value from the remainder as a median.','Sum indices n/3, n/3+2, and so on.','Pairing each chosen median with one larger value and one reserved smaller value constructs the optimum.'],'O(n log n)','O(n)',5),
3675:entry('minimum_cyclic_letter_operations',[('s','str')],'int',['strings','greedy'],['In one operation, any chosen characters may advance one step in the cycle a→z→y→...→a defined by the source rule.','Make every character a.','Return the fewest synchronized operations.'],[(['yz'],'Both characters can reach a within two synchronized steps.'),(['aaa'],'No character needs to move.')],[[s] for s in ['a','z','y','yz','aaa','abc','b','az','mnop','leetcode','zzzz','ayz','xza','abcdefghijklmnopqrstuvwxyz']],LETTERS,[LETTERS.replace('max(','min(',1),LETTERS.replace("if c!='a'",'')],['Uses the nearest character rather than the farthest required distance.','Includes a as needing a full cycle of operations.'],letters_oracle,random_letters,['Each non-a letter has a fixed remaining distance 26-index from a.','Characters may advance together, so the total time is the maximum individual distance.','Ignore letters already at a and take the maximum, defaulting to zero.','A shorter schedule cannot finish the farthest letter, and advancing every unfinished letter attains the maximum.'],'O(n)','O(1)',5),
3689:entry('maximum_total_subarray_value',[('nums','list[int]'),('k','int')],'int',['arrays','greedy'],['Choose exactly k nonempty subarrays; the same maximal interval may be chosen repeatedly.','A subarray value is its maximum minus minimum.','Return the largest total value.'],[([[1,3,2],2],'The full array has range two and may be selected twice, totaling four.'),([[-2,5],3],'The range seven repeated three times gives twenty-one.')],[[n,k] for n,k in [([1],1),([1,3,2],2),([-2,5],3),([1,2],1),([5,5],10),([3,1,4],5),([-5,-1,-3],2),([0,10,0],3),([9,8,7],4),([1,100],100),([4,2,6,3],2),([7],20),([-10,10],7),([2,9,1,8],6)]],SUBARRAYS,[SUBARRAYS.replace('max(nums)-min(nums)','max(nums)+min(nums)'),SUBARRAYS.replace('k*','(k-1)*')],['Adds extrema instead of taking their range.','Selects only k-1 subarrays.'],subarrays_oracle,random_subarrays,['No subarray can exceed the whole-array maximum minus minimum.','The full span containing both extrema attains that bound.','Because selections may repeat, use that span k times.','Multiplying the global range by k matches the upper bound and construction.'],'O(n)','O(1)',5),
3746:entry('minimum_balanced_removal_length',[('s','str')],'int',['strings','invariants'],['s contains only a and b.','Repeatedly remove any substring containing equal counts of a and b.','Return the minimum possible remaining length.'],[(['aabbab'],'The entire string has three of each character and can be removed.'),(['aaabb'],'Two a-b pairs can be removed, leaving one a.')],[[s] for s in ['a','b','ab','ba','aa','bb','aabbab','aaabb','abab','baba','aaaab','abbbb','aababb','bbbbba']],REMOVALS,[REMOVALS.replace('abs(','',1).replace(")\n", "\n"),REMOVALS.replace("s.count('b')","0")],['Returns a signed count difference instead of a length.','Ignores b characters entirely.'],removals_oracle,random_removals,['Removing a balanced substring preserves the global difference count(a)-count(b).','Therefore at least the absolute difference must remain.','Repeatedly pair one a with one b through balanced removals until only the majority character remains.','The invariant lower bound is attainable, so its absolute value is the minimum length.'],'O(n)','O(1)',5),
3760:entry('maximum_distinct_start_substrings',[('s','str')],'int',['strings','sets'],['Partition or select substrings so every chosen substring begins with a different letter.','Each lowercase letter can start at most one chosen substring.','Return the greatest possible count.'],[(['abab'],'Only a and b can be distinct starting letters, so the maximum is two.'),(['abcdef'],'Each of six letters can start its own substring.')],[[s] for s in ['a','aa','ab','abab','abcdef','banana','mississippi','leetcode','zzzz','abcabc','qwerty','abca','xyzzy','abcdefghijklmnopqrstuvwxyz']],DISTINCT,[DISTINCT.replace('set(s)','s'),DISTINCT.replace('len(set(s))','len(set(s))-1')],['Counts every character occurrence instead of distinct starts.','Subtracts one from every valid count.'],distinct_oracle,random_distinct,['Every selected substring’s first character must be unique, so distinct letters give an upper bound.','Choose a one-character substring at one occurrence of every distinct letter.','Return the size of set(s).','The construction reaches the distinct-letter upper bound exactly.'],'O(n)','O(alphabet)',5),
3828:entry('optimal_subarray_deletion_final_element',[('nums','list[int]')],'int',['arrays','game theory'],['Alice and Bob alternate removing a nonempty proper contiguous subarray, Alice first.','Alice maximizes and Bob minimizes the sole final value.','Return the final value under optimal play.'],[([[1,5,2]],'Alice can leave endpoint two immediately, and cannot force the interior five, so the value is two.'),([[7,1]],'Alice chooses the larger endpoint seven.')],[[x] for x in [[1],[7,1],[1,5,2],[1,2,3],[3,2,1],[5,1,9,2],[2,2,2],[0,-1,5],[-5,-1,-3],[10,1,1,9],[4,8,3,7,2],[1,100,1],[9,0,8,0,7],[3,6,1,5]]],'''def optimal_subarray_deletion_final_element(nums):
    return max(nums[0],nums[-1])
''',["def optimal_subarray_deletion_final_element(nums):\n    return max(nums)\n","def optimal_subarray_deletion_final_element(nums):\n    return min(nums[0],nums[-1])\n"],['Incorrectly assumes Alice can preserve an interior maximum.','Lets Bob choose between the original endpoints on Alice’s first move.'],final_oracle,random_final,['Only an original endpoint can be made final without exposing a worse reply.','Alice may delete everything except either endpoint in one move.','Choose the larger original endpoint.','The minimax structure bounds the result by that larger endpoint, and Alice’s immediate deletion attains it.'],'O(1)','O(1)',5),
}
