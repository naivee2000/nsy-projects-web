"""Digit encryption, reversed substrings, bounded repetitions, short OR windows, and Harshad numbers."""
from .import_batch_055 import entry

def encrypted(value):
    text=str(value);return int(max(text)*len(text))
def encryption_oracle(a):return sum(encrypted(value) for value in a[0])
def random_encryption(r):return [[r.randint(1,1000) for _ in range(r.randint(1,30))]]
def reverse_substring_oracle(a):
    s=a[0];back=s[::-1]
    return any(s[i:i+2] in back for i in range(len(s)-1))
def random_reverse_substring(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,30)))]
def twice_oracle(a):
    s=a[0];best=0
    for left in range(len(s)):
        counts={}
        for right in range(left,len(s)):
            counts[s[right]]=counts.get(s[right],0)+1
            if max(counts.values())<=2:best=max(best,right-left+1)
            else:break
    return best
def random_twice(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,25)))]
def shortest_oracle(a):
    nums,k=a;best=len(nums)+1
    for left in range(len(nums)):
        value=0
        for right in range(left,len(nums)):
            value|=nums[right]
            if value>=k:best=min(best,right-left+1)
    return -1 if best>len(nums) else best
def random_shortest(r):return [[r.randint(0,127) for _ in range(r.randint(1,30))],r.randint(0,255)]
def harshad_oracle(a):
    total=sum(map(int,str(a[0])));return total if a[0]%total==0 else -1
def random_harshad(r):return [r.randint(1,1000)]

ENCRYPT='''\
def sum_encrypted_integers(nums):
    answer=0
    for value in nums:
        digits=str(value);answer+=int(max(digits)*len(digits))
    return answer
'''
REVERSE_SUBSTRING='''\
def has_length_two_substring_in_reverse(s):
    pairs={s[i:i+2] for i in range(len(s)-1)}
    return any(pair[::-1] in pairs for pair in pairs)
'''
TWICE='''\
def longest_substring_at_most_twice(s):
    counts={};left=0;answer=0
    for right,char in enumerate(s):
        counts[char]=counts.get(char,0)+1
        while counts[char]>2:
            counts[s[left]]-=1;left+=1
        answer=max(answer,right-left+1)
    return answer
'''
SHORTEST='''\
def shortest_subarray_or_at_least_k(nums,k):
    best=len(nums)+1
    for left in range(len(nums)):
        value=0
        for right in range(left,len(nums)):
            value|=nums[right]
            if value>=k:best=min(best,right-left+1);break
    return -1 if best>len(nums) else best
'''
HARSHAD='''\
def harshad_digit_sum(x):
    digit_sum=sum(map(int,str(x)))
    return digit_sum if x%digit_sum==0 else -1
'''

BATCH={
3079:entry('sum_encrypted_integers',[('nums','list[int]')],'int',['arrays','digits','strings'],['Encrypt an integer by replacing every digit with its largest digit.','Preserve the original number of digits.','Return the sum of the encrypted forms of all nums values.'],[([[1,2,3]],'Each one-digit value encrypts to itself, totaling six.'),([[10,21,31]],'The encrypted values are 11,22,33, totaling 66.')],[[x] for x in [[1],[9],[10],[11],[12],[90],[100],[909],[1,2,3],[10,21,31],[999,1],[123,456],[1000,200],[5,55,505]]],ENCRYPT,[ENCRYPT.replace('max(digits)','min(digits)'),ENCRYPT.replace('*len(digits)','')],['Uses the smallest digit rather than the largest.','Produces only one copy of the largest digit.'],encryption_oracle,random_encryption,['Convert each positive integer to its decimal representation.','Find its maximum digit and repeat it for the original digit count.','Convert that repeated text back to an integer and add it.','Replacement makes every output position equal to that maximum, so this constructs the unique encrypted value.'],'O(total digits)','O(max digits)',3),
3083:entry('has_length_two_substring_in_reverse',[('s','str')],'bool',['strings','sets'],['Consider every contiguous substring of s having length two.','Return whether at least one also occurs as a substring of reversed(s).','A string shorter than two has no qualifying substring.'],[(['leetcode'],'The substring ee occurs unchanged in the reversed string.'),(['abcba'],'The substring ab appears as ba in the original, hence ab occurs in the reverse.')],[[s] for s in ['a','ab','aa','abc','aba','abcd','leetcode','abcba','xyyx','azby','aaaa','abca','xyzzy','cabd']],REVERSE_SUBSTRING,[REVERSE_SUBSTRING.replace('pair[::-1]','pair'),REVERSE_SUBSTRING.replace('range(len(s)-1)','range(len(s)-2)')],['Checks every existing pair against itself, making any length-two string pass.','Skips the final adjacent pair.'],reverse_substring_oracle,random_reverse_substring,['A pair xy appears in reversed(s) exactly when yx appears in s.','Store all adjacent length-two substrings of s.','Check whether the reverse of any stored pair is also stored.','This equivalence converts the reversed-string search into a complete set membership test.'],'O(n)','O(n)',3),
3090:entry('longest_substring_at_most_twice',[('s','str')],'int',['strings','sliding window','hash maps'],['Find the longest contiguous substring in which no character appears more than twice.','All characters in the substring count, not just consecutive repetitions.','Return the maximum length.'],[(['bcbbbcba'],'The longest valid window has length four.'),(['aaaa'],'Any valid substring contains at most two a characters, so the answer is two.')],[[s] for s in ['a','aa','aaa','aaaa','ab','abc','abca','bcbbbcba','aabbcc','ababab','abcabc','zzxyzz','abbacaba','abcdef']],TWICE,[TWICE.replace('>2','>3'),TWICE.replace('counts[s[left]]-=1','left+=1')],['Allows a third occurrence of a character.','Moves the window boundary without removing the departed character from its count.'],twice_oracle,random_twice,['Maintain a window whose character counts never exceed two.','When the newly added character reaches three, move left until its count returns to two.','Record the largest valid window length after shrinking.','Only the arriving character can violate the invariant, and the minimal shrink retains the longest valid window ending at each right index.'],'O(n)','O(alphabet)',3),
3095:entry('shortest_subarray_or_at_least_k',[('nums','list[int]'),('k','int')],'int',['arrays','bit manipulation','subarrays'],['Choose a nonempty contiguous subarray.','Its value is the bitwise OR of all contained elements.','Return the minimum length whose OR is at least k, or -1 if none exists.'],[([[1,2,3],2],'The one-element subarray [2] already reaches k.'),([[1,2],4],'Even the full OR is three, so no qualifying subarray exists.')],[[nums,k] for nums,k in [([1],0),([1],1),([1],2),([1,2,3],2),([1,2],4),([0],0),([0],1),([2,1],3),([4,1,2],7),([1,1,1],1),([8,0,1],8),([3,4],7),([5,2,1],6),([0,2,0,4],6)]],SHORTEST,[SHORTEST.replace('value|=nums[right]','value+=nums[right]'),SHORTEST.replace('>=k','>k')],['Adds values instead of combining their bits with OR.','Requires the OR to be strictly greater than k.'],shortest_oracle,random_shortest,['Fix every possible starting index under the source-I constraints.','Extend right while accumulating OR, whose set bits can only increase.','Record the first qualifying end for each start, since later ends are longer.','Every candidate start is examined, and monotonic OR justifies stopping after its shortest qualifying end.'],'O(n^2)','O(1)',3),
3099:entry('harshad_digit_sum',[('x','int')],'int',['math','digits'],['A Harshad number is divisible by the sum of its decimal digits.','Return that digit sum when x is Harshad.','Return -1 otherwise.'],[([18],'The digit sum is nine and eighteen is divisible by nine.'),([23],'The digit sum is five and twenty-three is not divisible by five.')],[[x] for x in [1,10,11,12,18,19,20,21,23,99,100,101,111,999]],HARSHAD,[HARSHAD.replace('x%digit_sum==0','x%digit_sum!=0'),HARSHAD.replace('sum(map(int,str(x)))','sum(map(int,str(x)))+1')],['Reverses the divisibility result.','Tests divisibility using one more than the true digit sum.'],harshad_oracle,random_harshad,['Compute the decimal digit sum directly.','Use the remainder of x divided by that sum.','Return the sum exactly when the remainder is zero.','This is the definition of a Harshad number, so the two return branches are exhaustive.'],'O(digits)','O(digits)',3),
}
BATCH[3095]['boundaries'].append([[1,1],2])
BATCH[3090]['wrong'][1]=TWICE.replace('counts[s[left]]-=1','counts[char]-=1')
