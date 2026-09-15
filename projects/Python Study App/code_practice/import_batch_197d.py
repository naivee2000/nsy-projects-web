"""Alternating extrema, knight parity, greedy digits, valid prefixes, and elevators."""
from .import_batch_055 import entry

def alternating_oracle(a):
    n,s,m=a;return s if n==1 else s+(n//2)*(m-1)+1
def random_alternating(r):return [r.randint(1,10**9),r.randint(1,10**9),r.randint(1,10**5)]
def knight_oracle(a):return sum(a[0])%2==sum(a[1])%2
def random_knight(r):return [[r.randrange(8),r.randrange(8)],[r.randrange(8),r.randrange(8)]]
def largest_oracle(a):
    n,s=a
    if s>9*n:return -1
    digits=[]
    for _ in range(n):digits.append(min(9,s));s-=digits[-1]
    return int(''.join(map(str,digits)))
def random_largest(r):return [r.randint(1,5),r.randint(0,100)]
def prefixes_oracle(a):return sum(abs(p.count('1')-p.count('0'))<=1 for p in (a[0][:i] for i in range(1,len(a[0])+1)))
def random_prefixes(r):return [''.join(r.choice('01') for _ in range(r.randint(1,100)))]
def elevator_oracle(a):
    _,requests=a;return abs(requests[0])+sum(abs(requests[i]-requests[i-1]) for i in range(1,len(requests)))
def random_elevator(r):
    n=r.randint(1,100);return [n,[r.randrange(n) for _ in range(r.randint(1,100))]]

ALTERNATING='''def maximum_alternating_sequence_value(n,s,m):
    if n==1:return s
    return s+(n//2)*(m-1)+1
'''
KNIGHT='''def knight_even_move_reachable(start,target):
    return sum(start)%2==sum(target)%2
'''
LARGEST='''def largest_integer_with_digit_sum(n,s):
    if s>9*n:return -1
    answer=0
    for _ in range(n):
        digit=min(9,s);answer=answer*10+digit;s-=digit
    return answer
'''
PREFIXES='''def count_rearrangeable_alternating_prefixes(s):
    balance=answer=0
    for char in s:
        balance+=1 if char=='1' else -1
        if abs(balance)<=1:answer+=1
    return answer
'''
ELEVATOR='''def elevator_request_time(n,requests):
    position=total=0
    for floor in requests:
        total+=abs(floor-position);position=floor
    return total
'''

BATCH={
3993:entry('maximum_alternating_sequence_value',[('n','int'),('s','int'),('m','int')],'int',['math','greedy'],['A valid length-n integer sequence starts at s and alternates strictly up/down or down/up.','Every adjacent absolute difference is at most m.','Return the largest value that can appear in any valid sequence.'],[([4,3,5],'The sequence 3, 8, 7, 12 is valid and reaches the maximum twelve.'),([2,4,3],'A single rise of three reaches seven.')],[[n,s,m] for n,s,m in [(1,1,1),(1,10,5),(2,4,3),(3,1,1),(4,3,5),(5,2,2),(6,10,4),(2,1,1),(10,5,3),(7,100,10),(3,9,2),(8,1,5),(99,7,1),(1000000000,1,100000)]],ALTERNATING,[ALTERNATING.replace('n//2','(n-1)//2'),ALTERNATING.replace('+1','-1')],['Uses too few upward peaks for even lengths.','Moves the first attainable peak in the wrong direction.'],alternating_oracle,random_alternating,['To grow successive peaks, alternate a rise of m with the smallest strict fall of one.','Each two steps can increase the peak by m-1.','Count complete two-step gains and handle the first rise.','The construction meets every bound and no alternating pair can gain more.'],'O(1)','O(1)',5),
3996:entry('knight_even_move_reachable',[('start','list[int]'),('target','list[int]')],'bool',['graphs','chessboard parity'],['start and target are cells on an 8 by 8 chessboard.','A knight changes square color on every move.','Return whether the target is reachable in an even number of moves.'],[([[1,1],[2,2]],'Both cells have even coordinate sum, and an even-length route exists.'),([[4,5],[6,6]],'The coordinate sums have opposite parity, requiring an odd number of moves.')],[[a,b] for a,b in [([0,0],[0,0]),([1,1],[2,2]),([4,5],[6,6]),([0,0],[1,2]),([7,7],[0,0]),([0,7],[7,0]),([3,3],[4,4]),([2,5],[6,1]),([1,0],[2,2]),([6,6],[7,4]),([2,2],[5,5]),([0,1],[7,6]),([4,4],[4,5]),([3,7],[5,6])]],KNIGHT,[KNIGHT.replace('==','!='),KNIGHT.replace('sum(target)%2','target[0]%2')],['Accepts opposite-colored rather than same-colored endpoints.','Ignores the target row when computing its square color.'],knight_oracle,random_knight,['Color a cell by the parity of row plus column.','Every knight move flips that color.','An even number of flips ends on the starting color.','Compare the two coordinate-sum parities.'],'O(1)','O(1)',3),
4000:entry('largest_integer_with_digit_sum',[('n','int'),('s','int')],'int',['greedy','digits'],['Construct the largest nonnegative integer with at most n decimal digits and digit sum s.','Return -1 if s exceeds the capacity of n digits.','Return zero when s is zero.'],[([2,9],'Putting nine first and zero second produces the largest value 90.'),([2,19],'Two digits can sum to at most eighteen, so no answer exists.')],[[n,s] for n,s in [(1,0),(1,1),(1,9),(1,10),(2,9),(2,18),(2,19),(3,1),(3,10),(3,27),(4,20),(5,0),(5,45),(5,46),(4,7)]],LARGEST,[LARGEST.replace('min(9,s)','min(8,s)'),LARGEST.replace('s>9*n','s>=9*n')],['Artificially caps every digit at eight.','Rejects the valid all-nine boundary case.'],largest_oracle,random_largest,['First reject sums larger than nine times n.','To maximize place value, put as much sum as possible into each earliest digit.','Repeatedly take min(9, remaining sum).','Greedy placement dominates any arrangement that moves value to a later place.'],'O(n)','O(1)',3),
4006:entry('count_rearrangeable_alternating_prefixes',[('s','str')],'int',['strings','counting','prefixes'],['A prefix is valid when its characters can be rearranged into a binary alternating string.','That is possible exactly when its zero and one counts differ by at most one.','Return the number of nonempty valid prefixes.'],[(['00101'],'Prefixes of lengths one, three, and five have balanced-enough counts, giving three.'),(['101'],'Every prefix has zero/one counts differing by at most one.')],[[s] for s in ['0','1','00','01','10','11','00101','101','0101','0001','1110','0011','1100','010101','000111']],PREFIXES,[PREFIXES.replace('<=1','==0'),PREFIXES.replace('if abs(balance)<=1','if balance>=0')],['Counts only perfectly balanced even-length prefixes.','Incorrectly treats every nonnegative balance as rearrangeable.'],prefixes_oracle,random_prefixes,['Maintain ones minus zeros for the growing prefix.','A rearranged alternating string exists exactly when the absolute balance is at most one.','Update once per character and count qualifying states.','Only counts matter because rearrangement can place the majority symbol at both ends when needed.'],'O(n)','O(1)',3),
4020:entry('elevator_request_time',[('n','int'),('requests','list[int]')],'int',['arrays','simulation'],['Floors are numbered zero through n-1 and the elevator starts at zero.','Serve requests in their listed order at one second per floor moved.','Return total travel time; repeated current-floor requests cost zero.'],[([5,[2,1,4,3]],'The moves cost two, one, three, and one seconds, totaling seven.'),([3,[2,0,0]],'Travel to two and back to zero costs four; the repeated zero costs nothing.')],[[n,q] for n,q in [(1,[0]),(2,[1]),(5,[2,1,4,3]),(3,[2,0,0]),(5,[0]),(10,[9,0]),(4,[1,1,1]),(6,[5,4,3,2,1,0]),(3,[0,2,0,2]),(8,[3,7,1]),(2,[0,1]),(100,[99]),(5,[4,4,0]),(7,[2,6,2])]],ELEVATOR,[ELEVATOR.replace('position=total=0','position=requests[0];total=0'),ELEVATOR.replace('abs(floor-position)','floor-position')],['Starts at the first request and omits the initial trip from floor zero.','Uses signed displacement and lets downward travel cancel time.'],elevator_oracle,random_elevator,['Track the current floor, initially zero.','Each request costs the absolute difference from the current floor.','Add the distance and update the current floor.','Sequential simulation counts every traveled floor exactly once.'],'O(n)','O(1)',3),
}
