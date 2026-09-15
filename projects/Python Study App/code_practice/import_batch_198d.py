"""Infinite digits, traffic lights, subsequence gaps, bishops, and decoded powers."""
from itertools import product
from .import_batch_055 import entry

def infinite_prefix(limit):
    text='123456789';block=1
    while len(text)<limit:
        values=range(10*block,10*block+10) if block%2==0 else range(10*block+9,10*block-1,-1)
        text+=''.join(map(str,values));block+=1
    return text
def kth_oracle(a):return int(infinite_prefix(a[0])[a[0]-1])
def random_kth(r):return [r.randint(1,5000)]
def lights_oracle(a):
    period,lights,arrivals=a
    return max((min(0 if t%period<green else period-t%period for green in lights) for t in arrivals),default=0)
def random_lights(r):
    p=r.randint(2,20);return [p,[r.randint(1,p) for _ in range(r.randint(1,6))],[r.randint(0,100) for _ in range(r.randint(1,20))]]
def gap_oracle(a):
    skill,station=a;choices=[]
    def walk(i,last,path):
        if i==len(skill):choices.append(path);return
        for j in range(last+1,len(station)):
            if station[j]==skill[i]:walk(i+1,j,path+[j])
    walk(0,-1,[])
    return max((max((p[i+1]-p[i] for i in range(len(p)-1)),default=0) for p in choices),default=0)
def random_gap(r):
    station=''.join(r.choice('abc') for _ in range(r.randint(1,10)));indices=sorted(r.sample(range(len(station)),r.randint(1,min(5,len(station)))))
    return [''.join(station[i] for i in indices),station]
def bishop_oracle(a):
    s,t=a
    if (sum(s)-sum(t))%2:return -1
    return 1 if abs(s[0]-t[0])==abs(s[1]-t[1]) else 2
def random_bishop(r):
    while True:
        s=[r.randint(1,8),r.randint(1,8)];t=[r.randint(1,8),r.randint(1,8)]
        if s!=t:return [s,t]
def decoded_oracle(a):
    total=0
    for encoded in a[0]:
        body,width=divmod(encoded,10);text=str(body);total+=pow(int(text[:width]),int(text[width:]),10**9+7)
    return total%(10**9+7)
def random_decoded(r):
    out=[]
    for _ in range(r.randint(1,8)):
        x=str(r.randint(1,99));y=str(r.randint(1,9));out.append(int(x+y)*10+len(x))
    return [out]

KTH='''def kth_digit_in_alternating_blocks(k):
    if k<=9:return k
    k-=9;digits=2;first_block=1
    while k>9*10**(digits-2)*10*digits:
        k-=9*10**(digits-2)*10*digits;digits+=1;first_block*=10
    block=first_block+(k-1)//(10*digits);position=(k-1)%(10*digits)
    offset=position//digits;number=10*block+(offset if block%2==0 else 9-offset)
    return int(str(number)[position%digits])
'''
LIGHTS='''def minimum_traffic_light_penalty(period,lights,arrival_times):
    longest=max(lights);answer=0
    for time in arrival_times:
        remainder=time%period
        if remainder>=longest:answer=max(answer,period-remainder)
    return answer
'''
GAP='''def maximum_station_assignment_gap(skill,station):
    n=len(skill);latest=[0]*n;j=len(station)-1
    for i in range(n-1,-1,-1):
        while station[j]!=skill[i]:j-=1
        latest[i]=j;j-=1
    answer=0;j=0
    for i in range(n-1):
        while station[j]!=skill[i]:j+=1
        answer=max(answer,latest[i+1]-j);j+=1
    return answer
'''
BISHOP='''def minimum_bishop_moves(source,target):
    if sum(source)%2!=sum(target)%2:return -1
    if abs(source[0]-target[0])==abs(source[1]-target[1]):return 1
    return 2
'''
DECODED='''def sum_decoded_powers(nums):
    MOD=10**9+7;answer=0
    for encoded in nums:
        body,width=divmod(encoded,10);text=str(body)
        answer=(answer+pow(int(text[:width]),int(text[width:]),MOD))%MOD
    return answer
'''

BATCH={
4022:entry('kth_digit_in_alternating_blocks',[('k','int')],'int',['math','binary search','strings'],['The infinite string begins with 1 through 9.','Then each block b contributes ten consecutive integers 10b..10b+9, ascending for even b and descending for odd b.','Return the one-indexed kth digit.'],[([4],'The fourth digit of the initial 123456789 prefix is four.'),([10],'Block one is descending, so the tenth digit is the first digit of nineteen: one.')],[[k] for k in [1,4,9,10,11,12,20,29,30,49,50,100,999,5000]],KTH,[KTH.replace('if k<=9:return k','if k<=9:return k-1'),KTH.replace('block%2==0','block%2==1')],['Treats the requested position as zero-indexed in the initial prefix.','Reverses which block parity is ascending.'],kth_oracle,random_kth,['Subtract complete groups sharing the same integer digit width.','Each block has ten integers and group sizes grow by powers of ten.','Locate the block, number offset, and digit offset with division and remainders.','Parity determines whether the number offset counts upward or downward.'],'O(log k)','O(1)',6),
4025:entry('minimum_traffic_light_penalty',[('period','int'),('lights','list[int]'),('arrivalTime','list[int]')],'int',['arrays','greedy'],['A light with green length g gives zero wait when arrival mod period < g, otherwise period-remainder.','Assign each car independently to one light.','Minimize the maximum waiting time across all cars.'],[([8,[2,3],[2,5,8,11]],'The longest green phase is three; waits are zero, three, zero, and five, so the maximum is five.'),([10,[10],[0,9,20]],'A full-period green phase gives every car zero wait.')],[[p,l,a] for p,l,a in [(8,[2,3],[2,5,8,11]),(10,[10],[0,9,20]),(5,[1],[0]),(5,[1],[4]),(6,[2,5],[1,4,5]),(7,[3],[3,6]),(4,[1,2],[2,3]),(10,[2,8],[7,8,9]),(3,[1],[1,2]),(9,[4,5],[0,4,5,8]),(8,[2,3],[8]),(2,[1],[1]),(12,[6],[5,6,11]),(20,[1,19],[18,19])]],LIGHTS.replace('arrival_times','arrivalTime'),[LIGHTS.replace('arrival_times','arrivalTime').replace('longest=max(lights)','longest=min(lights)'),LIGHTS.replace('arrival_times','arrivalTime').replace('remainder>=longest','remainder>longest')],['Uses the shortest green phase although every car may choose the best light.','Treats arrival exactly at green length as still green.'],lights_oracle,random_lights,['Only the longest green phase can weakly improve any car’s wait.','Reduce each arrival modulo period.','When the remainder is outside that phase, its wait is period-remainder.','Take the maximum of these individually minimized waits.'],'O(cars+lights)','O(1)',5),
4026:entry('maximum_station_assignment_gap',[('skill','str'),('station','str')],'int',['strings','two pointers','greedy'],['Assign each skill character to an equal station character at strictly increasing indices.','skill is guaranteed to be a subsequence of station.','Maximize the largest gap between consecutive assigned indices; return zero for one worker.'],[(['aa','aaaa'],'Assign the two a values to indices zero and three for gap three.'),(['abc','axbxc'],'The only broad assignment uses indices zero, two, and four, whose maximum gap is two.')],[[s,t] for s,t in [('a','a'),('aa','aaaa'),('abc','axbxc'),('ab','ab'),('ab','aab'),('ba','bxxa'),('aaa','aaaaa'),('ac','abcabc'),('cab','ccab'),('bb','abbbba'),('abc','abcabc'),('aba','aabbaa'),('xy','xzzzy'),('aaaa','aaaa')]],GAP,[GAP.replace('latest[i+1]-j','latest[i]-j'),GAP.replace('j=len(station)-1','j=len(station)-2')],['Compares the same worker’s earliest and latest positions instead of consecutive workers.','Starts the suffix scan before the final station and can miss the latest match.'],gap_oracle,random_gap,['For each skill position, compute its latest feasible station index by scanning backward.','Scan forward to obtain each current worker’s earliest feasible index.','Pair the earliest position for i with the latest feasible position for i+1.','Any optimal consecutive gap can move its left endpoint earlier and right endpoint later without invalidating surrounding assignments.'],'O(n+m)','O(n)',5),
4034:entry('minimum_bishop_moves',[('source','list[int]'),('target','list[int]')],'int',['chessboard','geometry'],['source and target are distinct cells on an 8 by 8 board.','A bishop moves any positive distance along a diagonal.','Return the minimum moves, or -1 when the target is unreachable.'],[([[8,1],[1,8]],'Both cells lie on the same diagonal, so one move suffices.'),([[1,1],[3,4]],'The squares have different colors, so no bishop route exists.')],[[s,t] for s,t in [([8,1],[1,8]),([1,1],[3,4]),([1,1],[2,2]),([1,1],[8,8]),([1,1],[1,3]),([4,2],[1,3]),([8,8],[1,1]),([2,3],[5,6]),([2,2],[7,4]),([3,5],[6,2]),([4,4],[8,2]),([7,1],[2,6]),([8,1],[8,3]),([5,5],[1,7])]],BISHOP,[BISHOP.replace('sum(source)%2!=sum(target)%2','sum(source)%2==sum(target)%2'),BISHOP.replace('return 1','return 2',1)],['Rejects same-colored reachable targets and accepts opposite colors.','Returns two moves even when source and target share a diagonal.'],bishop_oracle,random_bishop,['A bishop never changes square color, so opposite colors are unreachable.','On the same diagonal, absolute row and column differences match and one move suffices.','Any two same-colored cells not sharing a diagonal meet through an intermediate diagonal in two moves.','These mutually exclusive cases give the exact minimum.'],'O(1)','O(1)',3),
4039:entry('sum_decoded_powers',[('nums','list[int]')],'int',['math','strings','modular arithmetic'],['For encoded v, width=v mod 10 and body=v//10.','Split body’s decimal text after width digits into positive x and y, then decode as x^y.','Return the sum of decoded values modulo 1,000,000,007.'],[([[231]],'Body 23 split after one digit gives two to the third power, or eight.'),([[1121,341]],'The encodings represent one to the twelfth and three to the fourth, summing to 82.')],[[x] for x in [[231],[1121,341],[111],[221],[931],[1231],[991],[1232],[451],[231,231],[2121,3121,4121],[5671],[9991],[2301]]],DECODED,[DECODED.replace('body,width=divmod(encoded,10)','width,body=divmod(encoded,10)'),DECODED.replace('text[:width]','text[width:]',1)],['Swaps the body and width components.','Uses the suffix as x instead of the first width digits.'],decoded_oracle,random_decoded,['Use divmod by ten to separate body and width.','Convert the body to decimal text and split at width.','Apply modular exponentiation to x and y.','Accumulate every decoded power modulo the required constant.'],'O(total digits*log exponent)','O(total digits)',5),
}
