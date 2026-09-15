"""Vowel transitions, queen rays, constrained dice, equal frequencies, and meetings."""
from collections import Counter
from itertools import product
from .import_batch_055 import entry

def vowels_o(a):
    n=a[0];letters='aeiou';allowed={'a':'e','e':'ai','i':'aeou','o':'iu','u':'a'}
    if n<=7:return sum(all(word[i+1] in allowed[word[i]] for i in range(n-1)) for word in product(letters,repeat=n))%(10**9+7)
    endings={letter:1 for letter in letters}
    for _ in range(n-1):endings={letter:sum(count for previous,count in endings.items() if letter in allowed[previous])%(10**9+7) for letter in letters}
    return sum(endings.values())%(10**9+7)
def rvowels(r):return [r.randint(1,5)]

def queens_o(a):
    queens,king=a;occupied={tuple(q) for q in queens};answer=[]
    for dr,dc in product((-1,0,1),repeat=2):
        if dr==dc==0:continue
        r,c=king
        while 0<=r+dr<8 and 0<=c+dc<8:
            r+=dr;c+=dc
            if (r,c) in occupied:answer.append([r,c]);break
    return answer
def rqueens(r):
    king=[r.randrange(8),r.randrange(8)];cells=[[i,j] for i in range(8) for j in range(8) if [i,j]!=king];r.shuffle(cells);return [cells[:r.randint(1,20)],king]

def dice_o(a):
    n,limits=a;answer=0
    for rolls in product(range(6),repeat=n):
        start=0;valid=True
        while start<n:
            end=start+1
            while end<n and rolls[end]==rolls[start]:end+=1
            if end-start>limits[rolls[start]]:valid=False;break
            start=end
        answer+=valid
    return answer%(10**9+7)
def rdice(r):return [r.randint(1,5),[r.randint(1,4) for _ in range(6)]]

def frequency_o(a):
    nums=a[0];best=0
    for length in range(1,len(nums)+1):
        prefix=nums[:length]
        for removed in range(length):
            counts=Counter(prefix[:removed]+prefix[removed+1:])
            if len(set(counts.values()))<=1:best=length;break
    return best
def rfrequency(r):return [[r.randint(1,8) for _ in range(r.randint(1,30))]]

def meeting_o(a):
    first,second,duration=a;answer=None
    for x in first:
        for y in second:
            start=max(x[0],y[0]);end=min(x[1],y[1])
            if end-start>=duration and (answer is None or start<answer):answer=start
    return [] if answer is None else [answer,answer+duration]
def rmeeting(r):
    def slots():
        points=sorted(r.sample(range(0,80),r.randint(2,10)));return [[points[i],points[i+1]] for i in range(0,len(points)-1,2)]
    return [slots(),slots(),r.randint(1,12)]

VOWELS='''def count_vowel_permutations(n):
    mod=10**9+7;a=e=i=o=u=1
    for _ in range(n-1):a,e,i,o,u=(e+i+u)%mod,(a+i)%mod,(e+o)%mod,i%mod,(i+o)%mod
    return (a+e+i+o+u)%mod
'''
QUEENS='''def queens_attacking_king(queens,king):
    occupied={tuple(queen) for queen in queens};answer=[]
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==dc==0:continue
            row,column=king
            while 0<=row+dr<8 and 0<=column+dc<8:
                row+=dr;column+=dc
                if (row,column) in occupied:answer.append([row,column]);break
    return answer
'''
DICE='''def dice_sequence_count(n,rollMax):
    mod=10**9+7;states={(face,1):1 for face in range(6)}
    for _ in range(1,n):
        next_states={}
        for (face,run),count in states.items():
            for nxt in range(6):
                length=run+1 if nxt==face else 1
                if length<=rollMax[nxt]:next_states[nxt,length]=(next_states.get((nxt,length),0)+count)%mod
        states=next_states
    return sum(states.values())%mod
'''
FREQUENCY='''def maximum_equal_frequency_prefix(nums):
    counts=Counter();frequencies=Counter();maximum=answer=0
    for index,value in enumerate(nums,1):
        old=counts[value]
        if old:frequencies[old]-=1
        counts[value]+=1;frequencies[old+1]+=1;maximum=max(maximum,old+1)
        if maximum==1 or maximum*frequencies[maximum]+1==index or (maximum-1)*(frequencies[maximum-1]+1)+1==index:answer=index
    return answer
'''
MEETING='''def earliest_meeting_slot(slots1,slots2,duration):
    slots1=sorted(slots1);slots2=sorted(slots2);i=j=0
    while i<len(slots1) and j<len(slots2):
        start=max(slots1[i][0],slots2[j][0]);end=min(slots1[i][1],slots2[j][1])
        if end-start>=duration:return [start,start+duration]
        if slots1[i][1]<slots2[j][1]:i+=1
        else:j+=1
    return []
'''

BATCH={
1220:entry('count_vowel_permutations',[('n','int')],'int',['dynamic programming','strings'],['Build strings of length n from lowercase vowels.','After a: only e; after e: a or i; after i: any vowel except i; after o: i or u; after u: only a.','Return the count modulo 1000000007.'],[([1],'Every one-letter vowel string is valid, giving five.'),([2],'Applying the transition rules gives ten valid strings.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,12,15,20,25]],VOWELS,[VOWELS.replace('(e+i+u)','(e+i)'),VOWELS.replace('(a+i)','a')],['Omits transitions into a from u.','Omits transitions into e from i.'],vowels_o,rvowels,['Track how many valid prefixes end in each vowel.','Rewrite the forward rules as predecessor sums for the next five ending counts.','Repeat n-1 transitions and sum all endings.','Every valid string has exactly one prior prefix and final vowel, so the transition partitions the count.'],'O(n)','O(1)',8),
1222:entry('queens_attacking_king',[('queens','list[list[int]]'),('king','list[int]')],'list[list[int]]',['matrices','simulation'],['All pieces occupy distinct squares on an eight-by-eight board.','A queen attacks along a row, column, or diagonal unless another queen blocks it.','Return the nearest attacking queen in each direction; output order does not matter.'],[([[[0,1],[1,0],[4,0],[0,4],[3,3],[2,4]],[0,0]],'The nearest visible queens are at zero-one, one-zero, and three-three.'),([[[5,6],[7,7],[2,1],[0,3],[1,2],[6,3],[5,1],[3,4],[0,4],[2,2],[1,1],[6,4],[3,2],[2,3],[4,0],[6,2],[3,1],[4,5],[5,0],[4,1],[5,2],[0,2],[6,5],[4,3],[7,5],[2,0],[2,5],[7,4],[3,3],[7,3]],[3,4]],'Only the first queen encountered along each of the eight rays can attack.')],[[q,k] for q,k in [([[0,1]],[0,0]),([[1,1]],[0,0]),([[2,1]],[0,0]),([[0,1],[0,2]],[0,0]),([[7,7]],[0,0]),([[0,0]],[7,7]),([[3,0],[3,7]],[3,3]),([[0,3],[7,3]],[3,3]),([[0,0],[0,7],[7,0],[7,7]],[3,3]),([[2,2],[4,4]],[3,3]),([[1,3],[5,3],[3,1],[3,5]],[3,3]),([[0,1],[1,0],[3,3]],[0,0]),([[6,1],[5,2],[4,3]],[7,0]),([[1,6],[2,5],[3,4]],[0,7])]],QUEENS,[QUEENS.replace('break','continue'),QUEENS.replace('(-1,0,1)','(-1,0)',1)],['Looks through nearer queens and returns multiple queens from one direction.','Never scans positive row directions.'],queens_o,rqueens,['Treat the king as the origin of eight direction vectors.','Walk each ray outward until leaving the board or meeting its first queen.','Record that queen and stop the ray.','A farther queen is blocked by the first occupied square, so the eight scans return exactly all attackers.'],'O(queens+board width)','O(queens)',5),
1223:entry('dice_sequence_count',[('n','int'),('rollMax','list[int]')],'int',['dynamic programming'],['Count length-n sequences of six die faces.','Face i may appear consecutively at most rollMax[i] times.','Return the count modulo 1000000007.'],[([2,[1,1,2,2,2,3]],'Of thirty-six pairs, only repeated faces one and two are forbidden, leaving thirty-four.'),([2,[1,1,1,1,1,1]],'Only pairs with different faces are legal, giving thirty.')],[[n,m] for n,m in [(1,[1,1,1,1,1,1]),(2,[1,1,2,2,2,3]),(2,[1,1,1,1,1,1]),(3,[1,1,1,2,2,3]),(3,[2,2,2,2,2,2]),(4,[1,2,3,4,5,6]),(5,[1,1,1,1,1,1]),(2,[2,2,2,2,2,2]),(3,[3,3,3,3,3,3]),(4,[2,2,2,2,2,2]),(5,[1,2,1,2,1,2]),(6,[2,3,2,3,2,3]),(3,[1,3,1,3,1,3]),(4,[4,1,4,1,4,1])]],DICE,[DICE.replace('length<=rollMax[nxt]','length<rollMax[nxt]'),DICE.replace('if nxt==face','if nxt!=face')],['Rejects runs whose length exactly equals the allowed maximum.','Extends the run length when the face changes instead of when it repeats.'],dice_o,rdice,['Track the final face and its current run length.','Append each possible next face, resetting the run on a change and extending it on a repeat.','Keep only states within that face’s limit.','Face and run length contain all history relevant to the next legality decision.'],'O(n*36*max roll)','O(6*max roll)',8),
1224:entry('maximum_equal_frequency_prefix',[('nums','list[int]')],'int',['hash maps','frequency counting'],['Choose the longest prefix from which deleting exactly one element leaves all remaining value frequencies equal.','The remaining prefix may be empty.','Return that maximum prefix length.'],[([[2,2,1,1,5,3,3,5]],'Deleting one five from the length-seven prefix leaves frequencies two,two,two.'),([[1,1,1,2,2,2]],'Deleting one element from the length-five prefix leaves counts three and one, but the full prefix can delete one to leave counts two and three unequal; the answer is five.')],[[x] for x in [[1],[1,1],[1,2],[2,2,1,1,5,3,3,5],[1,1,1,2,2,2],[1,2,3,4],[1,1,2,2],[1,1,1,2],[1,2,2,3,3,3],[5,5,5,5],[1,2,1,2,3],[4,4,3,3,2,2,1],[1,1,2,2,3,3,3],[7,8,7,8,9,9,9,10]]],FREQUENCY,[FREQUENCY.replace('maximum==1','maximum==0'),FREQUENCY.replace('+1==index','==index')],['Fails the case where every value currently appears once.','Omits the single exceptional occurrence in a valid frequency pattern.'],frequency_o,rfrequency,['Maintain value counts and how many values have each count.','A prefix is valid when all counts are one, one value occurs once, or one value has frequency exactly one above all others.','Test those arithmetic identities after each insertion.','These are the only ways one deletion can make every positive frequency equal.'],'O(n)','O(distinct values)',8),
1229:entry('earliest_meeting_slot',[('slots1','list[list[int]]'),('slots2','list[list[int]]'),('duration','int')],'list[int]',['two pointers','intervals'],['Each person’s availability intervals are pairwise disjoint and have positive length.','Find the earliest overlap lasting at least duration.','Return its start and start plus duration, or an empty list.'],[([[[10,50],[60,120],[140,210]],[[0,15],[60,70]],8],'The earliest qualifying overlap begins at sixty and lasts at least eight.'),([[[10,50]],[[60,120]],12],'The availability sets never overlap.')],[[a,b,d] for a,b,d in [([[10,50],[60,120],[140,210]],[[0,15],[60,70]],8),([[10,50]],[[60,120]],12),([[0,10]],[[5,15]],5),([[0,10]],[[10,20]],1),([[1,100]],[[2,3]],1),([[5,10],[20,30]],[[0,6],[25,40]],4),([[0,5]],[[0,5]],5),([[0,5]],[[0,5]],6),([[10,20],[30,40]],[[15,35]],5),([[1,2],[3,9]],[[0,4]],1),([[0,100]],[[20,30],[40,50]],8),([[5,15]],[[0,10]],5),([[0,2],[4,8]],[[1,5],[7,9]],1),([[100,200]],[[150,180]],20)]],MEETING,[MEETING.replace('>=duration','>duration'),MEETING.replace('start=max','start=min')],['Rejects an overlap whose length equals the requested duration.','Uses the earlier interval start instead of the overlap start.'],meeting_o,rmeeting,['Sort both interval lists and compare their current intervals.','Their overlap begins at the later start and ends at the earlier end.','Return when it fits; otherwise advance the interval that ends first.','That interval cannot overlap any later counterpart earlier, so discarding it preserves the earliest possible answer.'],'O(a log a+b log b)','O(a+b)',5),
}
BATCH[1222]['comparator']='unordered'
