"""Second reviewed group of workbook batch 114."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from .import_batch_055 import entry

MOD=1_000_000_007

def quad_o(a):
 nums=a[0];return sum(nums[i]+nums[j]+nums[k]==nums[l] for i,j,k,l in combinations(range(len(nums)),4))
def weak_o(a):
 p=a[0];return sum(any(c>a0 and d>d0 for c,d in p) for a0,d0 in p)
def rooms_o(a):
 nxt=a[0];room=day=0;vis=[0]*len(nxt)
 while not all(vis):
  vis[room]+=1
  if all(vis):return day
  room=nxt[room] if vis[room]%2 else (room+1)%len(nxt);day+=1
def prefix_o(a):
 word,ch=a;at=word.find(ch);return word if at<0 else word[:at+1][::-1]+word[at+1:]
def rectangles_o(a):
 counts=Counter(Fraction(w,h) for w,h in a[0]);return sum(v*(v-1)//2 for v in counts.values())

def rquad(r):return [[r.randint(1,20) for _ in range(r.randint(4,15))]]
def rweak(r):return [[[r.randint(1,30),r.randint(1,30)] for _ in range(r.randint(1,20))]]
def rrooms(r):
 n=r.randint(2,12);return [[r.randint(0,i) for i in range(n)]]
def rprefix(r):
 w=''.join(r.choice('abcde') for _ in range(r.randint(1,30)));return [w,r.choice(w)]
def rrect(r):return [[[r.randint(1,30),r.randint(1,30)] for _ in range(r.randint(1,25))]]

QUAD='''\
def count_special_quadruplets(nums):
    from collections import Counter
    answer=0
    right=Counter()
    for b in range(len(nums)-3,0,-1):
        for d in range(b+2,len(nums)):
            right[nums[d]-nums[b+1]]+=1
        for a in range(b):
            answer+=right[nums[a]+nums[b]]
    return answer
'''
WEAK='''\
def number_of_weak_characters(properties):
    properties.sort(key=lambda item:(-item[0],item[1]))
    strongest_defense=-1
    answer=0
    for attack,defense in properties:
        if defense<strongest_defense:
            answer+=1
        strongest_defense=max(strongest_defense,defense)
    return answer
'''
ROOMS='''\
def first_day_in_all_rooms(next_visit):
    mod=1_000_000_007
    first=[0]*len(next_visit)
    for room in range(1,len(next_visit)):
        first[room]=(2*first[room-1]-first[next_visit[room-1]]+2)%mod
    return first[-1]
'''
PREFIX='''\
def reverse_prefix_through_character(word,ch):
    position=word.find(ch)
    if position<0:return word
    return word[:position+1][::-1]+word[position+1:]
'''
RECT='''\
def interchangeable_rectangle_pairs(rectangles):
    from math import gcd
    counts={}
    answer=0
    for width,height in rectangles:
        divisor=gcd(width,height)
        ratio=(width//divisor,height//divisor)
        answer+=counts.get(ratio,0)
        counts[ratio]=counts.get(ratio,0)+1
    return answer
'''
def L(*x):return list(x)

BATCH={
1995:entry('count_special_quadruplets',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['nums has 4 through 50 positive integers, each at most 100.','Count index tuples a<b<c<d for which nums[a]+nums[b]+nums[c]=nums[d].','Different index tuples count separately.'],[([[1,2,3,6]],'The four indices satisfy one plus two plus three equals six, so one tuple counts.'),([[3,3,6,4,5]],'No increasing four-index tuple satisfies the equation.')],[[x] for x in [[1,1,1,3],[1,2,3,6],[3,3,6,4,5],[1,1,1,1],[2,2,2,6],[1,2,1,4,4],[5,1,2,3,6],[10,20,30,60],[1,3,2,6,7],[4,4,4,4,12],[1,2,3,4,5,6],[7,1,1,1,10],[2,3,5,10,20],[1,5,1,5,7]]],QUAD,[QUAD.replace('range(b)','range(b+1)'),QUAD.replace('nums[d]-nums[b+1]','nums[d]+nums[b+1]')],['Allows the same index to serve as both a and b.','Stores a sum instead of the required d-minus-c difference.'],quad_o,rquad,L('Rearrange the equation as nums[a]+nums[b]=nums[d]-nums[c].','Sweep b backward while counting right-side differences for valid c,d pairs.','Add each new d-minus-c to a counter, then query it for every a<b.','At each b the counter contains exactly pairs b<c<d, so matching left sums enumerates every valid ordered tuple once.'),'O(n^2)','O(value range)',5),
1996:entry('number_of_weak_characters',[('properties','list[list[int]]')],'int',['sorting','greedy','arrays'],['properties contains 1 through 100000 distinct [attack,defense] pairs.','A character is weak only if another character has both strictly greater attack and strictly greater defense.','Return the number of weak characters.'],[([[[5,5],[6,3],[3,6]]],'No character is strictly dominated in both attributes.'),([[[2,2],[3,3]]],'The character two,two is dominated by three,three, so one is weak.')],[[p] for p in [[[1,1]],[[2,2],[3,3]],[[5,5],[6,3],[3,6]],[[1,5],[10,4],[4,3]],[[1,1],[1,2]],[[1,1],[2,1]],[[1,1],[2,2],[3,3]],[[3,1],[2,2],[1,3]],[[5,1],[5,5],[6,2]],[[1,10],[2,9],[3,8]],[[1,1],[4,4],[2,2],[3,1]],[[10,10],[1,1]],[[2,3],[3,2],[4,4]],[[7,5],[8,5],[9,6]]]],WEAK,[WEAK.replace('(-item[0],item[1])','(-item[0],-item[1])'),WEAK.replace('defense<strongest_defense','defense<=strongest_defense')],['Processes equal-attack defenses high-first and incorrectly lets them dominate each other.','Treats equal defense as strictly greater defense.'],weak_o,rweak,L('Equal attacks must never dominate each other.','Sort attack descending and defense ascending within equal attacks, then track the greatest defense already seen.','Count defense<max_seen while scanning (-attack,+defense).','Earlier attack groups are strictly stronger; ascending equal groups cannot contribute a larger earlier defense, enforcing both strict inequalities.'),'O(n log n)','O(n)',5),
1997:entry('first_day_in_all_rooms',[('next_visit','list[int]')],'int',['dynamic programming','modular arithmetic','arrays'],['next_visit has length 2 through 100000 and 0 <= next_visit[i] <= i.','After an odd-numbered visit to room i, go to next_visit[i]; after an even visit, go to (i+1) mod n.','Return the first day every room has been visited, modulo 1000000007.'],[([[0,0]],'The visits are room zero, room zero, then room one, so all rooms have been seen on day two.'),([[0,0,2]],'The recurrence gives first-visit days zero, two, and six.')],[[x] for x in [[0,0],[0,1],[0,0,2],[0,0,0],[0,1,2],[0,0,1],[0,1,1],[0,0,1,2],[0,1,0,2],[0,0,0,0],[0,1,2,3],[0,0,2,1],[0,1,1,3],[0,0,1,1,2],[0,1,0,3,2]]],ROOMS,[ROOMS.replace('+2)%mod','+1)%mod'),ROOMS.replace('first[next_visit[room-1]]','next_visit[room-1]')],['Counts only one of the two transitions needed before advancing to the next room.','Subtracts a room index instead of that room’s first-visit day.'],rooms_o,rrooms,L('Before first reaching room i, all earlier rooms follow a deterministic revisit cycle.','Let first[i] be its first day; derive first[i] from returning to next_visit[i-1] and then revisiting i-1 evenly.','first[i]=2*first[i-1]-first[next_visit[i-1]]+2 modulo M.','The interval from the earlier target’s first visit through room i-1’s first visit is traversed twice, with two transition days, yielding the recurrence.'),'O(n)','O(n)',6),
2000:entry('reverse_prefix_through_character',[('word','str'),('ch','str')],'str',['strings','two pointers'],['word has 1 through 250 lowercase letters and ch is one lowercase letter.','Reverse the prefix ending at the first occurrence of ch.','If ch does not occur, return word unchanged.'],[(['abcdefd','d'],'The first d is at index three; reversing abcd produces dcbaefd.'),(['xyxzxe','z'],'The first z ends prefix xyxz, which becomes zxyx.')],[[w,c] for w,c in [('a','a'),('a','z'),('ab','a'),('ab','b'),('abcdefd','d'),('xyxzxe','z'),('hello','l'),('aaaa','a'),('banana','n'),('python','p'),('python','n'),('reverse','v'),('testing','x'),('codepractice','c')]],PREFIX,[PREFIX.replace('word.find(ch)','word.rfind(ch)'),PREFIX.replace('position+1','position',1)],['Uses the final occurrence instead of the first occurrence.','Excludes ch itself from the reversed prefix.'],prefix_o,rprefix,L('Only the earliest matching position determines the operation.','Find that index and reverse the inclusive slice from zero through it.','i=word.find(ch); return word if i<0 else word[:i+1][::-1]+word[i+1:].','The two slices partition the word, and reversing exactly the inclusive prefix performs the specified single operation.'),'O(n)','O(n)',3),
2001:entry('interchangeable_rectangle_pairs',[('rectangles','list[list[int]]')],'int',['hash maps','math','counting'],['rectangles has 1 through 100000 positive width-height pairs, each coordinate at most 100000.','Two rectangles are interchangeable when width/height ratios are equal.','Return the number of unordered interchangeable pairs.'],[([[[4,8],[3,6],[10,20],[15,30]]],'All four ratios equal one half, producing six pairs.'),([[[4,5],[7,8]]],'The ratios differ, so there are no interchangeable pairs.')],[[x] for x in [[[1,1]],[[1,1],[1,1]],[[4,8],[3,6],[10,20],[15,30]],[[4,5],[7,8]],[[1,2],[2,4],[3,6]],[[2,1],[4,2],[2,2]],[[100000,99999],[20000,19999]],[[6,8],[3,4],[9,12]],[[1,3],[2,6],[4,12],[5,15]],[[10,20],[20,10]],[[7,7],[14,14],[21,21]],[[2,3],[4,5],[6,9]],[[5,10],[1,2],[10,5]],[[12,18],[2,3],[8,12]]]],RECT,[RECT.replace('width//divisor,height//divisor','width,height'),RECT.replace('answer+=counts.get(ratio,0)','answer+=1 if ratio in counts else 0')],['Uses raw dimensions as keys and misses scaled rectangles with equal ratios.','Counts only one match per ratio instead of all earlier matching rectangles.'],rectangles_o,rrect,L('Reduce each ratio to a canonical integer pair to avoid floating-point error.','Divide width and height by their greatest common divisor and count prior equal keys.','For each reduced ratio, add its existing frequency to the answer, then increment it.','Canonical reduction is equal exactly for equal rational ratios, and adding prior frequency counts every unordered pair once when its later rectangle arrives.'),'O(n log V)','O(n)',5)
}
