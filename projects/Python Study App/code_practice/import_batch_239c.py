"""Digit permutations, binary XOR, request windows, string merging, and parity ranges."""
from itertools import permutations, product
from math import factorial
from .import_batch_055 import entry


def digitorial_oracle(args):
    digits=str(args[0])
    for order in set(permutations(digits)):
        if order[0]!='0':
            value=int(''.join(order))
            if sum(factorial(int(character)) for character in order)==value:return True
    return False
def random_digitorial(rng):return [rng.randint(1,9_999_999)]

def xor_oracle(args):
    s,t=args
    return max((''.join(str(int(a)^int(b)) for a,b in zip(s,order)) for order in set(permutations(t))))
def random_xor(rng):
    n=rng.randint(1,9);return [''.join(rng.choice('01') for _ in range(n)),''.join(rng.choice('01') for _ in range(n))]

def requests_valid(items,k,window):
    by_user={}
    for user,time in items:by_user.setdefault(user,[]).append(time)
    for times in by_user.values():
        times.sort()
        for left in range(len(times)):
            if left+k<len(times) and times[left+k]-times[left]<=window:return False
    return True
def requests_oracle(args):
    requests,k,window=args;best=0
    for mask in range(1<<len(requests)):
        chosen=[request for i,request in enumerate(requests) if mask>>i&1]
        if len(chosen)>best and requests_valid(chosen,k,window):best=len(chosen)
    return best
def random_requests(rng):
    n=rng.randint(1,12);return [[[rng.randint(1,4),rng.randint(0,20)] for _ in range(n)],rng.randint(1,4),rng.randint(0,8)]

def merge_oracle(args):
    text,k=args;values=list(text)
    while True:
        pair=None
        for left in range(len(values)):
            for right in range(left+1,min(len(values),left+k+1)):
                if values[left]==values[right]:pair=(left,right);break
            if pair:break
        if not pair:return ''.join(values)
        values.pop(pair[1])
def random_merge(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,30))),rng.randint(0,10)]

def parity_oracle(args):
    nums=args[0]
    if len(nums)==1:return [0,0]
    answers=[]
    for first in (0,1):
        wrong=[i for i,value in enumerate(nums) if value%2!=(first+i)%2]
        best=10**30
        for directions in product((-1,1),repeat=len(wrong)):
            values=nums[:]
            for index,direction in zip(wrong,directions):values[index]+=direction
            best=min(best,max(values)-min(values))
        answers.append([len(wrong),best])
    return min(answers)
def random_parity(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(1,10))]]

DIGITORIAL='''def has_digitorial_permutation(n):
    factorials=[1,1,2,6,24,120,720,5040,40320,362880]
    total=sum(factorials[int(character)] for character in str(n))
    return sorted(str(total))==sorted(str(n))
'''

XOR='''def maximum_rearranged_xor(s,t):
    zeros=t.count('0');ones=len(t)-zeros;answer=[]
    for bit in s:
        if bit=='0' and ones:answer.append('1');ones-=1
        elif bit=='1' and zeros:answer.append('1');zeros-=1
        elif zeros:answer.append('0');zeros-=1
        else:answer.append('0');ones-=1
    return ''.join(answer)
'''

REQUESTS='''def maximum_valid_requests(requests,k,window):
    from collections import defaultdict,deque
    groups=defaultdict(list)
    for user,time in requests:groups[user].append(time)
    answer=len(requests)
    for times in groups.values():
        kept=deque()
        for time in sorted(times):
            while kept and time-kept[0]>window:kept.popleft()
            if len(kept)<k:kept.append(time)
            else:answer-=1
    return answer
'''

MERGE='''def merge_close_characters(s,k):
    last={};answer=[]
    for character in s:
        position=len(answer)
        if character in last and position-last[character]<=k:continue
        answer.append(character);last[character]=position
    return ''.join(answer)
'''

PARITY='''def minimum_parity_alternation(nums):
    if len(nums)==1:return [0,0]
    low=min(nums);high=max(nums)
    def evaluate(pattern):
        operations=0;minimum=10**30;maximum=-10**30
        for index,value in enumerate(nums):
            if value%2!=(pattern+index)%2:
                operations+=1
                if value==low:value+=1
                elif value==high:value-=1
            minimum=min(minimum,value);maximum=max(maximum,value)
        return [operations,max(1,maximum-minimum)]
    return min(evaluate(0),evaluate(1))
'''

def lesson(a,b,c,d):return [a,b,c,d]
D_CASES=[[n] for n in (145,1,2,10,12,40585,154,140,999,12345,100,101,222,999999,40558)]
X_CASES=[[s,t] for s,t in (('101','011'),('0','0'),('0','1'),('1','0'),('1','1'),('00','11'),('11','00'),('10','10'),('001','001'),('111','101'),('0101','0011'),('0000','0101'),('1100','1010'),('10101','11100'),('000111','101010'))]
Q_CASES=[[r,k,w] for r,k,w in (([[1,1],[2,1],[1,7],[2,8]],1,4),([[1,1]],1,0),([[1,1],[1,1]],1,0),([[1,1],[1,2]],1,1),([[1,1],[1,2]],2,1),([[1,1],[2,1]],1,10),([[1,1],[1,5],[1,9]],1,4),([[1,1],[1,5],[1,9]],2,4),([[1,3],[1,1],[1,2]],2,2),([[1,0],[2,0],[1,0],[2,0]],1,0),([[1,1],[1,2],[2,2],[1,3]],2,2),([[3,10],[3,1],[3,6]],1,4),([[1,1],[2,2],[1,3],[2,4]],1,2),([[1,0],[1,10],[1,20]],3,0),([[1,5],[1,5],[1,5],[2,5]],2,0))]
M_CASES=[[s,k] for s,k in (('abca',3),('a',0),('aa',0),('aa',1),('aba',2),('abca',2),('aaaa',1),('abcabc',3),('abacada',2),('mississippi',3),('banana',2),('abcde',10),('aabbcc',1),('abccba',4),('zzxyzz',2))]
P_CASES=[[[*v]] for v in ([-2,-3,1,4],[1],[2],[1,2],[2,2],[1,1,1],[1,2,3],[2,4,6,8],[-5,-4,-3],[0,10,1],[7,7,8,8],[3,100,5,102],[-10,9,-8,7],[4,1,6,3,8],[0,0,0,1])]

BATCH={
3848:entry('has_digitorial_permutation',[('n','int')],'bool',['math','counting','permutations'],['n is a positive integer with at most seven decimal digits.','Permutations with a leading zero are not valid integers.','Return whether some permutation equals the sum of the factorials of its own digits.'],[([145],'145 equals 1!+4!+5!, so its own digit order is a valid digitorial.'),([154],'Reordering the digits as 145 produces a digitorial, so the answer is true.')],D_CASES,DIGITORIAL,[DIGITORIAL.replace('sum(factorials[int(character)] for character in str(n))','sum(int(character) for character in str(n))'),DIGITORIAL.replace("sorted(str(total))==sorted(str(n))","str(total)==str(n)")],['Sums digits instead of their factorials.','Accepts only the original digit order instead of any permutation.'],digitorial_oracle,random_digitorial,lesson('Permuting digits never changes the multiset of digits or their factorial sum.','Compute that invariant sum once, then compare its digits with the input digits.','Equal sorted digit sequences prove the sum is a permutation without enumerating arrangements.','If a valid permutation exists it must equal the fixed factorial sum; conversely equal digit multisets provide that permutation, and a positive integer has no leading-zero representation.'),'O(d log d)','O(d)',5),
3849:entry('maximum_rearranged_xor',[('s','str'),('t','str')],'str',['strings','greedy','bit manipulation'],['s and t are nonempty binary strings of equal length.','You may rearrange t arbitrarily but may not rearrange s.','Return the lexicographically largest XOR string, which is also the largest binary value.'],[(['101','011'],'Use rearrangement 110: XOR with 101 gives 011? A better rearrangement 011 gives 110, which is maximal.'),(['00','11'],'Both positions can differ, producing 11.')],X_CASES,XOR,[XOR.replace("if bit=='0' and ones","if bit=='0' and zeros"),XOR.replace("for bit in s:","for bit in reversed(s):")],['Consumes an equal bit when s is zero instead of preferring a differing one.','Greedily maximizes from the least-significant end and returns reversed positional decisions.'],xor_oracle,random_xor,lesson('A one at the earliest possible position dominates every later XOR bit.','Count zeroes and ones in t; for each bit of s, consume the opposite bit whenever available.','If the opposite supply is empty, consume the matching bit and append zero.','The exchange argument fixes the earliest bit optimally without harming any earlier choice, so repeating it yields the lexicographic maximum.'),'O(n)','O(n)',5),
3851:entry('maximum_valid_requests',[('requests','list[list[int]]'),('k','int'),('window','int')],'int',['arrays','greedy','sorting','sliding window'],['Each request is [user,time], k is positive, and window is nonnegative.','For one user, no k+1 retained requests may have latest time minus earliest time at most window.','Delete as few requests as possible and return the maximum retained total.'],[([[[1,1],[2,1],[1,7],[2,8]],1,4],'Each user’s requests are more than four time units apart, so all four remain.'),([[[1,1],[1,2]],1,1],'The two same-user requests lie within the window, so only one can remain.')],Q_CASES,REQUESTS,[REQUESTS.replace('time-kept[0]>window','time-kept[0]>=window'),REQUESTS.replace('for times in groups.values():','for times in list(groups.values())[:1]:')],['Treats requests exactly window units apart as outside the restricted interval.','Enforces the restriction for only the first user.'],requests_oracle,random_requests,lesson('Users are independent, so optimize each user’s sorted timeline separately.','Keep a deque of accepted times still within window of the current request.','Accept when fewer than k remain in that deque; otherwise reject the current, latest request.','When a window is full, keeping earlier requests expires no later than keeping the current one, so rejecting the current request is an optimal greedy exchange.'),'O(n log n)','O(n)',6),
3853:entry('merge_close_characters',[('s','str'),('k','int')],'str',['strings','hash maps','simulation'],['s is a nonempty lowercase string and k is nonnegative.','Repeatedly delete the right member of the first equal-character pair whose current indices differ by at most k.','Continue on the shortened string until no qualifying pair remains.'],[(['abca',3],'The two a characters are three positions apart, so the right a merges away and abc remains.'),(['aa',0],'Distinct indices are never within distance zero, so aa remains unchanged.')],M_CASES,MERGE,[MERGE.replace('<=k','<k'),MERGE.replace('position=len(answer)','position=len(s)')],['Excludes equal characters exactly k positions apart.','Uses the original string length instead of the character’s updated output position.'],merge_oracle,random_merge,lesson('Only characters that survive affect all later updated positions.','Build the final string left to right and remember each character’s most recent surviving index.','Skip a character when its current output index is within k of that survivor; otherwise append and update its index.','Earlier survivors implement the required leftmost merge order, and skipped characters never occupy positions in the evolving string.'),'O(n)','O(n)',5),
3854:entry('minimum_parity_alternation',[('nums','list[int]')],'list[int]',['arrays','greedy','parity'],['nums is a nonempty integer array.','One operation changes one element by +1 or -1; first minimize operations needed for alternating parity.','Among minimum-operation results, minimize max(nums)-min(nums); return [operations,range].'],[([[-2,-3,1,4]],'The best parity pattern needs two changes; choosing directions toward the interior gives final range six.'),([[1]],'A singleton already alternates and has range zero, giving [0,0].')],P_CASES,PARITY,[PARITY.replace('return min(evaluate(0),evaluate(1))','return evaluate(0)'),PARITY.replace('if value==low:value+=1','if value==low:value-=1')],['Considers only the pattern beginning with even parity.','Moves a mismatched minimum outward, missing the smallest possible range tie-break.'],parity_oracle,random_parity,lesson('There are only two target parity patterns, and every mismatch costs exactly one operation.','For each pattern, count mismatches; changing an interior value cannot affect range, while a mismatched extreme should move inward.','Compute [operations,range] for both starts and take the lexicographically smaller pair.','This first minimizes operations; among tied patterns, inward moves attain the smallest possible extreme span, with a non-single alternating array having range at least one.'),'O(n)','O(1)',6),
}
