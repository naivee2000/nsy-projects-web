"""Second slice of workbook batch 132: medium greedy and sliding-window problems."""

from .import_batch_055 import entry


def strict_oracle(args):
    n=args[0]
    for base in range(2,n-1):
        digits=[];value=n
        while value:digits.append(value%base);value//=base
        if digits!=digits[::-1]:return False
    return True


def random_strict(rng):return [rng.randint(4,500)]


def nice_oracle(args):
    nums=args[0];best=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            values=nums[left:right+1]
            if all(values[i]&values[j]==0 for i in range(len(values)) for j in range(i+1,len(values))):best=max(best,len(values))
    return best


def random_nice(rng):return [[rng.randint(1,127) for _ in range(rng.randint(1,14))]]


def partition_oracle(args):
    text=args[0];n=len(text);best=n
    for mask in range(1<<(n-1)):
        pieces=[];start=0
        for i in range(n-1):
            if mask>>i&1:pieces.append(text[start:i+1]);start=i+1
        pieces.append(text[start:])
        if all(len(piece)==len(set(piece)) for piece in pieces):best=min(best,len(pieces))
    return best


def random_partition(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,11)))]


def continuous_oracle(args):
    text=args[0];best=1
    for left in range(len(text)):
        for right in range(left,len(text)):
            if all(ord(text[i+1])==ord(text[i])+1 for i in range(left,right)):best=max(best,right-left+1)
    return best


def random_continuous(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,30)))]


def maximum_run_oracle(args):
    nums=args[0];maximum=max(nums);best=0
    for left in range(len(nums)):
        length=0
        while left+length<len(nums) and nums[left+length]==maximum:length+=1
        best=max(best,length)
    return best


def random_maximum_run(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,25))]]


STRICT='''\
def is_strictly_palindromic(n):
    return False
'''

NICE='''\
def longest_nice_subarray(nums):
    left=mask=best=0
    for right,value in enumerate(nums):
        while mask&value:mask^=nums[left];left+=1
        mask|=value;best=max(best,right-left+1)
    return best
'''

PARTITION='''\
def minimum_unique_character_partitions(s):
    used=set();parts=1
    for char in s:
        if char in used:parts+=1;used.clear()
        used.add(char)
    return parts
'''

CONTINUOUS='''\
def longest_continuous_alphabetical_substring(s):
    best=run=1
    for left,right in zip(s,s[1:]):
        run=run+1 if ord(right)==ord(left)+1 else 1;best=max(best,run)
    return best
'''

MAXRUN='''\
def longest_maximum_and_subarray(nums):
    maximum=max(nums);best=run=0
    for value in nums:
        run=run+1 if value==maximum else 0;best=max(best,run)
    return best
'''


BATCH={
2396:entry('is_strictly_palindromic',[('n','int')],'bool',['math','number theory'],['n is at least four.','A strictly palindromic number would be palindromic in every base from two through n-2.','Return whether n satisfies that condition.'],[([9],'In base seven, nine is represented as 12, which is not a palindrome.'),([4],'In base two, four is 100, so it is not strictly palindromic.')],[[n] for n in [5,6,7,8,10,11,12,13,20,25,50,99,100,500]],STRICT,[STRICT.replace('False','True'),'''\
def is_strictly_palindromic(n):
    text=bin(n)[2:]
    return text==text[::-1]
'''],['Returns true for every input despite the universal-base requirement.','Checks only base two and ignores a failing representation in another required base.'],strict_oracle,random_strict,['It is enough to find one required base that always fails.','Consider base n-2 for every n at least four.','n equals 1*(n-2)+2, so its representation is 12, except n=4 where base two is 100; neither is palindromic.','Thus every permitted n has a concrete failing base and the result is always false.'],'O(1)','O(1)',5),
2401:entry('longest_nice_subarray',[('nums','list[int]')],'int',['arrays','sliding windows','bit manipulation'],['A subarray is nice when every pair of distinct elements has bitwise AND zero.','The chosen values must be contiguous.','Return the maximum nice subarray length.'],[([[1,3,8,48,10]],'The subarray [3,8,48] has disjoint set bits and length three.'),([[3,1,5,11,13]],'Every pair of adjacent candidates conflicts, so the maximum length is one.')],[[a] for a in [[1],[1,2],[1,3],[1,2,4,8],[3,4,8],[5,2,8],[7,8,16],[1,1],[2,4,6],[16,8,4,2,1],[10,5,2],[31,32,64],[1,6,8,16],[9,2,4,8]]],NICE,[NICE.replace('while mask&value','if mask&value'),NICE.replace('mask^=nums[left]','mask=0')],['Removes at most one conflicting left value even when several must leave.','Clears every retained bit when shrinking, losing conflicts from values still in the window.'],nice_oracle,random_nice,['In a nice window, OR and XOR of its values describe the same set of occupied bits.','Maintain a bit mask for the current window.','While a new value overlaps the mask, remove left values with XOR; then OR in the new value and update the best length.','Because retained values have disjoint bits, XOR removes exactly one value’s bits, and shrinking to no overlap restores the invariant.'],'O(n)','O(1)',6),
2405:entry('minimum_unique_character_partitions',[('s','str')],'int',['strings','greedy'],['Partition the nonempty string into contiguous substrings.','Every substring must contain no repeated character.','Return the minimum number of substrings.'],[(['abacaba'],'Greedy cuts before each repeated character produce four valid pieces, and fewer cannot avoid those repeats.'),(['ssssss'],'Every repeated s must begin a new substring, giving six parts.')],[[s] for s in ['a','ab','aa','abc','aba','abba','abcdef','abcabc','aabbcc','abcaef','xyzzy','leetcode','abababab','qwertyq']],PARTITION,[PARTITION.replace('used.clear()','used.remove(char)'),PARTITION.replace('parts=1','parts=0')],['Removes only the repeated character from the old part instead of starting a fresh part.','Fails to count the initial nonempty partition.'],partition_oracle,random_partition,['Scan while storing characters in the current part.','When the next character is already present, a cut is mandatory before it.','Increment the part count, clear the set, then add the current character to the new part.','Cutting earlier cannot avoid any mandatory repeat or reduce future cuts, so cutting exactly at each first conflict is optimal.'],'O(n)','O(1)',5),
2414:entry('longest_continuous_alphabetical_substring',[('s','str')],'int',['strings','dynamic programming'],['A substring is alphabetically continuous when every next character is exactly one letter after the previous.','The substring must be contiguous and nonempty.','Return the maximum length.'],[(['abacaba'],'The longest continuous part is ab, with length two.'),(['abcde'],'Every step advances one letter, so the whole length-five string qualifies.')],[[s] for s in ['a','z','ab','az','abcx','xyz','xyza','fed','aabc','bcdefa','mnopq','qrsuv','leetcode','abbcde']],CONTINUOUS,[CONTINUOUS.replace('+1 else 1','+1 else 0'),CONTINUOUS.replace('ord(right)==ord(left)+1','ord(right)>=ord(left)+1')],['Resets a broken run to zero even though the current character begins a length-one run.','Allows skipped alphabet letters instead of requiring the immediate successor.'],continuous_oracle,random_continuous,['Track the continuous run length ending at each character.','Extend it when ord(current)=ord(previous)+1; otherwise reset it to one.','Keep the maximum run observed.','Every qualifying substring ends at some position and its longest possible start is represented by that position’s run value.'],'O(n)','O(1)',5),
2419:entry('longest_maximum_and_subarray',[('nums','list[int]')],'int',['arrays','bit manipulation'],['Choose a nonempty contiguous subarray.','Maximize its bitwise AND value first, then return the greatest length attaining that value.','All nums values are positive.'],[([[1,2,3,3,2,2]],'The maximum possible AND is three, achieved by the consecutive pair [3,3].'),([[1,2,3,4]],'The global maximum four alone is the only subarray attaining AND four, so length is one.')],[[a] for a in [[1],[1,1],[1,2],[2,2,2],[3,3,1,3],[5,5,5,4],[8,4,8,8],[7,7,7,7],[1,9,9,2],[10,10,9,10],[2,4,6,6,6],[15,7,15],[3,5,5,5,3],[100,1,100,100]]],MAXRUN,[MAXRUN.replace('maximum=max(nums)','maximum=min(nums)'),MAXRUN.replace('value==maximum','value<=maximum')],['Targets the global minimum rather than the maximum possible AND.','Counts values no greater than the target instead of only values equal to the global maximum.'],maximum_run_oracle,random_maximum_run,['A subarray AND cannot exceed any of its elements, so the maximum possible value is max(nums).','An AND equals that global maximum only when every included value equals it.','Find the longest consecutive run of elements equal to max(nums).','Each such run attains the maximum, while including any smaller or different-bit value makes the AND lower.'],'O(n)','O(1)',5),
}

BATCH[2401]['boundaries'].extend([[[17,4,14,30,23,28,2]],[[20,1,19,8]]])
