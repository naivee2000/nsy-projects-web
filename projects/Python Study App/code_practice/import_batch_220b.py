"""Exact prefix cover, multiset windows, unique towers, one mismatch, and implicit strings."""
from itertools import combinations,product
from collections import Counter
from .import_batch_055 import entry

def cover_oracle(args):
    words,target=args;valid={word[:i] for word in words for i in range(1,len(word)+1)};dp=[10**9]*(len(target)+1);dp[0]=0
    for i in range(len(target)):
        for word in valid:
            if target.startswith(word,i):dp[i+len(word)]=min(dp[i+len(word)],dp[i]+1)
    return -1 if dp[-1]==10**9 else dp[-1]
def random_cover(rng):
    alphabet='abc';words=[''.join(rng.choice(alphabet) for _ in range(rng.randint(1,7))) for _ in range(rng.randint(1,7))]
    return [words,''.join(rng.choice(alphabet) for _ in range(rng.randint(1,12)))]

def contain_oracle(args):
    word1,word2=args;need=Counter(word2);answer=0
    for left in range(len(word1)):
        have=Counter()
        for right in range(left,len(word1)):
            have[word1[right]]+=1;answer+=all(have[c]>=v for c,v in need.items())
    return answer
def random_contain(rng):
    alphabet='abcd';return [''.join(rng.choice(alphabet) for _ in range(rng.randint(1,18))),''.join(rng.choice(alphabet) for _ in range(rng.randint(1,8)))]

def towers_oracle(args):
    limits=args[0];best=-1
    for heights in product(*(range(1,limit+1) for limit in limits)):
        if len(set(heights))==len(heights):best=max(best,sum(heights))
    return best
def random_towers(rng):return [[rng.randint(1,8) for _ in range(rng.randint(1,7))]]

def sequence_oracle(args):
    word1,word2=args
    for indices in combinations(range(len(word1)),len(word2)):
        if sum(word1[i]!=word2[j] for j,i in enumerate(indices))<=1:return list(indices)
    return []
def random_sequence(rng):
    alphabet='abc';n=rng.randint(2,11);m=rng.randint(1,n-1)
    return [''.join(rng.choice(alphabet) for _ in range(n)),''.join(rng.choice(alphabet) for _ in range(m))]

def game_oracle(args):
    k,operations=args;word='a'
    for operation in operations:
        changed=''.join(chr((ord(c)-96)%26+97) for c in word)
        word+=word if operation==0 else changed
    return word[k-1]
def random_game(rng):
    size=rng.randint(1,10);operations=[rng.randrange(2) for _ in range(size)];return [rng.randint(1,1<<size),operations]

COVER='''def minimum_valid_prefix_strings(words,target):
    n=len(target);longest=[0]*n
    for word in set(words):
        text=word+'#'+target;z=[0]*len(text);left=right=0
        for i in range(1,len(text)):
            if i<=right:z[i]=min(right-i+1,z[i-left])
            while i+z[i]<len(text) and text[z[i]]==text[i+z[i]]:z[i]+=1
            if i+z[i]-1>right:left,right=i,i+z[i]-1
        offset=len(word)+1
        for i in range(n):longest[i]=max(longest[i],min(len(word),z[offset+i]))
    pieces=0;end=farthest=0
    for i in range(n):
        if i>farthest:return -1
        farthest=max(farthest,i+longest[i])
        if i==end:
            if end==farthest:return -1
            pieces+=1;end=farthest
            if end>=n:return pieces
    return -1
'''
CONTAIN='''def count_rearrangeable_containing_substrings(word1,word2):
    from collections import Counter
    required=Counter(word2);missing=len(required);window=Counter();left=0;answer=0
    for char in word1:
        window[char]+=1
        if window[char]==required[char]:missing-=1
        while missing==0:
            outgoing=word1[left]
            if window[outgoing]==required[outgoing]:missing+=1
            window[outgoing]-=1;left+=1
        answer+=left
    return answer
'''
TOWERS='''def maximum_unique_tower_height_sum(maximum_height):
    ceiling=10**30;answer=0
    for limit in sorted(maximum_height,reverse=True):
        height=min(limit,ceiling-1)
        if height<=0:return -1
        answer+=height;ceiling=height
    return answer
'''
SEQUENCE='''def smallest_almost_equal_index_sequence(word1,word2):
    n=len(word1);m=len(word2);suffix=[m]*(n+1);wanted=m-1
    for i in range(n-1,-1,-1):
        if wanted>=0 and word1[i]==word2[wanted]:wanted-=1
        suffix[i]=wanted+1
    answer=[];changed=False;wanted=0
    for i,char in enumerate(word1):
        if char==word2[wanted] or (not changed and suffix[i+1]<=wanted+1):
            changed|=char!=word2[wanted];answer.append(i);wanted+=1
            if wanted==m:return answer
    return []
'''
GAME='''def kth_implicit_game_character(k,operations):
    length=1;used=0
    while length<k:length*=2;used+=1
    shifts=0
    while length>1:
        if k>length//2:k-=length//2;shifts+=operations[used-1]
        length//=2;used-=1
    return chr(ord('a')+shifts%26)
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3292:entry('minimum_valid_prefix_strings',[('words','list[str]'),('target','str')],'int',['strings','greedy','z algorithm'],['words contains at most 100 lowercase strings with total length at most 100,000; target length is at most 50,000.','Any nonempty prefix of any word may be appended, and prefixes may be reused.','Return the minimum number of valid prefixes forming target exactly, or -1.'],[([['abc','aaaaa','bcdef'],'aabcdabc'],'The target splits into aa, bcd, and abc, so three prefixes suffice.'),([['abababab','ab'],'ababaababa'],'Two copies of prefix ababa form the target.')],[[w,t] for w,t in [(['a'],'a'),(['a'],'b'),(['abc'],'ab'),(['abc'],'abcabc'),(['ab','bc'],'abbc'),(['ab','bc'],'ac'),(['aaaa'],'aaaaa'),(['cat','car'],'cacar'),(['x','xy','xyz'],'xyzx'),(['abc','bcd'],'abcd'),(['ababa'],'ababababa'),(['hello','help'],'helhello'),(['aa','a'],'aaaa'),(['abc','def'],'abcdefabc')]],COVER,[COVER.replace("word+'#'+target","word+'#'+word"),COVER.replace('farthest=max(farthest,i+longest[i])','farthest=i+longest[i]')],['Computes matches against each word itself instead of the target.','Forgets farther reach discovered by an earlier starting position.'],cover_oracle,random_cover,lesson('At each target position, only the longest matching dictionary prefix matters because every shorter prefix is also valid.','Compute exact word-versus-target LCP lengths with Z arrays, then treat each position as an interval reach.','Greedily take a new piece when the current frontier ends, extending to the farthest reachable endpoint.','The Z values are collision-free, and the standard minimum-jump exchange argument proves each frontier choice optimal.'),'O(total word length+words·target length)','O(word length+target length)',8),
3298:entry('count_rearrangeable_containing_substrings',[('word1','str'),('word2','str')],'int',['sliding windows','hash maps','strings'],['word1 has up to 1,000,000 lowercase letters and word2 up to 10,000.','A substring is valid when its character multiset contains every character of word2 with multiplicity.','Return the number of valid substrings of word1.'],[(['bcca','abc'],'Only bcca contains at least one a, b, and c.'),(['abcabc','abc'],'Every substring of length at least three that covers the required counts contributes, totaling ten.')],[[a,b] for a,b in [('a','a'),('a','b'),('ab','a'),('aaa','aa'),('abc','abcd'),('aaaa','a'),('abab','ab'),('abcabc','aaabc'),('zzzz','zz'),('cabca','abc'),('mississippi','ssi'),('abcdabc','bd'),('bbbba','ab'),('xyzxyz','xyz')]],CONTAIN,[CONTAIN.replace('answer+=left','answer+=1'),CONTAIN.replace('window[outgoing]-=1','window[outgoing]-=2')],['Counts only one valid start per ending position.','Removes two copies of each outgoing character.'],contain_oracle,random_contain,lesson('For each right endpoint, valid starts form a prefix 0..left-1 once the window is shrunk just past validity.','Track required multiplicities and how many distinct requirements remain unmet.','While all are met, remove from the left; then add left to the answer.','All earlier starts contain the minimal valid window, and no later start does, so left is the exact contribution.'),'O(n+m)','O(alphabet)',6),
3301:entry('maximum_unique_tower_height_sum',[('maximum_height','list[int]')],'int',['greedy','sorting'],['maximum_height contains 1–100,000 positive limits.','Assign every tower a distinct positive integer no greater than its corresponding limit.','Return the maximum total height, or -1 when no assignment exists.'],[([[2,3,4,3]],'Limits sorted descending accept heights 4,3,2,1 for total ten.'),([[15,10]],'The distinct maximum values 15 and 10 can both be used, totaling 25.')],[[a] for a in [[1],[1,1],[2,2,1],[3,3,3],[1,2,3],[5,5],[2,3,4,3],[10,1],[4,4,4,4],[2,100,100],[6,5,5,3],[3,1,4,1],[7,7,6,6,5],[100,99,1,2]]],TOWERS,[TOWERS.replace('ceiling-1','ceiling'),TOWERS.replace('sorted(maximum_height,reverse=True)','sorted(maximum_height)')],['Allows equal assigned heights.','Processes tight limits last and can waste large heights on constrained towers.'],towers_oracle,random_towers,lesson('For descending limits, the current tower should take the largest unused height below the previous choice.','Sort limits descending and greedily cap each assignment at previous height minus one.','If the cap becomes nonpositive return -1; otherwise accumulate it.','Lowering an earlier feasible choice cannot help later tighter choices, so taking each maximum is exchange-optimal.'),'O(n log n)','O(n)',5),
3302:entry('smallest_almost_equal_index_sequence',[('word1','str'),('word2','str')],'list[int]',['greedy','two pointers','strings'],['word2 is shorter than word1 and both contain lowercase letters.','Choose increasing indices spelling a length-len(word2) string that differs from word2 in at most one position.','Return the lexicographically smallest valid index list, or an empty list.'],[(['vbcca','abc'],'Indices 0,1,2 spell vbc, requiring only the first character change.'),(['bacdc','abc'],'Indices 1,2,4 are the earliest sequence needing at most one change.')],[[a,b] for a,b in [('ab','a'),('abc','ab'),('xyz','a'),('aaaaaa','aaabc'),('axbc','abc'),('abcx','abc'),('zabc','abc'),('abbc','abc'),('acbd','abd'),('banana','ana'),('aaaa','bbb'),('cabca','abc'),('xaybz','abc'),('abcdef','ace')]],SEQUENCE,[SEQUENCE.replace('suffix[i+1]<=wanted+1','True'),SEQUENCE.replace('changed|=char!=word2[wanted]','changed=False')],['Spends the one mismatch before checking whether the remaining suffix can match.','Resets the mismatch flag and may use multiple character changes.'],sequence_oracle,random_sequence,lesson('A mismatch is safe only when the remaining target suffix can still be matched exactly afterward.','Precompute from the right how much of word2 remains unmatched by every word1 suffix.','Scan indices left to right, taking an exact match or the earliest feasible one-time mismatch.','Every accepted index is the smallest that preserves completion, which inductively yields the lexicographically smallest sequence.'),'O(n+m)','O(n)',7),
3307:entry('kth_implicit_game_character',[('k','int'),('operations','list[int]')],'str',['recursion','bit manipulation','strings'],['operations contains up to 100 zero/one operations and the final implicit word has at least k characters.','Each operation appends either an unchanged copy or a copy with every letter shifted forward once modulo 26.','Return the one-indexed kth character without constructing the exponentially large word.'],[([5,[0,0,0]],'Every operation duplicates unchanged a characters, so position five is a.'),([10,[0,1,0,1]],'Tracing position ten through the appended halves accumulates one shift, producing b.')],[[k,o] for k,o in [(1,[0]),(2,[0]),(2,[1]),(3,[1,0]),(4,[1,1]),(1,[1,1,1]),(8,[0,0,1]),(7,[1,0,1]),(16,[1,1,1,1]),(9,[0,1,0,1]),(5,[1,1,0]),(6,[0,1,1]),(12,[1,0,0,1]),(20,[1,1,0,0,1])]],GAME,[GAME.replace('shifts+=operations[used-1]','shifts+=1'),GAME.replace('k>length//2','k>=length//2')],['Shifts for every appended-half choice even when the operation is type zero.','Treats the last position of the first half as belonging to the appended half.'],game_oracle,random_game,lesson('Each operation doubles length; a position in the second half maps to the same offset in the first half.','Work backward through only the doublings needed to cover k and count type-one second-half choices.','If k exceeds half, subtract half and add that operation; finally map total shifts modulo 26 from a.','Backward mapping follows the unique ancestry of the requested character without materializing any other position.'),'O(min(operations,log k))','O(1)',8),
}

# Keep the negative control executable in the browser worker: it rejects full-word prefixes.
BATCH[3292]['wrong'][0]=COVER.replace('min(len(word),z[offset+i])','min(len(word)-1,z[offset+i])')
BATCH[3292]['wrong_reasons'][0]='Treats every complete dictionary word as one character too long to use.'
