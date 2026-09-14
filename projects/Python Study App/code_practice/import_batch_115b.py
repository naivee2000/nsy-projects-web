"""Second reviewed group of workbook batch 115."""
from functools import lru_cache
from .import_batch_055 import entry

def bright_o(a):
 lights=a[0];left=min(x-r for x,r in lights);right=max(x+r for x,r in lights)
 scores=[(sum(x-r<=p<=x+r for x,r in lights),p) for p in range(left,right+1)]
 best=max(score for score,_ in scores);return min(p for score,p in scores if score==best)
def matrix_o(a):
 original,m,n=a;return [original[i*n:(i+1)*n] for i in range(m)] if len(original)==m*n else []
def concat_o(a):
 nums,target=a;return sum(i!=j and nums[i]+nums[j]==target for i in range(len(nums)) for j in range(len(nums)))
def confusion_o(a):
 s,k=a;best=0
 for i in range(len(s)):
  for j in range(i,len(s)):
   part=s[i:j+1]
   if min(part.count('T'),part.count('F'))<=k:best=max(best,len(part))
 return best
def moves_o(a):
 s=a[0]
 @lru_cache(None)
 def solve(text):
  if 'X' not in text:return 0
  first=text.index('X');best=10**6
  for start in range(max(0,first-2),min(first,len(text)-3)+1):
   changed=text[:start]+'OOO'+text[start+3:];best=min(best,1+solve(changed))
  return best
 return solve(s)
def rbright(r):return [[[r.randint(-20,20),r.randint(0,8)] for _ in range(r.randint(1,15))]]
def rmatrix(r):
 length=r.randint(0,30);original=[r.randint(-20,20) for _ in range(length)];m=r.randint(1,8);n=r.randint(1,8);return [original,m,n]
def rconcat(r):
 nums=[''.join(r.choice('0123') for _ in range(r.randint(1,4))) for _ in range(r.randint(1,15))];return [nums,''.join(r.choice('0123') for _ in range(r.randint(1,7)))]
def rconfusion(r):return [''.join(r.choice('TF') for _ in range(r.randint(1,30))),r.randint(0,8)]
def rmoves(r):return [''.join(r.choice('XO') for _ in range(r.randint(3,14)))]

BRIGHT='''\
def brightest_street_position(lights):
    events={}
    for position,radius in lights:
        events[position-radius]=events.get(position-radius,0)+1
        events[position+radius+1]=events.get(position+radius+1,0)-1
    brightness=best=-1;answer=0
    for position in sorted(events):
        brightness+=events[position]
        if brightness>best:best=brightness;answer=position
    return answer
'''
MATRIX='''\
def construct_2d_array(original,m,n):
    if len(original)!=m*n:return []
    return [original[row*n:(row+1)*n] for row in range(m)]
'''
CONCAT='''\
def count_concatenation_pairs(nums,target):
    frequencies={};answer=0
    for value in nums:
        if target.startswith(value):answer+=frequencies.get(target[len(value):],0)
        if target.endswith(value):answer+=frequencies.get(target[:-len(value)] if value else target,0)
        frequencies[value]=frequencies.get(value,0)+1
    return answer
'''
CONFUSION='''\
def maximum_exam_confusion(answer_key,k):
    def longest(target):
        left=changes=best=0
        for right,char in enumerate(answer_key):
            changes+=char!=target
            while changes>k:
                changes-=answer_key[left]!=target;left+=1
            best=max(best,right-left+1)
        return best
    return max(longest('T'),longest('F'))
'''
MOVES='''\
def minimum_moves_to_remove_x(s):
    moves=index=0
    while index<len(s):
        if s[index]=='X':moves+=1;index+=3
        else:index+=1
    return moves
'''
def L(*x):return list(x)
BATCH={
2021:entry('brightest_street_position',[('lights','list[list[int]]')],'int',['sweep line','prefix sums','sorting'],['lights has 1 through 100000 [position,radius] pairs with integer coordinates.','A lamp illuminates every integer position in its inclusive interval [position-radius,position+radius].','Return the smallest position having maximum brightness.'],[([[[-3,2],[1,2],[3,3]]],'Brightness two first occurs at negative one, before the tied region beginning at zero.'),([[[1,0],[0,1]]],'Position one is illuminated by both lamps and is uniquely brightest.')],[[x] for x in [[[0,0]],[[1,0],[0,1]],[[-3,2],[1,2],[3,3]],[[0,1]],[[0,1],[2,1]],[[0,2],[0,2]],[[5,3],[-5,3]],[[1,1],[3,1],[5,1]],[[10,0],[10,5]],[[0,10],[5,0]],[[2,2],[4,2],[6,2]],[[100,1],[-100,1]],[[0,0],[1,0],[2,0]],[[3,5],[-2,1],[8,2]]]],BRIGHT,[BRIGHT.replace('position+radius+1','position+radius'),BRIGHT.replace('brightness>best','brightness>=best')],['Ends inclusive light intervals one position too early.','Overwrites ties and returns the largest brightest position rather than the smallest.'],bright_o,rbright,L('Inclusive integer intervals become prefix-sum events at left and right+1.','Sweep event coordinates in order while maintaining brightness; update the answer only on a strict improvement.','Add +1 at position-radius and -1 at position+radius+1; prefix-sum sorted events.','Brightness is constant between events, and the first coordinate of the first strictly best region is the smallest maximizer.'),'O(n log n)','O(n)',5),
2022:entry('construct_2d_array',[('original','list[int]'),('m','int'),('n','int')],'list[list[int]]',['arrays','matrices','simulation'],['m and n are positive and original has at most 50000 integers.','Fill an m-by-n matrix row by row without changing element order.','Return [] when len(original) is not m*n.'],[([[1,2,3,4],2,2],'Two rows of width two produce [[1,2],[3,4]].'),([[1,2,3],1,3],'One row contains the original sequence unchanged.')],[[a,m,n] for a,m,n in [([],1,1),([1],1,1),([1,2],1,2),([1,2],2,1),([1,2,3,4],2,2),([1,2,3],1,3),([1,2,3],3,1),([1,2,3],2,2),([1,2,3,4,5,6],2,3),([1,2,3,4,5,6],3,2),([0,0,0,0],4,1),([-1,2,-3,4],1,4),([1,2,3,4,5],1,5),([1,2,3,4,5],5,1)]],MATRIX,[MATRIX.replace('len(original)!=m*n','len(original)<m*n'),MATRIX.replace('row*n:(row+1)*n','row*m:(row+1)*m')],['Accepts oversized arrays and silently ignores extra values.','Uses the row count instead of the column count as slice width.'],matrix_o,rmatrix,L('A valid shape must contain exactly m*n cells.','After checking the size, take consecutive slices of width n.','Return [original[r*n:(r+1)*n] for r in range(m)].','The slices are disjoint, ordered, cover exactly m*n elements, and therefore implement row-major placement.'),'O(m*n)','O(m*n)',3),
2023:entry('count_concatenation_pairs',[('nums','list[str]'),('target','str')],'int',['strings','hash maps','counting'],['nums has 2 through 100 digit strings and target is a nonempty digit string.','Count ordered index pairs i!=j for which nums[i]+nums[j] equals target.','Equal strings at different indices remain distinct choices.'],[([['777','7','77','77'],'7777'],'The ordered compatible choices produce four index pairs.'),([['123','4','12','34'],'1234'],'The pairs 123+4 and 12+34 produce two.')],[[a,t] for a,t in [(['1','2'],'12'),(['1','2'],'21'),(['777','7','77','77'],'7777'),(['123','4','12','34'],'1234'),(['1','1'],'11'),(['0','0','00'],'00'),(['12','12'],'1212'),(['1','23','123'],'123'),(['9','99','999'],'999'),(['10','0','1'],'10'),(['3','33','333','3'],'333'),(['5','55'],'555'),(['01','1','0'],'011'),(['2','22','222'],'2222')]],CONCAT,[CONCAT.replace('target.startswith(value)','target.endswith(value)',1),CONCAT.replace('frequencies[value]=frequencies.get(value,0)+1','frequencies[value]=1')],['Uses a suffix test when deciding whether the current value can be the first half.','Discards duplicate frequencies and undercounts distinct index choices.'],concat_o,rconcat,L('For a current string, it may be either the first or second member of a pair with an earlier string.','Maintain frequencies of earlier strings and query the exact complementary prefix or suffix when target matches.','If target starts with x query remaining suffix; if target ends with x query remaining prefix; then record x.','Each ordered pair is counted when its later index arrives, in the orientation where that value appears; exact splitting guarantees concatenation equality.'),'O(total characters)','O(n)',5),
2024:entry('maximum_exam_confusion',[('answer_key','str'),('k','int')],'int',['strings','sliding windows','two pointers'],['answer_key has 1 through 50000 T/F characters and 0 <= k <= len(answer_key).','Change at most k characters to maximize a consecutive run of one answer.','Return the greatest achievable run length.'],[(['TTFF',2],'Changing both F answers makes all four positions equal.'),(['TFFT',1],'Changing either middle answer produces a run of three equal answers.')],[[s,k] for s,k in [('T',0),('F',1),('TTFF',2),('TFFT',1),('TTFTTFTT',1),('FFFF',0),('FFFF',4),('TFTFTF',1),('TFTFTF',2),('TTTFFF',1),('FTTTFF',2),('TF',0),('TF',1),('TTFFTT',2)]],CONFUSION,[CONFUSION.replace('changes>k','changes>=k'),CONFUSION.replace("max(longest('T'),longest('F'))","longest('T')")],['Shrinks when changes equals k and therefore allows only k-1 edits.','Optimizes only an all-T window and misses a longer all-F result.'],confusion_o,rconfusion,L('A target run is a window containing at most k occurrences of the opposite character.','Run the standard at-most-k sliding window once for target T and once for target F.','Expand right, count mismatches, shrink left while mismatches>k, and retain maximum width.','Every feasible window remains until a new character makes it infeasible; minimal shrinking preserves the widest feasible window ending at each right index.'),'O(n)','O(1)',5),
2027:entry('minimum_moves_to_remove_x',[('s','str')],'int',['strings','greedy'],['s has 3 through 1000 characters, each X or O.','One move selects any three consecutive positions and changes all of them to O.','Return the fewest moves needed to leave no X.'],[(['XXX'],'One move covers all three X characters.'),(['XXOX'],'A move starting at zero covers the first two X characters, and a second move covers the final X.')],[[s] for s in ['XXX','OOO','XXO','OXX','XOO','XXOX','XXXX','XXXXX','XXXXXX','OXOXOX','XOXOXO','OOXOOX','XOOXOOX','XXOOOXX']],MOVES,[MOVES.replace('index+=3','index+=2'),MOVES.replace("s[index]=='X'","s[index:index+3]=='XXX'")],['Advances only two positions and can count overlapping work unnecessarily.','Starts a move only for three consecutive X values, leaving isolated X values unchanged.'],moves_o,rmoves,L('The leftmost remaining X must be covered by some move, and starting that move as far left as possible covers the most future positions.','Scan left to right; on X count a move and skip its three covered positions, otherwise advance one.','If s[i]==X: moves++, i+=3; else i+=1.','Any solution must spend a move covering the current leftmost X; shifting that move to start at i cannot lose coverage of an earlier unresolved position and maximizes rightward coverage.'),'O(n)','O(1)',3)
}

BATCH[2022]['boundaries'].append([[1, 2, 3], 1, 2])
BATCH[2023]['boundaries'].append([['1', '1', '1'], '11'])
