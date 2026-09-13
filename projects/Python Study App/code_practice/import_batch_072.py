"""Reviewed graph, dynamic-programming, greedy, and simulation imports."""
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations

from .import_batch_055 import entry


def inversions_oracle(args):
    nums=args[0];global_count=sum(nums[i]>nums[j] for i in range(len(nums)) for j in range(i+1,len(nums)))
    return global_count==sum(a>b for a,b in zip(nums,nums[1:]))

def transform_oracle(args):
    start,result=args
    if len(start)!=len(result):return False
    queue=deque([start]);seen={start}
    while queue:
        value=queue.popleft()
        if value==result:return True
        for index in range(len(value)-1):
            pair=value[index:index+2]
            if pair in ('XL','RX'):
                following=value[:index]+pair[::-1]+value[index+2:]
                if following not in seen:seen.add(following);queue.append(following)
    return False

def grammar_oracle(args):
    n,k=args;row='0'
    for _ in range(1,n):row=''.join('01' if char=='0' else '10' for char in row)
    return int(row[k-1])

def rabbits_oracle(args):
    counts=Counter(args[0]);return sum(((count+answer)//(answer+1))*(answer+1) for answer,count in counts.items())

def fraction_oracle(args):
    arr,k=args;pairs=sorted((Fraction(arr[i],arr[j]),[arr[i],arr[j]]) for i in range(len(arr)) for j in range(i+1,len(arr)))
    return pairs[k-1][1]

def flights_oracle(args):
    n,flights,src,dst,k=args;graph=[[] for _ in range(n)]
    for left,right,cost in flights:graph[left].append((right,cost))
    best=10**18
    def visit(node,edges,cost):
        nonlocal best
        if cost>=best:return
        if node==dst:best=cost;return
        if edges==k+1:return
        for following,price in graph[node]:visit(following,edges+1,cost+price)
    visit(src,0,0);return -1 if best==10**18 else best

def rotated_oracle(args):
    mapping={'0':'0','1':'1','2':'5','5':'2','6':'9','8':'8','9':'6'}
    return sum(all(char in mapping for char in str(value)) and ''.join(mapping[c] for c in str(value))!=str(value) for value in range(1,args[0]+1))

def escape_oracle(args):
    ghosts,target=args;player=abs(target[0])+abs(target[1])
    return all(abs(x-target[0])+abs(y-target[1])>player for x,y in ghosts)

def tiling_oracle(args):
    n=args[0];full=3
    states={0:1}
    for _ in range(n):
        following=Counter()
        shapes=(((0,0),(1,0)),((0,0),(0,1)),((1,0),(1,1)),
                ((0,0),(1,0),(0,1)),((0,0),(1,0),(1,1)),
                ((0,0),(0,1),(1,1)),((1,0),(0,1),(1,1)))
        def fill(mask,next_mask,ways):
            if mask==full:following[next_mask]+=ways;return
            row=0 if not mask&1 else 1
            for shape in shapes:
                if (row,0) not in shape:continue
                if any((column==0 and mask>>r&1) or (column==1 and next_mask>>r&1) for r,column in shape):continue
                new_mask=mask;new_next=next_mask
                for r,column in shape:
                    if column==0:new_mask|=1<<r
                    else:new_next|=1<<r
                fill(new_mask,new_next,ways)
        for mask,ways in states.items():fill(mask,0,ways)
        states=following
    return states.get(0,0)%(10**9+7)

def custom_oracle(args):
    order,text=args;rank={char:index for index,char in enumerate(order)}
    return ''.join(sorted(text,key=lambda char:rank.get(char,len(order))))

def subsequences_oracle(args):
    text,words=args
    def matches(word):
        iterator=iter(text);return all(any(char==candidate for candidate in iterator) for char in word)
    return sum(matches(word) for word in words)

def tictactoe_oracle(args):
    board=args[0];x=sum(row.count('X') for row in board);o=sum(row.count('O') for row in board)
    lines=list(board)+[''.join(board[r][c] for r in range(3)) for c in range(3)]+[''.join(board[i][i] for i in range(3)),''.join(board[i][2-i] for i in range(3))]
    xwin='XXX' in lines;owin='OOO' in lines
    return x in (o,o+1) and not (xwin and owin) and (not xwin or x==o+1) and (not owin or x==o)

def bounded_oracle(args):
    nums,left,right=args
    return sum(left<=max(nums[i:j])<=right for i in range(len(nums)) for j in range(i+1,len(nums)+1))

def rotate_oracle(args):
    first,goal=args
    return len(first)==len(goal) and any(first[index:]+first[:index]==goal for index in range(len(first) or 1))

def paths_oracle(args):
    graph=args[0];answer=[]
    def visit(node,path):
        if node==len(graph)-1:answer.append(path);return
        for following in graph[node]:visit(following,path+[following])
    visit(0,[0]);return answer

def champagne_oracle(args):
    poured,row,glass=args;current=[float(poured)]
    for _ in range(row):
        following=[0.0]*(len(current)+1)
        for index,value in enumerate(current):
            overflow=max(0.0,(value-1.0)/2);following[index]+=overflow;following[index+1]+=overflow
        current=following
    return min(1.0,current[glass])

def color_oracle(args):
    text=args[0];answer='#'
    for index in (1,3,5):
        value=int(text[index:index+2],16);candidate=min(range(0,256,17),key=lambda x:(abs(x-value),x));answer+=f'{candidate:02x}'
    return answer

def safe_oracle(args):
    graph=args[0];safe=[]
    for start in range(len(graph)):
        def cycle(node,path):
            if node in path:return True
            return any(cycle(next_node,path|{node}) for next_node in graph[node])
        if not cycle(start,set()):safe.append(start)
    return safe

MORSE=['.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..']
def morse_oracle(args):return len({''.join(MORSE[ord(char)-97] for char in word) for word in args[0]})

def lines_oracle(args):
    widths,text=args;lines=1;used=0
    for char in text:
        width=widths[ord(char)-97]
        if used+width>100:lines+=1;used=0
        used+=width
    return [lines,used]


def random_inversions(rng):
    nums=list(range(rng.randint(1,8)));rng.shuffle(nums);return [nums]
def random_transform(rng):
    start=''.join(rng.choice('LRX') for _ in range(rng.randint(1,7)));states={start}
    for _ in range(rng.randint(0,8)):
        moves=[value[:i]+value[i:i+2][::-1]+value[i+2:] for value in states for i in range(len(value)-1) if value[i:i+2] in ('XL','RX')]
        if moves:states.add(rng.choice(moves))
    result=rng.choice(list(states)) if rng.random()<.7 else ''.join(rng.choice('LRX') for _ in start)
    return [start,result]
def random_grammar(rng):
    n=rng.randint(1,10);return [n,rng.randint(1,2**(n-1))]
def random_rabbits(rng):return [[rng.randint(0,8) for _ in range(rng.randint(0,20))]]
def random_fraction(rng):
    primes=[1,2,3,5,7,11,13,17];arr=primes[:rng.randint(2,8)];return [arr,rng.randint(1,len(arr)*(len(arr)-1)//2)]
def random_flights(rng):
    n=rng.randint(2,7);flights=[[a,b,rng.randint(1,20)] for a in range(n) for b in range(n) if a!=b and rng.random()<.2]
    return [n,flights,rng.randrange(n),rng.randrange(n),rng.randint(0,n-1)]
def random_rotated(rng):return [rng.randint(1,1000)]
def random_escape(rng):return [[[rng.randint(-10,10),rng.randint(-10,10)] for _ in range(rng.randint(1,8))],[rng.randint(-10,10),rng.randint(-10,10)]]
def random_tiling(rng):return [rng.randint(1,10)]
def random_custom(rng):
    order=''.join(rng.sample('abcdef',rng.randint(1,6)));text=''.join(rng.choice('abcdefxyz') for _ in range(rng.randint(1,20)));return [order,text]
def random_subsequences(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,18))),[''.join(rng.choice('abcde') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,10))]]
def random_board(rng):return [[''.join(rng.choice('XO ') for _ in range(3)) for _ in range(3)]]
def random_bounded(rng):return [[rng.randint(0,10) for _ in range(rng.randint(1,12))],rng.randint(0,5),rng.randint(5,10)]
def random_rotate(rng):
    first=''.join(rng.choice('abcd') for _ in range(rng.randint(1,12)));cut=rng.randrange(len(first));goal=first[cut:]+first[:cut] if rng.random()<.6 else ''.join(rng.choice('abcd') for _ in first);return [first,goal]
def random_paths(rng):
    n=rng.randint(2,8);return [[[j for j in range(i+1,n) if rng.random()<.35] for i in range(n)]]
def random_champagne(rng):
    row=rng.randint(0,12);return [rng.randint(0,100),row,rng.randint(0,row)]
def random_color(rng):return ['#'+''.join(rng.choice('0123456789abcdef') for _ in range(6))]
def random_safe(rng):
    n=rng.randint(1,8);return [[[j for j in range(n) if j!=i and rng.random()<.18] for i in range(n)]]
def random_morse(rng):return [[''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,15))]]
def random_lines(rng):return [[rng.randint(2,10) for _ in range(26)],''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,80)))]


INVERSIONS='''\
def has_only_local_inversions(nums):
    suffix_min=nums[-1]
    for index in range(len(nums)-3,-1,-1):
        suffix_min=min(suffix_min,nums[index+2])
        if nums[index]>suffix_min:return False
    return True
'''
TRANSFORM='''\
def can_transform_lr(start, result):
    if start.replace('X','')!=result.replace('X',''):return False
    left=[(char,index) for index,char in enumerate(start) if char!='X']
    right=[(char,index) for index,char in enumerate(result) if char!='X']
    return all(not (char=='L' and a<b) and not (char=='R' and a>b) for (char,a),(_,b) in zip(left,right))
'''
GRAMMAR='''\
def kth_grammar_symbol(n, k):
    return (k-1).bit_count()%2
'''
RABBITS='''\
def minimum_rabbits(answers):
    from collections import Counter
    total=0
    for answer,count in Counter(answers).items():
        group=answer+1;total+=((count+group-1)//group)*group
    return total
'''
FRACTION='''\
def kth_smallest_fraction(arr, k):
    from heapq import heapify,heappop,heappush
    heap=[(arr[0]/arr[j],0,j) for j in range(1,len(arr))];heapify(heap)
    for _ in range(k-1):
        _,i,j=heappop(heap)
        if i+1<j:heappush(heap,(arr[i+1]/arr[j],i+1,j))
    _,i,j=heappop(heap);return [arr[i],arr[j]]
'''
FLIGHTS='''\
def cheapest_flight_with_stops(n, flights, src, dst, k):
    infinity=10**18;cost=[infinity]*n;cost[src]=0
    for _ in range(k+1):
        following=cost[:]
        for left,right,price in flights:
            if cost[left]!=infinity:following[right]=min(following[right],cost[left]+price)
        cost=following
    return -1 if cost[dst]==infinity else cost[dst]
'''
ROTATED='''\
def rotated_digit_count(n):
    valid=set('0125689');changed=set('2569');answer=0
    for value in range(1,n+1):
        digits=set(str(value));answer+=digits<=valid and bool(digits&changed)
    return answer
'''
ESCAPE='''\
def can_escape_ghosts(ghosts, target):
    distance=abs(target[0])+abs(target[1])
    return all(abs(x-target[0])+abs(y-target[1])>distance for x,y in ghosts)
'''
TILING='''\
def domino_tromino_tilings(n):
    mod=10**9+7
    if n<=2:return n
    first,second,third=1,1,2
    for _ in range(3,n+1):first,second,third=second,third,(2*third+first)%mod
    return third
'''
CUSTOM='''\
def custom_sort_text(order, s):
    from collections import Counter
    counts=Counter(s);answer=[]
    for char in order:answer.append(char*counts.pop(char,0))
    for char in s:
        if char in counts:answer.append(char);counts[char]-=1
        if counts.get(char)==0:counts.pop(char,None)
    return ''.join(answer)
'''
SUBSEQUENCES='''\
def matching_subsequence_count(s, words):
    waiting={char:[] for char in 'abcdefghijklmnopqrstuvwxyz'}
    for word in words:waiting[word[0]].append((word,0))
    answer=0
    for char in s:
        current=waiting[char];waiting[char]=[]
        for word,index in current:
            index+=1
            if index==len(word):answer+=1
            else:waiting[word[index]].append((word,index))
    return answer
'''
TICTACTOE='''\
def valid_tic_tac_toe(board):
    x=sum(row.count('X') for row in board);o=sum(row.count('O') for row in board)
    def wins(char):
        return any(all(board[r][c]==char for c in range(3)) for r in range(3)) or any(all(board[r][c]==char for r in range(3)) for c in range(3)) or all(board[i][i]==char for i in range(3)) or all(board[i][2-i]==char for i in range(3))
    return x in (o,o+1) and not (wins('X') and wins('O')) and (not wins('X') or x==o+1) and (not wins('O') or x==o)
'''
BOUNDED='''\
def bounded_max_subarray_count(nums, left, right):
    answer=0;last_too_large=-1;last_in_range=-1
    for index,value in enumerate(nums):
        if value>right:last_too_large=index
        if left<=value<=right:last_in_range=index
        answer+=max(0,last_in_range-last_too_large)
    return answer
'''
ROTATE='''\
def is_rotation(s, goal):
    return len(s)==len(goal) and goal in s+s
'''
PATHS='''\
def all_source_target_paths(graph):
    target=len(graph)-1;answer=[]
    def visit(node,path):
        if node==target:answer.append(path);return
        for following in graph[node]:visit(following,path+[following])
    visit(0,[0]);return answer
'''
CHAMPAGNE='''\
def champagne_amount(poured, query_row, query_glass):
    row=[float(poured)]
    for _ in range(query_row):
        following=[0.0]*(len(row)+1)
        for index,value in enumerate(row):
            overflow=max(0.0,(value-1)/2);following[index]+=overflow;following[index+1]+=overflow
        row=following
    return min(1.0,row[query_glass])
'''
COLOR='''\
def nearest_shorthand_color(color):
    answer='#'
    for index in (1,3,5):
        value=int(color[index:index+2],16);digit=max(0,min(15,(value+8)//17));answer+=format(digit,'x')*2
    return answer
'''
SAFE='''\
def eventual_safe_nodes(graph):
    state=[0]*len(graph)
    def safe(node):
        if state[node]:return state[node]==2
        state[node]=1
        if all(safe(following) for following in graph[node]):state[node]=2;return True
        return False
    return [node for node in range(len(graph)) if safe(node)]
'''
MORSE_CODE='''\
def unique_morse_count(words):
    codes=['.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..']
    return len({''.join(codes[ord(char)-97] for char in word) for word in words})
'''
LINES='''\
def writing_line_usage(widths, s):
    lines=1;used=0
    for char in s:
        width=widths[ord(char)-97]
        if used+width>100:lines+=1;used=0
        used+=width
    return [lines,used]
'''


def lesson(a,b,c,d):return [a,b,c,d],d

BATCH={
775:entry('has_only_local_inversions',[('nums','list[int]')],'bool',['arrays','greedy'],['nums is a permutation of 0 through n-1.','Return whether every global inversion is also adjacent.'],[([[1,0,2]],'The only inversion is the adjacent pair 1,0.'),([[1,2,0]],'The pair 1,0 is a nonlocal inversion.')],[[x] for x in ([0],[0,1],[1,0],[0,2,1],[2,0,1],[2,1,0],[1,0,3,2],[0,1,3,2],[2,1,0,3],[3,0,1,2],[1,3,2,0],[4,0,1,2,3])],INVERSIONS,[INVERSIONS.replace('index+2','index+1'),"def has_only_local_inversions(nums):\n    return sum(a>b for a,b in zip(nums,nums[1:]))<=1\n"],['Includes adjacent elements in the suffix test.','Checks only the number of local inversions.'],inversions_oracle,random_inversions,*lesson('A nonlocal inversion exists exactly when an element exceeds some value at least two positions right.','Sweep backward while tracking the minimum beyond the adjacent position.','For i from n-3 down, update minimum from i+2 and reject nums[i]>minimum.','The maintained suffix minimum witnesses every possible nonlocal inversion in linear time.'),'O(n)','O(1)',5),
777:entry('can_transform_lr',[('start','str'),('result','str')],'bool',['two-pointers','strings'],['Strings contain L, R, and X with equal length.','Allowed moves are XL to LX and RX to XR.'],[(['RXXLRXRXL','XRLXXRRLX'],'Non-X pieces remain ordered, L never moves right, and R never moves left.'),(['X','L'],'The non-X sequences differ, so transformation is impossible.')],[[a,b] for a,b in (('',''),('X','X'),('XL','LX'),('LX','XL'),('RX','XR'),('XR','RX'),('XXL','LXX'),('RXX','XXR'),('RL','LR'),('XXRXL','XRXLL'),('LXXR','LXXR'),('RXLX','XRXL'))],TRANSFORM,[TRANSFORM.replace("start.replace('X','')!=result.replace('X','')","False"),TRANSFORM.replace("char=='L' and a<b","char=='L' and a>b")],['Does not verify that the pieces remain in the same order.','Allows L to move right instead of left.'],transform_oracle,random_transform,*lesson('Moves never change non-X order; L can only decrease its index and R can only increase it.','Compare corresponding non-X pieces and their positions.','Reject unequal stripped strings, L with start<result, or R with start>result.','Those invariants are necessary, and empty X slots let each correctly directed piece reach its target in order.'),'O(n)','O(n)',5),
779:entry('kth_grammar_symbol',[('n','int'),('k','int')],'int',['recursion','bit-manipulation'],['1 <= n <= 30 and 1 <= k <= 2^(n-1).','Each zero expands to 01 and each one to 10; return the one-indexed kth symbol.'],[([1,1],'The first row contains only zero.'),([4,5],'Row four is 01101001, whose fifth symbol is one.')],[[n,k] for n,k in ((2,1),(2,2),(3,1),(3,2),(3,3),(3,4),(4,1),(4,8),(5,7),(6,16),(10,256),(20,524288))],GRAMMAR,[GRAMMAR.replace('k-1','k'),"def kth_grammar_symbol(n,k):\n    return (k-1)%2\n"],['Counts bits from k instead of zero-based k-1.','Assumes the row simply alternates.'],grammar_oracle,random_grammar,*lesson('A position flips once for every one bit in its zero-based index.','Use parity of popcount(k-1), equivalent to recursive parent tracing.','Return bit_count(k-1) modulo two.','Every right-child choice flips the parent symbol; those choices are exactly the one bits of k-1.'),'O(log k)','O(1)',5),
781:entry('minimum_rabbits',[('answers','list[int]')],'int',['hash-maps','greedy'],['0 <= len(answers) <= 1,000; each answer is between 0 and 999.','An answer x describes x other same-color rabbits; return the minimum possible total.'],[([[1,1,2]],'Two answer-one rabbits share a group of two; answer two requires a group of three, totaling five.'),([[10,10,10]],'All three may belong to one color group of eleven rabbits.')],[[x] for x in ([],[0],[0,0],[1],[1,1],[1,1,1],[2,2,2],[2,2,2,2],[0,1,1],[3,3,3,3],[3,3,3,3,3],[1,2,1,2])],RABBITS,[RABBITS.replace('(count+group-1)//group','count//group'),RABBITS.replace('*group','*count')],['Rounds incomplete color groups down.','Multiplies group count by report count instead of group size.'],rabbits_oracle,random_rabbits,*lesson('Rabbits reporting x fit in color groups of exactly x+1.','Group equal answers into as few ceiling-sized batches as possible.','For count c and group g=x+1, add ceil(c/g)*g.','Each batch needs a distinct color; filling batches maximally minimizes unseen rabbits.'),'O(n)','O(n)',5),
786:entry('kth_smallest_fraction',[('arr','list[int]'),('k','int')],'list[int]',['heaps','arrays'],['arr starts with 1 followed by increasing primes; k indexes all i<j fractions.','Return numerator and denominator of the kth smallest fraction.'],[([[1,2,3,5],3],'The ordered fractions begin 1/5, 1/3, then 2/5.'),([[1,7],1],'The only fraction is 1/7.')],[[a,k] for a,k in (([1,2],1),([1,2,3],1),([1,2,3],2),([1,2,3],3),([1,3,5,7],4),([1,2,5,11],5),([1,2,3,5,7],10),([1,3,7,11],2),([1,5,11,17],6),([1,2,3,5,7,11],8),([1,13,17],2),([1,2,3,5,7,11,13],20))],FRACTION,[FRACTION.replace('range(k-1)','range(k)'),FRACTION.replace('arr[i+1]/arr[j]','arr[i]/arr[j-1]')],['Pops one extra fraction.','Advances the denominator instead of the numerator.'],fraction_oracle,random_fraction,*lesson('For each denominator, fractions form an increasing list as numerator index grows.','Merge those sorted lists with a min-heap.','Seed 1/arr[j]; pop k-1 times and push the next numerator for that denominator.','Heap merging preserves global fraction order while storing only one frontier item per denominator.'),'O(k log n)','O(n)',6),
787:entry('cheapest_flight_with_stops',[('n','int'),('flights','list[list[int]]'),('src','int'),('dst','int'),('k','int')],'int',['graphs','dynamic-programming'],['Cities are 0..n-1 with positive directed flight prices.','Return the cheapest src-to-dst cost using at most k stops, or -1.'],[([4,[[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]],0,3,1],'With at most one stop, route 0-1-3 costs 700.'),([3,[[0,1,100],[1,2,100],[0,2,500]],0,2,1],'Allowing one stop makes 0-1-2 cost 200.')],[[n,f,s,d,k] for n,f,s,d,k in ((2,[],0,1,0),(2,[[0,1,5]],0,1,0),(3,[[0,1,2],[1,2,2]],0,2,0),(3,[[0,1,2],[1,2,2]],0,2,1),(3,[[0,2,9],[0,1,2],[1,2,3]],0,2,1),(4,[[0,1,1],[1,2,1],[2,3,1],[0,3,10]],0,3,1),(4,[[0,1,1],[1,3,5],[0,2,2],[2,3,2]],0,3,1),(3,[[1,0,1]],0,2,2),(3,[[0,1,1],[1,0,1],[1,2,1]],0,2,2),(2,[[0,1,7]],0,0,0),(5,[[0,1,1],[1,2,1],[2,4,1],[0,3,10],[3,4,1]],0,4,2),(3,[[0,1,10],[0,2,1],[2,1,1]],0,1,1))],FLIGHTS,[FLIGHTS.replace('following=cost[:]','following=[infinity]*n'),FLIGHTS.replace('range(k+1)','range(k)')],['Forces exactly the current edge count and loses cheaper shorter routes.','Allows only k edges instead of k+1 edges.'],flights_oracle,random_flights,*lesson('A route with at most k stops contains at most k+1 edges.','Run bounded Bellman-Ford using a snapshot per edge count.','Repeat k+1 times: copy costs and relax every flight from the previous row.','Snapshots prevent one round from using multiple new edges, so each round expands the allowed route length by exactly one.'),'O(k*flights)','O(n)',5),
788:entry('rotated_digit_count',[('n','int')],'int',['math','simulation'],['1 <= n <= 10,000.','Count numbers that remain valid but change after rotating every digit 180 degrees.'],[([10],'The good numbers are 2, 5, 6, and 9.'),([1],'One remains one, so none qualify.')],[[n] for n in (2,5,6,9,11,15,20,25,50,100,256,10000)],ROTATED,[ROTATED.replace("bool(digits&changed)",'True'),ROTATED.replace("valid=set('0125689')","valid=set('0123456789')")],['Counts unchanged numbers containing only 0,1,8.','Allows invalid digits 3,4,7.'],rotated_oracle,random_rotated,*lesson('A good number uses only rotatable digits and includes at least one digit that changes.','Check each number’s digit set against valid and changed sets.','Accept digits subset of 0125689 and intersection with 2569 nonempty.','The first condition makes rotation defined; the second makes the rotated result different.'),'O(n*digits)','O(1)',5),
789:entry('can_escape_ghosts',[('ghosts','list[list[int]]'),('target','list[int]')],'bool',['math','geometry'],['All players move one Manhattan step per turn and ghosts may wait.','Return whether the player from [0,0] can reach target before every ghost.'],[([[[1,0],[0,3]],[0,1]],'The player needs one move while each ghost needs at least two.'),([[[1,0]],[2,0]],'The ghost reaches the target in one move, no later than the player.')],[[g,t] for g,t in (([[2,0]],[1,0]),([[-2,0]],[1,0]),([[5,5]],[1,1]),([[0,1]],[0,1]),([[-1,-1]],[1,1]),([[10,0],[0,10]],[5,5]),([[1,1]],[2,2]),([[3,0]],[0,2]),([[-3,0]],[-1,0]),([[0,0]],[1,1]),([[4,4],[2,0]],[1,2]),([[-5,-5]],[0,0]))],ESCAPE,[ESCAPE.replace('>distance','>=distance'),ESCAPE.replace('abs(x-target[0])+abs(y-target[1])','abs(x)+abs(y)')],['Allows a tie even though a ghost can block the target.','Measures each ghost from the origin instead of from the target.'],escape_oracle,random_escape,*lesson('A ghost can always head directly to the target and wait there.','Compare the player’s Manhattan distance with every ghost’s distance to target.','Escape only if each ghost distance is strictly greater than the player distance.','If a ghost arrives no later it blocks the target; otherwise the player’s direct shortest route finishes first.'),'O(ghosts)','O(1)',5),
790:entry('domino_tromino_tilings',[('n','int')],'int',['dynamic-programming'],['1 <= n <= 1,000.','Count tilings of a 2-by-n board with dominoes and trominoes modulo 1,000,000,007.'],[([3],'There are five complete tilings of a 2-by-3 board.'),([1],'Only one vertical domino fits.')],[[n] for n in (2,4,5,6,7,8,10,20,50,100,500,1000)],TILING,[TILING.replace('2*third+first','third+second'),TILING.replace('if n<=2:return n','if n<=2:return 1')],['Uses the domino-only recurrence and misses tromino configurations.','Returns one instead of two for n=2.'],tiling_oracle,random_tiling,*lesson('Tracking the two one-cell gap states yields a recurrence that collapses to f(n)=2f(n-1)+f(n-3).','Keep the last three complete-board counts.','Start f0=1,f1=1,f2=2; iterate 2*latest+three_back modulo M.','The collapsed recurrence accounts for a final domino or paired orientations of the gap-producing tromino arrangements.'),'O(n)','O(1)',5),
791:entry('custom_sort_text',[('order','str'),('s','str')],'str',['hash-maps','strings'],['order has distinct characters; every ordered character must precede later ordered characters.','For deterministic feedback, preserve original relative order among characters absent from order.'],[(['cba','abcd'],'c, b, and a follow the custom order; d remains afterward.'),(['kqep','pekeq'],'Ordered characters produce kqeep while preserving the remaining character positions as a suffix.')],[[o,s] for o,s in (('a','a'),('a','bbb'),('ba','abc'),('abc','cba'),('cba','aabbcc'),('x','xyzx'),('zyx','xyzabc'),('ab','ccba'),('qwe','eeqqwwr'),('fed','abcdef'),('b','bbbb'),('ac','cabdca'))],CUSTOM,[CUSTOM.replace('for char in order','for char in reversed(order)'),CUSTOM.replace("if char in counts:answer.append(char);counts[char]-=1","if char in counts:answer.append(sorted(counts)[0]);counts[char]-=1")],['Applies the custom order backward.','Sorts unordered suffix characters instead of preserving their input order.'],custom_oracle,random_custom,*lesson('Custom-order characters can be emitted from counts; all others form a stable suffix.','Count s, emit ordered groups, then scan s for remaining characters.','Append char*count for order; remove it; append leftover occurrences in original scan order.','Every ordered relation is satisfied, multiplicities are preserved, and the explicit suffix rule makes output deterministic.'),'O(len(order)+len(s))','O(alphabet)',5),
792:entry('matching_subsequence_count',[('s','str'),('words','list[str]')],'int',['strings','queues'],['1 <= len(s) <= 50,000; words are nonempty lowercase strings.','Count words that are subsequences of s, including duplicate word entries separately.'],[(['abcde',['a','bb','acd','ace']],'a, acd, and ace are subsequences, so the count is three.'),(['dsahjpjauf',['ahjpjau','ja','ahbwzgqnuk','tnmlanowax']],'The first two words match as subsequences.')],[[s,w] for s,w in (('a',['a']),('a',['b']),('abc',['abc','ac','c']),('abc',['abc','abc']),('aaaa',['a','aa','aaaa','aaaaa']),('xyz',['xz','zx']),('abcde',['edc']),('abbc',['abc','bbc']),('q',['q','q','x']),('abcdef',['ace','bdf','af']),('mississippi',['mip','sip','miss']),('leetcode',['leet','code','etc']))],SUBSEQUENCES,[SUBSEQUENCES.replace('waiting[char]=[]','waiting[char]=current'),SUBSEQUENCES.replace('answer+=1','answer=1')],['Leaves advanced iterators in the old bucket and advances them repeatedly.','Collapses all matched words to a boolean-like one.'],subsequences_oracle,random_subsequences,*lesson('Each waiting word needs only its next unmatched character.','Bucket word iterators by their next required character and advance one bucket per source character.','Remove the current bucket, advance each iterator, count completions, and rebucket the rest.','Each word character advances once, avoiding a full scan of s for every word.'),'O(len(s)+total word characters)','O(total word characters)',5),
794:entry('valid_tic_tac_toe',[('board','list[str]')],'bool',['simulation','logic'],['board is a 3-by-3 grid of X, O, and spaces.','X moves first; turns alternate and no moves occur after a win.'],[([['O  ','   ','   ']],'O cannot appear before X, so this board is unreachable.'),([['XOX','O O','XOX']],'Counts alternate correctly and neither player made an earlier incompatible win.')],[[b] for b in (['   ','   ','   '],['X  ','   ','   '],['XO ','   ','   '],['XX ','OO ','   '],['XXX','OO ','   '],['OOO','XX ','X  '],['XXX','OOO','   '],['XOX','OXO','XOX'],['XOX','O O','X X'],['XXO','OOX','XOX'],['OOX','XXO','X  '],['X X',' O ','  O'])],TICTACTOE,[TICTACTOE.replace("x in (o,o+1)",'True'),TICTACTOE.replace("not (wins('X') and wins('O'))",'True')],['Ignores turn-count legality.','Allows both players to have winning lines.'],tictactoe_oracle,random_board,*lesson('Reachability is determined by move counts and whether a winning line agrees with who moved last.','Count marks and detect wins for rows, columns, and diagonals.','Require x=o or x=o+1; X win requires x=o+1; O win requires x=o; reject dual wins.','Those conditions exactly encode alternating turns and the fact that play stops immediately after the winning move.'),'O(1)','O(1)',5),
795:entry('bounded_max_subarray_count',[('nums','list[int]'),('left','int'),('right','int')],'int',['sliding-windows','arrays'],['1 <= len(nums) <= 100,000 and left <= right.','Count nonempty subarrays whose maximum lies in [left,right].'],[([[2,1,4,3],2,3],'The valid subarrays are [2], [2,1], and [3].'),([[2,9,2,5,6],2,8],'Seven subarrays have a maximum between two and eight.')],[[n,l,r] for n,l,r in (([1],1,1),([1],2,3),([3],1,2),([1,2],1,2),([1,2,3],2,2),([2,2,2],2,2),([0,1,0],1,1),([5,1,2],2,4),([1,5,1],2,4),([2,1,4,3],4,4),([1,2,3,4],1,4),([9,1,2,9,3],2,3))],BOUNDED,[BOUNDED.replace('last_too_large=-1','last_too_large=0'),BOUNDED.replace('last_in_range-last_too_large','index-last_too_large')],['Initializes the last invalid boundary incorrectly.','Counts every suffix after a valid value even when its maximum is too small.'],bounded_oracle,random_bounded,*lesson('For each right endpoint, valid starts lie after the last too-large value and no later than the last in-range value.','Track those two most recent indices.','Update invalid on value>right and qualifying on left<=value<=right; add max(0,qualifying-invalid).','Every counted start produces a legal maximum, and every legal suffix start lies in that exact interval.'),'O(n)','O(1)',5),
796:entry('is_rotation',[('s','str'),('goal','str')],'bool',['strings'],['Strings contain lowercase letters.','Return whether repeated left shifts can transform s into goal.'],[(['abcde','cdeab'],'Two left shifts transform abcde into cdeab.'),(['abcde','abced'],'No cyclic cut produces abced.')],[[a,b] for a,b in (('a','a'),('a','b'),('ab','ba'),('ab','ab'),('abc','bca'),('abc','cab'),('abc','acb'),('aaaa','aaaa'),('abab','baba'),('waterbottle','erbottlewat'),('x','xx'),('abcd','dabc'))],ROTATE,[ROTATE.replace("len(s)==len(goal) and ",''),ROTATE.replace('s+s','s')],['Does not require equal lengths.','Checks only ordinary substring containment, not wraparound rotations.'],rotate_oracle,random_rotate,*lesson('Every rotation is a length-n window crossing the boundary in s+s.','Require equal lengths, then search goal inside the doubled string.','Return len(s)==len(goal) and goal in s+s.','Doubling contains every possible cyclic cut exactly as a contiguous length-n window.'),'O(n)','O(n)',3),
797:entry('all_source_target_paths',[('graph','list[list[int]]')],'list[list[int]]',['graphs','depth-first-search'],['graph is a directed acyclic graph with nodes 0 through n-1.','Return every path from node 0 to node n-1.'],[([[[1,2],[3],[3],[]]],'The two paths are 0-1-3 and 0-2-3.'),([[[4,3,1],[3,2,4],[3],[4],[]]],'Depth-first traversal finds all five source-to-target routes.')],[[g] for g in (([[]]),([[1],[]]),([[1,2],[],[]]),([[1],[2],[]]),([[1,2],[2],[]]),([[1,2,3],[3],[3],[]]),([[2],[2],[]]),([[1,3],[2],[3],[]]),([[1],[3],[3],[]]),([[1,2],[3],[4],[4],[]]),([[1,2],[],[3],[]]),([[1,2,3],[4],[4],[4],[]]))],PATHS,[PATHS.replace('path+[following]','[following]'),PATHS.replace('for following in graph[node]','for following in graph[node][:1]')],['Drops the path prefix while recursing.','Explores only the first outgoing edge.'],paths_oracle,random_paths,*lesson('In a DAG, depth-first search can enumerate paths without cycle handling.','Carry the current path and branch once per outgoing edge.','At target append path; otherwise recurse on each neighbor with path+[neighbor].','Each recursion branch corresponds to one unique edge sequence, so every source-target path is emitted once.'),'O(total output size)','O(path length)',5),
799:entry('champagne_amount',[('poured','int'),('query_row','int'),('query_glass','int')],'float',['dynamic-programming','simulation'],['0 <= poured <= 1,000,000,000 and 0 <= query_glass <= query_row <= 100.','Each full glass keeps one cup and splits overflow equally downward; return queried fill up to one.'],[([1,1,1],'One cup fills only the top glass, leaving this lower glass empty.'),([2,1,1],'One overflow cup splits evenly, so the queried glass contains one half.')],[[p,r,g] for p,r,g in ((0,0,0),(1,0,0),(2,0,0),(2,1,0),(3,1,0),(3,1,1),(4,2,1),(10,3,0),(10,3,1),(25,6,1),(100,10,5),(1000,20,10))],CHAMPAGNE,[CHAMPAGNE.replace('(value-1)/2','value/2'),CHAMPAGNE.replace('min(1.0,row[query_glass])','row[query_glass]')],['Splits the retained cup as well as overflow.','Returns uncapped volume rather than glass fullness.'],champagne_oracle,random_champagne,*lesson('Only overflow beyond one cup reaches the next row, split equally between two children.','Simulate one row of volumes at a time.','For each value add max(0,(value-1)/2) to both children; cap only the final answer.','All incoming contributions are accumulated before the next row, matching simultaneous flow through the tower.'),'O(row²)','O(row)',5),
800:entry('nearest_shorthand_color',[('color','str')],'str',['math','strings'],['color is lowercase #RRGGBB hexadecimal.','Return the closest color whose channel pairs repeat one digit; ties choose the smaller channel.'],[(['#09f166'],'Each channel rounds to a multiple of hexadecimal 11, producing #11ee66.'),(['#4e3fe1'],'The nearest shorthand channels produce #5544dd.')],[[c] for c in ('#000000','#ffffff','#010101','#080808','#090909','#101010','#111111','#121212','#abcdef','#123456','#f0e0d0','#89abcd')],COLOR,[COLOR.replace('(value+8)//17','value//17'),COLOR.replace("max(0,min(15,(value+8)//17))","max(0,min(15,round(value/16)))")],['Always rounds channels downward.','Uses multiples of sixteen instead of seventeen.'],color_oracle,random_color,*lesson('A repeated hex digit has numeric value 17*d for d from 0 through 15.','Round each RGB channel to its nearest multiple of seventeen.','digit=(value+8)//17; emit that hex digit twice for each channel.','Adjacent shorthand values differ by seventeen, so integer nearest rounding minimizes squared RGB distance independently per channel.'),'O(1)','O(1)',3),
802:entry(
    'eventual_safe_nodes',[('graph','list[list[int]]')],'list[int]',
    ['graphs','depth-first-search'],
    ['Nodes are 0 through n-1 in a directed graph.',
     'A node is safe when every possible path from it eventually ends; return safe nodes sorted.'],
    [([[[1,2],[2,3],[5],[0],[5],[],[]]],
      'Nodes 2,4,5,6 cannot reach the cycle among 0,1,3.'),
     ([[[1,2,3,4],[1,2],[3,4],[0,4],[]]],
      'Only terminal node four is eventually safe.')],
    [[graph] for graph in ([[]],[[0]],[[1],[]],[[1],[0]],[[1],[2],[]],
                            [[1,2],[2],[1]],[[1,2],[],[]],[[1],[2],[3],[]],
                            [[1],[2],[1],[]],[[1,2],[3],[3],[]],
                            [[1],[2],[0],[2]],[[1,2],[2],[3],[1],[]])],
    SAFE,
    [SAFE.replace('state[node]=1','state[node]=2'),
     SAFE.replace('all(safe(following)','any(safe(following)')],
    ['Marks a node safe before exploring its outgoing paths.',
     'Requires only one safe successor instead of every successor.'],
    safe_oracle,random_safe,
    *lesson('A node is unsafe if DFS reaches a currently visiting node or any unsafe successor.',
            'Use three colors: unseen, visiting, and proven safe.',
            'Mark visiting; recursively require every neighbor safe; then mark safe.',
            'A visiting revisit detects a reachable cycle, while completed safe nodes memoize paths already proved terminating.'),
    'O(nodes+edges)','O(nodes)',5),
804:entry('unique_morse_count',[('words','list[str]')],'int',['hash-maps','strings'],['Words contain lowercase English letters.','Translate each word using standard Morse codes and count distinct translations.'],[([['gin','zen','gig','msg']],'Gin and zen share one code while gig and msg share another, giving two.'),([['a']],'A single word produces one unique transformation.')],[[w] for w in ((['e','t']),(['a','b','c']),(['gin','zen']),(['sos','sos']),(['abc','acb']),(['z','zz']),(['hello','world']),(['no','on']),(['leetcode','code']),(['morse','words','study']),(['a','et']),(['abc','abc','def']))],MORSE_CODE,[MORSE_CODE.replace('ord(char)-97','ord(char)-96'),MORSE_CODE.replace("return len({","return sum(len(code) for code in {")],['Uses a one-off alphabet index.','Returns total encoded length rather than number of distinct encodings.'],morse_oracle,random_morse,*lesson('Different words may concatenate to the same Morse sequence, so compare completed encodings.','Translate characters through a fixed 26-code table and insert each concatenation into a set.','For each word join codes[ord(c)-97]; return set size.','The set merges exactly those words with identical full transformations.'),'O(total letters)','O(total encoded length)',3),
806:entry('writing_line_usage',[('widths','list[int]'),('s','str')],'list[int]',['greedy','strings'],['widths gives each lowercase letter width from 2 to 10; a line holds at most 100 units.','Return [number of lines, width used on the final line].'],[([[10]*26,'abcdefghijklmnopqrstuvwxyz'],'Ten letters fit per line, so 26 letters use three lines and 60 units on the last.'),([[4]*26,'bbbcccdddaaa'],'All twelve letters fit on one line using 48 units.')],[[w,s] for w,s in (([2]*26,'a'),([10]*26,'abcdefghij'),([10]*26,'abcdefghijk'),([5]*26,'abcdefghijklmnopqrst'),([5]*26,'abcdefghijklmnopqrstu'),([2]*26,'z'*50),([2]*26,'z'*51),([3]*26,'abc'),([10]*26,'a'*100),([4]*26,'hello'),([i%9+2 for i in range(26)],'azby'),([7]*26,'codestudy'))],LINES,[LINES.replace('>100','>=100'),LINES.replace('lines=1','lines=0')],['Starts a new line when a letter exactly fills the current line.','Fails to count the initial line.'],lines_oracle,random_lines,*lesson('Letters are placed greedily because their order is fixed and a line break is needed only when the next width would overflow.','Track current used width and line count.','Before adding a letter, if used+width>100 increment lines and reset used; then add width.','Every break is forced and delaying no forced break minimizes the line count.'),'O(len(s))','O(1)',3),
}

BATCH[799]['comparator']='float'
BATCH[794]['sample_contract_adapter']={
    'source_sample':'Input board = ["O "," "," "] → Output false.',
    'arguments':[['O  ','   ','   ']],
    'expected':False,
    'reason':'The workbook collapsed repeated spaces inside the three fixed-width rows; the source contract requires a 3-by-3 board.',
}

BATCH[791]['boundaries'].append(['a','dcba'])
BATCH[791]['wrong'][1]='''\
def custom_sort_text(order, s):
    from collections import Counter
    counts=Counter(s);answer=''
    for char in order:answer+=char*counts.pop(char,0)
    return answer+''.join(sorted(char for char,count in counts.items() for _ in range(count)))
'''
BATCH[794]['wrong'][1]='''\
def valid_tic_tac_toe(board):
    x=sum(row.count('X') for row in board);o=sum(row.count('O') for row in board)
    lines=list(board)+[''.join(board[r][c] for r in range(3)) for c in range(3)]
    xwin='XXX' in lines;owin='OOO' in lines
    return x in (o,o+1) and not (xwin and owin)
'''
BATCH[794]['wrong_reasons'][1]='Checks mark counts and dual wins but not whether the winner made the last move.'
BATCH[794]['boundaries'].append([['OOO','XX ','XX ']])
