"""Jump scores, spam detection, XOR triplets, threat sorting, and run lengths."""
from itertools import permutations
from .import_batch_055 import entry

def jump_oracle(a):
    nums=a[0];score=[float('-inf')]*len(nums);score[0]=0
    for j in range(1,len(nums)):
        score[j]=max(score[i]+(j-i)*nums[i] for i in range(j))
    return score[-1]
def random_jump(r):return [[r.randint(1,30) for _ in range(r.randint(2,12))]]
def spam_oracle(a):
    banned=a[1];matches=0
    for word in a[0]:
        if any(word==candidate for candidate in banned):matches+=1
    return matches>=2
def random_spam(r):
    words=['red','blue','green','sale','free'];return [[r.choice(words) for _ in range(r.randint(1,15))],r.sample(words,r.randint(1,5))]
def xor_triplets_oracle(a):
    nums=a[0];return len({nums[i]^nums[j]^nums[k] for i in range(len(nums)) for j in range(i,len(nums)) for k in range(j,len(nums))})
def random_xor_triplets(r):
    nums=list(range(1,r.randint(1,9)+1));r.shuffle(nums);return [nums]
def threats_oracle(a):
    remaining=[row[:] for row in a[0]];answer=[]
    while remaining:
        chosen=min(range(len(remaining)),key=lambda i:(-(2*remaining[i][1]+remaining[i][2]),remaining[i][0]))
        answer.append(remaining.pop(chosen))
    return answer
def random_threats(r):
    ids=r.sample(range(1,500),r.randint(1,20));return [[[i,r.randint(0,10),r.randint(0,10)] for i in ids]]
def runs_oracle(a):
    lengths=[];start=0;s=a[0]
    for i in range(1,len(s)+1):
        if i==len(s) or s[i]!=s[start]:lengths.append(i-start);start=i
    return max(lengths.count(x) for x in set(lengths))
def random_runs(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,100)))]

JUMP='''def maximum_jump_score(nums):
    answer=best=0
    for value in nums[:-1]:
        best=max(best,value);answer+=best
    return answer
'''
SPAM='''def is_spam_message(message,bannedWords):
    banned=set(bannedWords)
    return sum(word in banned for word in message)>=2
'''
XOR_TRIPLETS='''def count_unique_xor_triplets(nums):
    n=len(nums)
    return n if n<=2 else 1<<n.bit_length()
'''
THREATS='''def sort_security_threats(threats):
    return sorted(threats,key=lambda row:(-(2*row[1]+row[2]),row[0]))
'''
RUNS='''def maximum_equal_length_runs(s):
    from collections import Counter
    lengths=Counter();start=0
    for i in range(1,len(s)+1):
        if i==len(s) or s[i]!=s[start]:lengths[i-start]+=1;start=i
    return max(lengths.values())
'''

BATCH={
3282:entry('maximum_jump_score',[('nums','list[int]')],'int',['arrays','greedy'],['2 <= len(nums) <= 100,000; nums values are positive.','From i, jump to any j>i and gain (j-i)*nums[i].','Start at index zero and reach the final index with maximum total score.'],[([[1,3,1,5]],'Jump 0-1 and then 1-3 for scores one and six, totaling seven.'),([[4,3,1,3,2]],'Using value four across all four index steps yields total sixteen.')],[[x] for x in [[1,1],[1,3,1,5],[4,3,1,3,2],[5,1],[1,2,3],[3,2,1],[2,10,1],[10,1,1,1],[1,5,2,6],[7,7,7],[2,1,9,1,10],[1,100,1,1],[8,3,9,2,4],[2,4,8,16]]],JUMP,[JUMP.replace('best=max(best,value)','best=value'),JUMP.replace('nums[:-1]','nums')],['Uses only the current value instead of the best value seen before each unit step.','Adds a score contribution after already reaching the last index.'],jump_oracle,random_jump,['Split any jump into unit distances; its source value is paid once for every crossed boundary.','For each boundary, use the greatest value available on its left.','Scan nums except the last, maintain a prefix maximum, and add it.','Choosing the prefix maximum at each boundary can be realized by jumping when that maximum first becomes available.'],'O(n)','O(1)',5),
3295:entry('is_spam_message',[('message','list[str]'),('bannedWords','list[str]')],'bool',['strings','sets'],['message and bannedWords contain lowercase words.','A message is spam when at least two message positions exactly match any banned word.','Repeated matching message words count at each occurrence.'],[([['hello','world','leetcode'],['world','hello']],'Two message positions match banned words, so the message is spam.'),([['hello','programming','fun'],['world','programming']],'Only programming matches, so the message is not spam.')],[[m,b] for m,b in [(['a'],['a']),(['a','a'],['a']),(['a','b'],['a','b']),(['hello','world','leetcode'],['world','hello']),(['hello','programming','fun'],['world','programming']),(['x','y'],['z']),(['free','sale','now'],['free','sale']),(['free','free'],['free']),(['one','two','three'],['two']),(['a','b','a'],['a']),(['red','blue'],['red','green']),(['same'],['same','same']),(['cat','dog','bird'],['dog','bird']),(['clean','message'],['spam'])]],SPAM,[SPAM.replace('>=2','>=1'),SPAM.replace('sum(word in banned for word in message)','len(set(message)&banned)')],['Marks a message spam after only one match.','Counts distinct matching words instead of matching positions.'],spam_oracle,random_spam,['Membership lookup should be constant-time because every message word is checked.','Convert banned words to a set and count matching message positions.','Return whether the count reaches two.','Iterating message positions naturally counts repeated occurrences as required.'],'O(m+b)','O(b)',5),
3513:entry('count_unique_xor_triplets',[('nums','list[int]')],'int',['arrays','bit manipulation','math'],['nums is a permutation of integers 1 through n.','Choose indices i <= j <= k and compute nums[i] XOR nums[j] XOR nums[k].','Return the number of distinct results.'],[([[1,2]],'The possible results are one and two, so the count is two.'),([[3,1,2]],'For n=3 the attainable XOR values fill zero through three, giving four results.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[3,1,2],[1,2,3,4],[4,3,2,1],[2,1,4,3],[1,2,3,4,5],[5,4,3,2,1],[1,2,3,4,5,6],[7,1,4,2,6,3,5],[1,2,3,4,5,6,7,8],[9,8,7,6,5,4,3,2,1]]],XOR_TRIPLETS,[XOR_TRIPLETS.replace('n<=2','n<=3'),XOR_TRIPLETS.replace('n.bit_length()','(n-1).bit_length()')],['Returns n for the three-element case instead of four results.','Uses the next power of two based on n-1 and fails when n itself is a power of two.'],xor_triplets_oracle,random_xor_triplets,['Repeated indices allow every original value, while three distinct choices expand the reachable bit patterns for n>=3.','For n one or two, the answer is n; otherwise all values below the next power of two above n occur.','Return 1 << n.bit_length() for n>=3.','The permutation contains the low integers needed to construct every bit pattern in that range by three XOR choices.'],'O(1)','O(1)',5),
3631:entry('sort_security_threats',[('threats','list[list[int]]')],'list[list[int]]',['arrays','sorting'],['Each row is [unique ID, severity, exploitability].','Its score is 2*severity+exploitability.','Sort by descending score, breaking ties by ascending ID, and return all rows.'],[([[[101,2,3],[102,3,2],[103,3,3]]],'Scores are seven, eight, and nine, so IDs appear 103, 102, 101.'),([[[5,2,2],[1,1,4],[3,3,0]]],'Every score is six, so the tie is ordered by IDs 1, 3, 5.')],[[x] for x in [[[1,0,0]],[[1,1,1],[2,2,2]],[[101,2,3],[102,3,2],[103,3,3]],[[5,2,2],[1,1,4],[3,3,0]],[[9,5,0],[2,0,10]],[[3,1,0],[1,1,0],[2,1,0]],[[10,4,1],[20,3,3]],[[7,0,1],[8,0,0]],[[2,10,10],[1,10,9]],[[4,2,5],[3,3,3]],[[100,1,8],[50,4,1],[75,3,3]],[[1,0,10],[2,5,0]],[[6,2,1],[5,1,3]],[[42,7,7],[9,9,1],[12,4,9]]]],THREATS,[THREATS.replace('-(2*row[1]+row[2])','(2*row[1]+row[2])'),THREATS.replace(',row[0]',',-row[0]')],['Sorts lower scores first.','Breaks equal-score ties by descending ID.'],threats_oracle,random_threats,['Encode both ordering rules in one sort key.','Negate the score for descending order while keeping ID positive for ascending order.','Sort rows by (-(2*severity+exploitability), ID).','Lexicographic tuple ordering applies the ID only when the primary scores tie.'],'O(n log n)','O(n)',5),
3773:entry('maximum_equal_length_runs',[('s','str')],'int',['strings','counting'],['1 <= len(s) <= 100,000; s contains lowercase letters.','A run is a maximal consecutive block of one repeated character.','Group runs by their lengths and return the greatest group size.'],[(['hello'],'The runs h, e, ll, and o have lengths 1,1,2,1; length one occurs three times.'),(['aaabbccccdd'],'Run lengths are three, two, four, and two, so two runs share the most common length.')],[[s] for s in ['a','aa','ab','hello','aaabbccccdd','abcde','aabbcc','aaaab','ababab','mississippi','zzzyyyxxx','aabbaa','abcddddd','aaabcccdd']],RUNS,[RUNS.replace('lengths[i-start]+=1','lengths[i-start]=1'),RUNS.replace('max(lengths.values())','max(lengths)')],['Records only whether a length exists and loses its frequency.','Returns the largest run length rather than the largest number of equal-length runs.'],runs_oracle,random_runs,['First identify maximal runs, independent of which character forms them.','Count how often each run length occurs.','Scan change points, increment the completed run length, and return the largest frequency.','Every maximal run ends at exactly one change point or the end of the string.'],'O(n)','O(n)',5),
}
