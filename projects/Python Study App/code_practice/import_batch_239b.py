"""Colored-house DP, frequency uniqueness, near palindromes, keyboard distance, and games."""
from collections import Counter
from .import_batch_055 import entry

KEYS=['qwertyuiop','asdfghjkl','zxcvbnm']
POSITIONS={character:(row,column) for row,keys in enumerate(KEYS) for column,character in enumerate(keys)}

def robber_oracle(args):
    nums,colors=args;best=0
    for mask in range(1<<len(nums)):
        if all(not(mask>>i&1 and mask>>(i+1)&1 and colors[i]==colors[i+1]) for i in range(len(nums)-1)):
            best=max(best,sum(nums[i] for i in range(len(nums)) if mask>>i&1))
    return best
def random_robber(rng):
    n=rng.randint(1,16);return [[rng.randint(0,30) for _ in range(n)],[rng.randint(1,5) for _ in range(n)]]

def frequency_oracle(args):
    nums=args[0];counts={value:sum(item==value for item in nums) for value in nums}
    for value in nums:
        if sum(count==counts[value] for count in counts.values())==1:return value
    return -1
def random_frequency(rng):return [[rng.randint(-8,8) for _ in range(rng.randint(1,35))]]

def almost_oracle(args):
    text=args[0];answer=0
    for left in range(len(text)):
        for right in range(left,len(text)):
            value=text[left:right+1]
            if any(value[:i]+value[i+1:]==(value[:i]+value[i+1:])[::-1] for i in range(len(value))):answer=max(answer,len(value))
    return answer
def random_almost(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,18)))]

def keyboard_oracle(args):
    previous=POSITIONS['a'];answer=0
    for character in args[0]:
        current=POSITIONS[character];answer+=sum(abs(a-b) for a,b in zip(previous,current));previous=current
    return answer
def random_keyboard(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,60)))]

def game_oracle(args):
    first=second=0;active=0
    for index,points in enumerate(args[0]):
        if points%2:active=1-active
        if index%6==5:active=1-active
        if active==0:first+=points
        else:second+=points
    return first-second
def random_game(rng):return [[rng.randint(0,30) for _ in range(rng.randint(1,60))]]

ROBBER='''def rob_colored_houses(nums,colors):
    skip=0;take=nums[0]
    for i in range(1,len(nums)):
        best=max(skip,take)
        if colors[i-1]==colors[i]:skip,take=best,skip+nums[i]
        else:skip,take=best,best+nums[i]
    return max(skip,take)
'''

FREQUENCY='''def first_unique_frequency(nums):
    from collections import Counter
    counts=Counter(nums);frequencies=Counter(counts.values())
    for value in nums:
        if frequencies[counts[value]]==1:return value
    return -1
'''

ALMOST='''def longest_almost_palindrome(s):
    n=len(s);answer=0
    def expand(left,right):
        while left>=0 and right<n and s[left]==s[right]:left-=1;right+=1
        best=right-left-1
        a,b=left-1,right
        while a>=0 and b<n and s[a]==s[b]:a-=1;b+=1
        best=max(best,b-a-1)
        a,b=left,right+1
        while a>=0 and b<n and s[a]==s[b]:a-=1;b+=1
        return min(n,max(best,b-a-1))
    for center in range(n):answer=max(answer,expand(center,center),expand(center,center+1))
    return answer
'''

KEYBOARD='''def keyboard_finger_distance(s):
    rows=['qwertyuiop','asdfghjkl','zxcvbnm'];positions={}
    for row,keys in enumerate(rows):
        for column,character in enumerate(keys):positions[character]=(row,column)
    previous=positions['a'];answer=0
    for character in s:
        current=positions[character]
        answer+=abs(previous[0]-current[0])+abs(previous[1]-current[1]);previous=current
    return answer
'''

GAME='''def game_score_difference(nums):
    difference=0;sign=1
    for index,points in enumerate(nums):
        if points%2:sign=-sign
        if index%6==5:sign=-sign
        difference+=sign*points
    return difference
'''

def lesson(a,b,c,d):return [a,b,c,d]
R_CASES=[[a,c] for a,c in (([1,4,3,5],[1,1,2,2]),([5],[1]),([2,3],[1,1]),([2,3],[1,2]),([1,2,3],[1,1,1]),([1,2,3],[1,2,1]),([9,1,9],[2,2,2]),([4,5,6,7],[1,1,2,2]),([0,8,0],[3,3,3]),([2,10,2,10],[1,1,1,1]),([3,1,4,1,5],[1,2,2,3,3]),([8,7,6],[1,2,3]),([6,6,6,6],[1,2,2,1]),([1,20,1,20,1],[4,4,5,5,4]),([10,1,1,10],[2,2,3,3]))]
F_CASES=[[[*v]] for v in ([20,10,30,30],[1],[1,1],[1,2],[1,1,2],[1,2,2,3,3,3],[4,4,5,5],[1,1,2,3,3],[0,-1,-1],[5,6,5,7,7,7],[2,2,2,3,3,4],[8,9,8,10,9,11],[1,2,1,3,2,4,4],[7,7,8,9,9,10,10,10],[3,4,5,3,4,6,6,6])]
A_CASES=[[s] for s in ('abca','a','ab','aa','abc','aba','abcdc','racecar','deeee','abbca','abcba','aab','cabba','abcdefgf','abccaa','zzxyyx')]
K_CASES=[[s] for s in ('hello','a','q','z','az','qa','type','keyboard','qwerty','asdf','zxcv','algorithm','leetcode','mississippi','abcdefghijklmnopqrstuvwxyz')]
G_CASES=[[[*v]] for v in ([1,2,3],[2],[1],[2,4],[1,1],[0,0,0],[2,3,4],[1,2,3,4,5,6],[2,2,2,2,2,2],[1,3,5,7],[6,5,4,3,2,1,7],[9,0,9,0,9],[4,8,12,16,20,24,28],[3,6,9,12,15,18],[1,2,4,8,16,32,64])]

BATCH={
3840:entry('rob_colored_houses',[('nums','list[int]'),('colors','list[int]')],'int',['arrays','dynamic programming'],['nums and colors have the same positive length, up to 100,000.','Money values are nonnegative.','You may rob adjacent houses unless those two houses have the same color; maximize the total.'],[([[1,4,3,5],[1,1,2,2]],'Rob houses worth four and five; each conflicts only with its same-colored neighbor, totaling nine.'),([[2,3],[1,2]],'Different colors do not conflict, so both houses yield five.')],R_CASES,ROBBER,[ROBBER.replace("if colors[i-1]==colors[i]","if colors[i-1]!=colors[i]"),ROBBER.replace('skip+nums[i]','take+nums[i]')],['Treats different-colored adjacent houses as conflicting instead of same-colored ones.','When colors match, extends a state that may already include the previous house.'],robber_oracle,random_robber,lesson('Only adjacent selected houses of the same color are forbidden.','Track the best total ending with the previous house skipped or taken.','For a matching-color edge, taking i must extend skip; otherwise it may extend the overall best.','The two states represent every valid choice for the processed prefix, and each transition enforces exactly the new edge constraint.'),'O(n)','O(1)',5),
3843:entry('first_unique_frequency',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['nums contains between 1 and 100,000 integers.','An element qualifies when its total occurrence count is not shared by any other distinct value.','Return the first qualifying value in array order, or -1 when none qualifies.'],[([[20,10,30,30]],'Twenty and ten both occur once, while only thirty occurs twice, so thirty is the first qualifying value.'),([[1,2]],'Both distinct values occur once, so neither frequency is unique and the answer is -1.')],F_CASES,FREQUENCY,[FREQUENCY.replace('frequencies[counts[value]]==1','counts[value]==1'),FREQUENCY.replace('for value in nums:','for value in reversed(nums):')],['Confuses a unique frequency with a value that appears once.','Returns the rightmost qualifying value instead of the first from the left.'],frequency_oracle,random_frequency,lesson('The question compares occurrence counts between distinct values, not individual positions.','Count values, then count how many distinct values have each occurrence count.','Scan the original array and return the first value whose count-frequency equals one.','The second map proves uniqueness of the occurrence count, while the final scan enforces leftmost order.'),'O(n)','O(n)',5),
3844:entry('longest_almost_palindrome',[('s','str')],'int',['strings','two pointers','dynamic programming'],['s is a nonempty lowercase string of length up to 2,000.','Choose a contiguous substring and remove exactly one of its characters.','Return the original substring length when the remaining characters form a palindrome.'],[(['abca'],'Removing b or c leaves a palindrome, so the full length four qualifies.'),(['abc'],'Any length-two substring can lose one character and become a palindrome; length three cannot.')],A_CASES,ALMOST,[ALMOST.replace('a,b=left-1,right','a,b=left,right'),ALMOST.replace('return min(n,max(best,b-a-1))','return best')],['Fails to test deleting the mismatching character on the left side.','Ignores the second deletion direction and returns only the first expansion result.'],almost_oracle,random_almost,lesson('After expanding a palindrome center, the first mismatch is the only place a deletion can help.','Try skipping either side of that mismatch and continue matching outward.','Evaluate both odd and even centers and retain the largest original span, capped by the string length.','Every almost-palindrome has a center; outside its one deleted character, expansion is forced, so one of the two skips reconstructs it.'),'O(n²)','O(1)',6),
3846:entry('keyboard_finger_distance',[('s','str')],'int',['strings','hash maps','simulation'],['s is a nonempty lowercase English string.','Keys occupy rows qwertyuiop, asdfghjkl, and zxcvbnm at zero-based coordinates.','Start on a and sum Manhattan distance for each typed character.'],[(['hello'],'Starting at a and following h, e, l, l, o produces total distance seventeen.'),(['a'],'The finger begins on a, so typing a costs zero.')],K_CASES,KEYBOARD,[KEYBOARD.replace("previous=positions['a']","previous=positions['q']"),KEYBOARD.replace("abs(previous[0]-current[0])+abs(previous[1]-current[1])","abs(previous[1]-current[1])")],['Starts the finger on q instead of a.','Counts horizontal movement but ignores row changes.'],keyboard_oracle,random_keyboard,lesson('Represent each key by its row and column on the given keyboard.','Precompute a character-to-coordinate map, beginning the previous position at a.','For each character, add row difference plus column difference and advance the finger.','Each keystroke cost is exactly its Manhattan distance from the preceding position, so summing them gives the required path length.'),'O(n)','O(1)',5),
3847:entry('game_score_difference',[('nums','list[int]')],'int',['arrays','simulation'],['nums contains nonnegative points for consecutive games.','The active player swaps before scoring whenever points are odd, and also before every sixth game (indices 5,11,…).','Return first-player points minus second-player points.'],[([[1,2,3]],'Odd one swaps to player two, two stays there, and odd three swaps back; -1-2+3=0.'),([[2]],'No swap occurs, so player one scores two and the difference is two.')],G_CASES,GAME,[GAME.replace('difference+=sign*points','difference+=points'),GAME.replace('if index%6==5:sign=-sign','if index%6==0:sign=-sign')],['Adds every score to the first player regardless of the active role.','Applies the periodic swap on indices divisible by six rather than every sixth one-based game.'],game_oracle,random_game,lesson('A sign of +1 or -1 can represent which player receives the next score.','Flip the sign for each triggering condition before adding the current points.','Odd points and sixth-game events are independent, so two simultaneous flips cancel.','The sign matches the active player after exactly the prescribed swaps, and the signed running sum is first score minus second score.'),'O(n)','O(1)',5),
}
