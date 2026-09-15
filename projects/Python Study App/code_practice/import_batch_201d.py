"""Device transfers, rotated palindromes, pair merges, and cyclic rotations."""
from functools import lru_cache
from .import_batch_055 import entry

def ratings_oracle(a):
    start=tuple(tuple(sorted(row)) for row in a[0]);devices=len(start)
    @lru_cache(None)
    def search(state,used):
        best=sum(row[0] if row else 0 for row in state)
        for source,row in enumerate(state):
            if used>>source&1:continue
            for index,value in enumerate(row):
                for destination in range(devices):
                    if destination==source:continue
                    nxt=[list(x) for x in state];nxt[source].pop(index);nxt[destination].append(value);nxt[destination].sort()
                    best=max(best,search(tuple(tuple(x) for x in nxt),used|(1<<source)))
        return best
    return search(start,0)
def random_ratings(r):
    m=r.randint(1,3);n=r.randint(1,3);return [[[r.randint(1,12) for _ in range(n)] for _ in range(m)]]
def palindrome_oracle(a):
    s=a[0];n=len(s);best=10**9
    for shift in range(n):
        text=s[shift:]+s[:shift];cost=shift
        for i in range(n//2):
            distance=abs(ord(text[i])-ord(text[-1-i]));cost+=min(distance,26-distance)
        best=min(best,cost)
    return best
def random_palindrome(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,20)))]
def largest_oracle(a):
    answer=[]
    for count in a[0]:
        start='a'*count;seen={start};todo=[start]
        while todo:
            text=todo.pop()
            for i in range(len(text)-1):
                if text[i]==text[i+1] and text[i]!='z':
                    nxt=text[:i]+chr(ord(text[i])+1)+text[i+2:]
                    if nxt not in seen:seen.add(nxt);todo.append(nxt)
        answer.append(max(seen))
    return answer
def random_largest(r):return [[r.randint(1,14) for _ in range(r.randint(1,6))]]
def rotations_oracle(a):
    s,k=a;return sum(sum(text[i]==text[i+1] for i in range(len(text)-1))==k for shift in range(len(s)) for text in [s[shift:]+s[:shift]])
def random_rotations(r):
    n=r.randint(1,30);return [''.join(r.choice('abc') for _ in range(n)),r.randint(0,max(0,n-1))]
def good_oracle(a):
    nums=a[0];half=len(nums)//2;return sum(sum((nums[shift:]+nums[:shift])[:half])>sum((nums[shift:]+nums[:shift])[half:]) for shift in range(len(nums)))
def random_good(r):return [[r.randint(-20,20) for _ in range(2*r.randint(1,15))]]

RATINGS='''def maximum_device_rating_sum(units):
    if len(units[0])==1:return sum(row[0] for row in units)
    second_sum=0;smallest_first=float('inf');smallest_second=float('inf')
    for row in units:
        first,second=sorted(row)[:2];second_sum+=second;smallest_first=min(smallest_first,first);smallest_second=min(smallest_second,second)
    return second_sum-smallest_second+smallest_first
'''
PALINDROME='''def minimum_rotated_palindrome_operations(s):
    n=len(s);answer=float('inf')
    for shift in range(n):
        cost=shift
        for left in range(n//2):
            a=ord(s[(left+shift)%n])-97;b=ord(s[(n-1-left+shift)%n])-97;distance=abs(a-b);cost+=min(distance,26-distance)
        answer=min(answer,cost)
    return answer
'''
LARGEST='''def largest_strings_after_pair_merges(nums):
    answer=[]
    for value in nums:
        text=''
        for bit in range(25,-1,-1):
            text+=chr(97+bit)*((value>>bit)&1)
        answer.append(text)
    return answer
'''
ROTATIONS='''def count_rotations_with_score(s,k):
    answer=0
    for shift in range(len(s)):
        text=s[shift:]+s[:shift]
        answer+=sum(text[i]==text[i+1] for i in range(len(text)-1))==k
    return answer
'''
GOOD='''def count_good_half_sum_rotations(nums):
    n=len(nums);half=n//2;left=sum(nums[:half]);right=sum(nums[half:]);answer=left>right
    for i in range(n-1):
        left-=nums[i];right+=nums[i];left+=nums[(i+half)%n];right-=nums[(i+half)%n];answer+=left>right
    return answer
'''

BATCH={
3961:entry('maximum_device_rating_sum',[('units','list[list[int]]')],'int',['arrays','greedy'],['units is a nonempty rectangular matrix of positive capacities.','A device rating is its minimum unit, or zero if empty; each device may donate one unit at most once to another device.','Return the maximum possible sum of device ratings.'],[([[[1,3],[2,2]]],'Move the one from the first device; its remaining rating three plus the recipient rating one totals four.'),([[[5,5,5],[1,1,1]]],'No transfer improves the existing rating sum six.')],[[x] for x in [[[1]],[[1],[2]],[[1,3],[2,2]],[[5,5,5],[1,1,1]],[[1,2,3],[4,5,6]],[[10,1],[2,3]],[[1,100],[2,99],[3,98]],[[4,4],[4,4]],[[9,8,7]],[[1],[10],[5]],[[2,6,7],[1,8,9]],[[5,10],[1,2],[3,4]],[[100,1,2],[50,3,4]],[[7,7,9],[2,8,8],[1,5,6]]]],RATINGS,[RATINGS.replace('smallest_first','smallest_second',1),RATINGS.replace('sorted(row)[:2]','sorted(row,reverse=True)[:2]')],['Loses the globally smallest first unit needed for the receiving device.','Uses the two largest units of each device rather than the two smallest.'],ratings_oracle,random_ratings,['Every donating device can remove its smallest unit and raise its rating to its second smallest.','All removed minima may be placed into one receiver, whose final rating is the global smallest removed value.','Sum all second minima, then replace the smallest second minimum with the global first minimum.','Choosing the receiver with smallest second minimum minimizes the sacrificed gain; no other move can raise a donor beyond its second minimum.'],'O(total units log width)','O(width)',5),
4021:entry('minimum_rotated_palindrome_operations',[('s','str')],'int',['strings','enumeration'],['s contains lowercase letters.','An operation either rotates left once or increments one letter cyclically from z to a.','Return the minimum operations to reach any palindrome.'],[(['abc'],'One rotation and one cyclic letter adjustment can form a palindrome in two operations.'),(['aba'],'The original string is already a palindrome.')],[[s] for s in ['a','aa','ab','aba','abc','abcd','az','za','racecar','aabb','xyz','zzza','leetcode','abca']],PALINDROME,[PALINDROME.replace('min(distance,26-distance)','distance'),PALINDROME.replace('cost=shift','cost=0')],['Ignores wraparound letter increments.','Treats every cyclic rotation as free.'],palindrome_oracle,random_palindrome,['There are only n distinct rotations, with rotation cost equal to the left-shift count.','For each mirrored pair, either letter can be incremented cyclically until they meet at minimum circular distance.','Evaluate every shift and add pair distances.','Pair edits are independent within a fixed rotation, so their minima sum exactly.'],'O(n^2)','O(1)',5),
4036:entry('largest_strings_after_pair_merges',[('nums','list[int]')],'list[str]',['strings','bit manipulation'],['Each positive x begins as x copies of a.','Two adjacent equal letters below z may merge into one next letter.','Return the lexicographically largest reachable string for every x.'],[([[2,5,7]],'Binary decompositions yield b, ca, and cba.'),([[1,4,8]],'Powers of two merge completely into a, c, and d respectively.')],[[x] for x in [[1],[2],[3],[2,5,7],[1,4,8],[6],[9],[10],[12],[15],[16],[5,5],[3,7,11],[1,2,4,8,14]]],LARGEST,[LARGEST.replace('range(25,-1,-1)','range(26)'),LARGEST.replace('((value>>bit)&1)','(value>>bit)')],['Emits letters from low to high, producing a lexicographically smaller order.','Repeats letters by quotient counts and represents the same mass noncanonically.'],largest_oracle,random_largest,['Merging equal letters is binary carrying: two level-j letters become one level-(j+1) letter.','The final multiset is the set bits of x, and descending letters maximize lexicographic order.','Scan bits high to low and append the corresponding letter for each set bit.','Any unmerged equal pair can be replaced by a larger leading possibility, so the fully carried descending representation is maximal.'],'O(items*log max(nums))','O(log max(nums))',5),
4043:entry('count_rotations_with_score',[('s','str'),('k','int')],'int',['strings','sliding window'],['s is nonempty and 0<=k<len(s).','A cyclic rotation’s score counts equal adjacent pairs at ordinary indices 0..n-2; the wrap pair is not counted.','Return how many of the n rotations have score k.'],[(['aab',1],'Two rotations contain exactly one equal adjacent pair.'),(['abc',0],'All three rotations have no equal adjacent pair.')],[[s,k] for s,k in [('a',0),('aa',1),('ab',0),('aab',1),('abc',0),('aaa',2),('abab',0),('abba',1),('aabb',2),('abcd',1),('zzza',2),('abca',1),('abcabc',0),('aabaa',3)]],ROTATIONS,[ROTATIONS.replace('range(len(s))','range(len(s)-1)'),ROTATIONS.replace('==k','>=k')],['Omits the final cyclic rotation.','Counts rotations whose score exceeds k as well.'],rotations_oracle,random_rotations,['A rotation changes only the pair removed at one end and the pair introduced at the other.','The score can be updated in constant time per shift, or directly recomputed for clarity.','Count each of n shifts whose n-1 internal adjacent comparisons equal k.','Enumerating all shifts covers every cyclic rotation exactly once.'],'O(n^2)','O(n)',3),
4044:entry('count_good_half_sum_rotations',[('nums','list[int]')],'int',['arrays','sliding window'],['nums has positive even length.','For each cyclic rotation, compare the sum of its first half with its second half.','Return the number whose first-half sum is strictly larger.'],[([[1,2,3,4,5,6]],'Three of the six rotations have a larger first-half sum.'),([[1,1]],'Both rotations tie, so neither is good.')],[[x] for x in [[1,1],[2,1],[1,2],[1,2,3,4,5,6],[1,1,1,1],[4,3,2,1],[1,10,1,10],[5,1,2,3],[0,0,1,0],[3,3,1,1,2,2],[10,0,0,0],[1,2,1,2,1,2],[9,8,7,6,5,4,3,2],[2,5,1,8,3,7]]],GOOD,[GOOD.replace('left>right','left>=right'),GOOD.replace('range(n-1)','range(n-2)')],['Counts tied half sums as good.','Omits one noninitial rotation.'],good_oracle,random_good,['Maintain the two half sums while shifting the rotation start.','Move the outgoing first value to the second half and the crossing midpoint value to the first.','Update both sums in O(1) and test strict inequality for every rotation.','The updates preserve the exact partition of each rotated array into equal halves.'],'O(n)','O(1)',5),
}
BATCH[3961]['wrong'][0]=RATINGS.replace('return second_sum-smallest_second+smallest_first','return second_sum')
BATCH[3961]['wrong_reasons'][0]='Forgets the receiver must retain the globally smallest donated unit.'
