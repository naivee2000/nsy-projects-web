"""Specialized and Hard-focused third group of workbook batch 115."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import EXTRA_BOUNDARIES, entry

def crossword_o(a):
 board,word=a;rows=len(board);cols=len(board[0])
 for line in board+[[board[r][c] for r in range(rows)] for c in range(cols)]:
  for slot in ''.join(line).split('#'):
   if len(slot)==len(word) and any(all(x==' ' or x==y for x,y in zip(slot,candidate)) for candidate in (word,word[::-1])):return True
 return False
def score_o(a):
 s,answers=a;nums=tuple(map(int,s[::2]));ops=tuple(s[1::2])
 @lru_cache(None)
 def values(left,right):
  if right-left==1:return {nums[left]}
  out=set()
  for cut in range(left,right-1):
   for x in values(left,cut+1):
    for y in values(cut+1,right):
     z=x+y if ops[cut]=='+' else x*y
     if z<=1000:out.add(z)
  return out
 total=term=nums[0]
 if len(nums)>1:
  total=0;term=nums[0]
  for op,x in zip(ops,nums[1:]):
   if op=='*':term*=x
   else:total+=term;term=x
  total+=term
 possible=values(0,len(nums));return sum(5 if x==total else 2 if x in possible else 0 for x in answers)
def partitions_o(a):
 nums,k=a
 def count(values):
  total=sum(values);left=0;answer=0
  for x in values[:-1]:left+=x;answer+=left*2==total
  return answer
 return max([count(nums)]+[count(nums[:i]+[k]+nums[i+1:]) for i in range(len(nums))])
def stones_o(a):
 counts=tuple(Counter(x%3 for x in a[0])[i] for i in range(3))
 @lru_cache(None)
 def play(state,total,alice):
  if sum(state)==0:return False
  outcomes=[]
  for rem,count in enumerate(state):
   if not count:continue
   if (total+rem)%3==0:outcomes.append(not alice)
   else:
    nxt=list(state);nxt[rem]-=1;outcomes.append(play(tuple(nxt),(total+rem)%3,not alice))
  return any(outcomes) if alice else all(outcomes)
 return play(counts,0,True)
def subsequence_o(a):
 s,k,letter,repetition=a
 return min(''.join(s[i] for i in ids) for ids in combinations(range(len(s)),k) if sum(s[i]==letter for i in ids)>=repetition)
def rcross(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.choice(['#',' ','a','b']) for _ in range(cols)] for _ in range(rows)],''.join(r.choice('ab') for _ in range(r.randint(1,5)))]
def rscore(r):
 length=r.randint(1,6);s=str(r.randint(0,9))
 for _ in range(length-1):s+=r.choice('+*')+str(r.randint(0,5))
 return [s,[r.randint(0,100) for _ in range(r.randint(1,12))]]
def rpart(r):return [[r.randint(-10,10) for _ in range(r.randint(2,10))],r.randint(-10,10)]
def rstones(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
def rsub(r):
 n=r.randint(2,10);s=''.join(r.choice('abc') for _ in range(n));letter=r.choice(s);rep=r.randint(1,s.count(letter));k=r.randint(rep,n);return [s,k,letter,rep]

CROSS='''\
def can_place_word_in_crossword(board,word):
    rows,cols=len(board),len(board[0])
    def fits(row,col,dr,dc):
        before=(row-dr,col-dc);after=(row+dr*len(word),col+dc*len(word))
        if 0<=before[0]<rows and 0<=before[1]<cols and board[before[0]][before[1]]!='#':return False
        if 0<=after[0]<rows and 0<=after[1]<cols and board[after[0]][after[1]]!='#':return False
        for index,char in enumerate(word):
            r,c=row+dr*index,col+dc*index
            if not (0<=r<rows and 0<=c<cols) or board[r][c] not in (' ',char):return False
        return True
    return any(fits(r,c,dr,dc) for r in range(rows) for c in range(cols) for dr,dc in ((0,1),(0,-1),(1,0),(-1,0)))
'''
SCORE='''\
def score_student_answers(s,answers):
    from functools import lru_cache
    numbers=list(map(int,s[::2]));operators=s[1::2]
    total=term=numbers[0]
    total=0
    for operator,value in zip(operators,numbers[1:]):
        if operator=='*':term*=value
        else:total+=term;term=value
    correct=total+term
    @lru_cache(None)
    def possible(left,right):
        if left==right:return {numbers[left]}
        results=set()
        for cut in range(left,right):
            for a in possible(left,cut):
                for b in possible(cut+1,right):
                    value=a+b if operators[cut]=='+' else a*b
                    if value<=1000:results.add(value)
        return results
    plausible=possible(0,len(numbers)-1)
    return sum(5 if answer==correct else 2 if answer in plausible else 0 for answer in answers)
'''
PART='''\
def maximum_partition_ways(nums,k):
    total=sum(nums);prefix=0;right=Counter()
    for value in nums[:-1]:prefix+=value;right[2*prefix-total]+=1
    answer=right[0];left=Counter();prefix=0
    for index,value in enumerate(nums):
        delta=k-value
        answer=max(answer,left[delta]+right[-delta])
        prefix+=value
        if index<len(nums)-1:
            difference=2*prefix-total;right[difference]-=1;left[difference]+=1
    return answer
'''
STONES='''\
def alice_wins_stone_game_nine(stones):
    counts=[0,0,0]
    for value in stones:counts[value%3]+=1
    if counts[0]%2==0:return counts[1]>0 and counts[2]>0
    return abs(counts[1]-counts[2])>2
'''
SUB='''\
def smallest_required_letter_subsequence(s,k,letter,repetition):
    stack=[];letters_left=s.count(letter);needed=repetition
    for index,char in enumerate(s):
        while stack and stack[-1]>char and len(stack)-1+len(s)-index>=k and (stack[-1]!=letter or letters_left>needed):
            removed=stack.pop()
            if removed==letter:needed+=1
        if len(stack)<k:
            if char==letter:stack.append(char);needed-=1
            elif k-len(stack)>needed:stack.append(char)
        if char==letter:letters_left-=1
    return ''.join(stack)
'''
def L(*x):return list(x)
EXTRA_BOUNDARIES['can_place_word_in_crossword']=[[[[' ','a','b','c','#']],'abc']]
EXTRA_BOUNDARIES['score_student_answers']=[['1+3*8*5*8',[1000]]]
EXTRA_BOUNDARIES['alice_wins_stone_game_nine']=[[[4,4,2,2]]]
EXTRA_BOUNDARIES['alice_wins_stone_game_nine'].append([[3,1,1,1,2]])
BATCH={
2018:entry('can_place_word_in_crossword',[('board','list[list[str]]'),('word','str')],'bool',['matrices','simulation','strings'],['board is a nonempty matrix of lowercase letters, spaces, and # blocks.','The word may run horizontally or vertically in either direction; spaces accept any letter and existing letters must match.','The cells immediately before and after the placement direction must be outside the board or blocked.'],[([[['#',' ','#'],[' ',' ','#'],['#','c',' ']],'abc'],'Reading upward through the final column-compatible slot places abc.'),([[[' ','#','a'],[' ','#','b'],[' ','#','c']],'abc'],'The right column exactly matches abc vertically.')],[[b,w] for b,w in [([[' ']],'a'),([['a']],'a'),([['b']],'a'),([[' ',' ']],'a'),([['#',' ','#']],'a'),([['a','b','c']],'abc'),([['c','b','a']],'abc'),([['a',' ','#']],'ab'),([['a',' ','c']],'abc'),([['a'],['b'],['c']],'abc'),([['c'],['b'],['a']],'abc'),([['#','a','#'],['#','b','#']],'ab'),([[' ','#'],[' ','#']],'aa'),([['a','b',' ','#']],'abc')]],CROSS,[CROSS.replace("board[before[0]][before[1]]!='#'","False"),CROSS.replace("board[r][c] not in (' ',char)","board[r][c] != ' '")],['Ignores a nonblocked cell before the word and permits placement inside a longer slot.','Allows only blank cells and rejects matching prefilled letters.'],crossword_o,rcross,L('A legal placement is an exact bounded slot match in one of four directions.','Try every start and direction, checking the boundary cells and each character-compatible board cell.','Require before/after blocked or outside; require each cell blank or equal to its word character.','The four direction vectors cover both orientations and reversals, while the boundary and cell predicates are exactly the placement rules.'),'O(rows*cols*word length)','O(1)',5),
2019:entry('score_student_answers',[('s','str'),('answers','list[int]')],'int',['dynamic programming','parsing','intervals'],['s alternates single digits with + or * and has at most 31 characters; answers has at most 10000 entries.','Award five for the standard-precedence result, two for a result from some parenthesization with correct arithmetic, otherwise zero.','Only plausible intermediate results at most 1000 are retained.'],[(['7+3*1*2',[20,13,42]],'Twenty is a plausible left-to-right grouping for two points and thirteen is correct for five, totaling seven.'),(['3+5*2',[13,16]],'Thirteen is correct and sixteen is a valid alternative grouping, totaling seven.')],[[s,a] for s,a in [('1',[1,2]),('1+2',[3,2]),('2*3',[6,5]),('7+3*1*2',[20,13,42]),('3+5*2',[13,16]),('1+2*3',[7,9]),('2*3+4',[10,14]),('1+1+1',[3]),('2*2*2',[8]),('0+5*0',[0,5]),('9*9+1',[82,90]),('4+2*3+1',[11,25]),('2+3*4*2',[26,40]),('5*0+7',[7,35])]],SCORE,[SCORE.replace('correct=total+term','correct=eval(s)'),SCORE.replace('if value<=1000','if value<1000')],['Uses unrestricted evaluation as though it differed, but this mutation is caught by the validator contract.', 'Drops the valid plausible value exactly 1000.'],score_o,rscore,L('Correct grading needs both standard precedence and every result obtainable by changing only parenthesization.','Compute the correct total with multiplication runs; use interval DP sets for all binary splits.','possible(l,r) unions a op b for every cut and cached subinterval result; score answers by correct first, then membership.','Every full parenthesization has a unique final split, so interval DP enumerates all and only arithmetic-order mistakes; separate precedence evaluation identifies five-point answers.'),'O(numbers^3*result combinations)','O(numbers^2*1001)',8),
2025:entry('maximum_partition_ways',[('nums','list[int]'),('k','int')],'int',['prefix sums','hash maps','dynamic programming'],['nums has 2 through 100000 integers and k is an integer in the same bounded range.','A pivot splits before index p, 1<=p<n, and is valid when left and right sums match.','Change at most one nums element to k and maximize the number of valid pivots.'],[([[2,-1,2],3],'Changing the middle value to three enables one balanced pivot.'),([[0,0,0],1],'Making no change preserves both balanced pivots, which is optimal.')],[[x,k] for x,k in [([2,-1,2],3),([0,0,0],1),([1,2,3],3),([1,1],1),([1,2],2),([2,2,2,2],2),([1,-1,1,-1],0),([10,-10,10],0),([1,2,3,4],0),([-1,-1,-1],1),([5,5,5,5,5],0),([3,1,2,2],4),([0,1,0,1,0],1),([7,-3,2,-6,4],5)]],PART,[PART.replace('right[-delta]','right[delta]'),PART.replace('left[delta]','left[-delta]')],['Uses the right-side sign rule for both sides of the changed index.','Uses the left-side sign rule for both sides of the changed index.'],partitions_o,rpart,L('Represent each pivot by difference 2*prefix-total; changing a value shifts that difference with opposite signs depending on which side contains it.','Sweep the changed index with counters for pivots to its left and right.','For delta=k-nums[i], candidate=left[delta]+right[-delta]; then move the next pivot difference from right to left.','Left pivots place the changed element on their right and need old difference delta; right pivots place it on their left and need old difference -delta.'),'O(n)','O(n)',8),
2029:entry('alice_wins_stone_game_nine',[('stones','list[int]')],'bool',['game theory','counting','modular arithmetic'],['stones has 1 through 100000 positive values.','Players alternately remove a stone; the mover loses immediately when the running sum becomes divisible by three.','Bob wins if all stones are removed; return whether Alice wins under optimal play.'],[([[2,1]],'Alice can remove either residue and force Bob into the losing divisible-by-three move.'),([[2]],'Alice removes the only stone without reaching a divisible sum, so exhaustion awards Bob the win.')],[[x] for x in [[1],[2],[3],[2,1],[2],[1,1],[2,2],[3,3,1,2],[1,2,3],[1,1,1,2],[2,2,2,1],[3,1,1,2,2],[6,9,1,2],[1,4,7,2,5,8]]],STONES,[STONES.replace('counts[0]%2==0','counts[0]%2==1'),STONES.replace('>2','>=2')],['Reverses how residue-zero moves swap the effective player parity.','Allows a residue-count gap of exactly two, which optimal reply play can neutralize.'],stones_o,rstones,L('Only each stone’s residue modulo three matters.','Count residues zero, one, and two; residue-zero parity changes whose strategy applies, while residues one and two must be balanced differently.','If count0 even require both count1 and count2; if odd require abs(count1-count2)>2.','Alternating residues one and two avoids a zero sum; analyzing which side runs out, with zero moves swapping turns, yields these necessary and sufficient cases.'),'O(n)','O(1)',6),
2030:entry('smallest_required_letter_subsequence',[('s','str'),('k','int'),('letter','str'),('repetition','int')],'str',['monotonic stack','greedy','subsequences'],['s has 1 through 50000 lowercase letters; 1<=k<=len(s).','Return the lexicographically smallest length-k subsequence containing letter at least repetition times.','The input guarantees enough occurrences of letter.'],[(['leet',3,'e',1],'Among length-three subsequences containing e, eet is lexicographically smallest.'),(['leetcode',4,'e',2],'The smallest valid result is ecde while retaining two e characters.')],[[s,k,l,r] for s,k,l,r in [('leet',3,'e',1),('leetcode',4,'e',2),('aaabbb',3,'a',2),('abc',3,'b',1),('abc',1,'b',1),('bbbaa',3,'a',2),('cbaabc',3,'a',1),('aaaa',2,'a',2),('zzaz',2,'a',1),('bacbac',4,'b',2),('dcba',3,'a',1),('abacaba',5,'a',3),('ccbbbaa',4,'b',2),('xyzzzyx',4,'z',2)]],SUB,[SUB.replace('letters_left>needed','letters_left>=needed'),SUB.replace('k-len(stack)>needed','k-len(stack)>=needed')],['Pops a required letter when only exactly enough future copies remain.','Allows a nonrequired character to occupy the final slot reserved for a needed letter.'],subsequence_o,rsub,L('A monotonic stack gives lexical minimality, but capacity and required-letter reservations constrain pops and pushes.','Pop larger characters only when enough total positions remain and any popped required letter can be replaced later.','Track letters_left and needed; reserve needed of the remaining k-stack slots, and adjust needed when required letters enter or leave.','The stack exchange makes each prefix smallest among feasible completions; the two feasibility counts guarantee length and repetition can still be met.'),'O(n)','O(k)',8)
}

BATCH[2019]['wrong'][0] = SCORE.replace('correct=total+term', 'correct=total')
BATCH[2019]['wrong_reasons'][0] = 'Omits the final multiplication run when computing the standard-precedence answer.'
BATCH[2018]['boundaries'].append([[[' ', 'a', 'b', 'c', '#']], 'abc'])
BATCH[2019]['boundaries'].append(['1+3*8*5*8', [1000]])
