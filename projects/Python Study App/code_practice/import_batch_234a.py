"""Monotone splits, two ZigZag constraints, nonzero XOR, and balanced removal."""
from itertools import product
from .import_batch_055 import entry

MOD=10**9+7

def split_oracle(args):
    nums=args[0];answer=None
    for cut in range(1,len(nums)):
        left=nums[:cut];right=nums[cut:]
        if all(a<b for a,b in zip(left,left[1:])) and all(a>b for a,b in zip(right,right[1:])):
            value=abs(sum(left)-sum(right));answer=value if answer is None else min(answer,value)
    return -1 if answer is None else answer

def random_split(rng):return [[rng.randint(1,20) for _ in range(rng.randint(2,12))]]

def zigzag_oracle(args):
    n,left,right=args
    if right-left==1:return 2
    answer=0
    for values in product(range(left,right+1),repeat=n):
        if any(a==b for a,b in zip(values,values[1:])):continue
        if any((a<b<c) or (a>b>c) for a,b,c in zip(values,values[1:],values[2:])):continue
        answer+=1
    return answer%MOD

def random_zigzag_one(rng):return [rng.randint(3,7),1,(size:=rng.randint(2,4))]
def random_zigzag_two(rng):return [rng.randint(3,7),3,3+rng.randint(1,3)]

def xor_oracle(args):
    nums=args[0];best=0
    for mask in range(1,1<<len(nums)):
        value=0;length=0
        for index,item in enumerate(nums):
            if mask>>index&1:value^=item;length+=1
        if value:best=max(best,length)
    return best

def random_xor(rng):return [[rng.randint(0,31) for _ in range(rng.randint(1,13))]]

def removal_oracle(args):
    s,k=args;target='('*k+')'*k
    while target in s:s=s.replace(target,'')
    return s

def random_removal(rng):
    n=rng.randint(2,30);return [''.join(rng.choice('()') for _ in range(n)),rng.randint(1,n//2)]


SPLIT='''def minimum_increasing_decreasing_split(nums):
    n=len(nums);prefix=[True]*n;suffix=[True]*n
    for index in range(1,n):prefix[index]=prefix[index-1] and nums[index-1]<nums[index]
    for index in range(n-2,-1,-1):suffix[index]=suffix[index+1] and nums[index]>nums[index+1]
    total=sum(nums);left_sum=0;answer=None
    for cut in range(1,n):
        left_sum+=nums[cut-1]
        if prefix[cut-1] and suffix[cut]:
            difference=abs(left_sum-(total-left_sum));answer=difference if answer is None else min(answer,difference)
    return -1 if answer is None else answer
'''

ZIGZAG_ONE='''def count_zigzag_arrays(n,l,r):
    mod=10**9+7;size=r-l+1;up=[1]*size;down=[1]*size
    for _ in range(n-1):
        new_up=[0]*size;new_down=[0]*size;running=0
        for index in range(size):new_up[index]=running;running=(running+down[index])%mod
        running=0
        for index in range(size-1,-1,-1):new_down[index]=running;running=(running+up[index])%mod
        up,down=new_up,new_down
    return sum(up+down)%mod
'''

ZIGZAG_TWO='''def count_large_zigzag_arrays(n,l,r):
    mod=10**9+7;size=r-l+1
    up=[0]*size;down=[0]*size
    for index in range(size):up[index]=index;down[index]=size-1-index
    sequence=[1,size,sum(up+down)%mod]
    for _ in range(3,4*size+8):
        new_up=[0]*size;new_down=[0]*size;running=0
        for index in range(size):new_up[index]=running;running=(running+down[index])%mod
        running=0
        for index in range(size-1,-1,-1):new_down[index]=running;running=(running+up[index])%mod
        up,down=new_up,new_down;sequence.append(sum(up+down)%mod)
    def berlekamp(values):
        current=[1];backup=[1];length=0;shift=1;last=1
        for position in range(len(values)):
            discrepancy=values[position]
            for index in range(1,length+1):discrepancy=(discrepancy+current[index]*values[position-index])%mod
            if discrepancy==0:shift+=1;continue
            previous=current[:];factor=discrepancy*pow(last,mod-2,mod)%mod
            if len(current)<len(backup)+shift:current+=([0]*(len(backup)+shift-len(current)))
            for index,value in enumerate(backup):current[index+shift]=(current[index+shift]-factor*value)%mod
            if 2*length<=position:length=position+1-length;backup=previous;last=discrepancy;shift=1
            else:shift+=1
        return [(-value)%mod for value in current[1:length+1]]
    recurrence=berlekamp(sequence);order=len(recurrence)
    if n<len(sequence):return sequence[n]
    def combine(first,second):
        result=[0]*(2*order-1)
        for i,a in enumerate(first):
            for j,b in enumerate(second):result[i+j]=(result[i+j]+a*b)%mod
        for degree in range(2*order-2,order-1,-1):
            for offset,value in enumerate(recurrence,1):result[degree-offset]=(result[degree-offset]+result[degree]*value)%mod
        return result[:order]
    answer=[1]+[0]*(order-1);power=([recurrence[0]] if order==1 else [0,1]+[0]*(order-2));exponent=n
    while exponent:
        if exponent&1:answer=combine(answer,power)
        power=combine(power,power);exponent//=2
    return sum(coefficient*sequence[index] for index,coefficient in enumerate(answer))%mod
'''

XOR='''def longest_nonzero_xor_subsequence(nums):
    total=0
    for value in nums:total^=value
    if total:return len(nums)
    if all(value==0 for value in nums):return 0
    return len(nums)-1
'''

REMOVAL='''def remove_k_balanced_substrings(s,k):
    runs=[]
    for character in s:
        if runs and runs[-1][0]==character:runs[-1][1]+=1
        else:runs.append([character,1])
        if character==')' and len(runs)>1 and runs[-1][1]==k and runs[-2][0]=='(' and runs[-2][1]>=k:
            runs.pop();runs[-1][1]-=k
            if runs[-1][1]==0:runs.pop()
    return ''.join(character*count for character,count in runs)
'''

def lesson(a,b,c,d):return [a,b,c,d]

S_CASES=[[[x for x in values]] for values in ([1,2],[2,1],[1,2,3],[3,2,1],[1,1,2],[2,1,1],[1,4,3,2],[2,1,3],[1,5,2,1],[2,4,6,5,3],[5,1,2,3],[1,3,5,4,2,1])]
Z1_CASES=[[n,l,r] for n,l,r in ((3,2,3),(4,1,2),(5,3,4),(6,1,3),(4,2,5),(7,1,3),(8,4,6),(5,1,5),(9,2,4),(10,1,3),(6,5,9),(12,1,4))]
Z2_CASES=[[n,l,r] for n,l,r in ((3,2,3),(4,1,2),(5,3,4),(6,1,3),(7,1,4),(8,4,6),(9,1,3),(10,2,5),(12,1,4),(20,1,2),(1000000000,1,2),(999999937,7,8))]
X_CASES=[[[x for x in values]] for values in ([0],[1],[0,0],[1,1],[1,2],[2,3,5],[5,5,0],[7,0,7,0],[1,2,4,8],[3,3,3],[0,6,6,0,0],[9,10,11,12])]
R_CASES=[[s,k] for s,k in (('()',1),('((',1),('))',1),('())(',1),('()()',1),('((()))',1),('((()))()()()',3),('((()))',2),('(((())))',2),('())(()',1),('((()))((()))',3),('(()())(()())',1))]

BATCH={
3698:entry('minimum_increasing_decreasing_split',[('nums','list[int]')],'int',['arrays','prefix sums'],['nums has two to 100,000 positive integers.','Both nonempty parts must preserve the original contiguous order.','The left part is strictly increasing and the right part strictly decreasing; return negative one if no split qualifies.'],[([[1,3,2]],'Splitting after three gives sums four and two, so the minimum difference is two.'),([[1,2,4,3]],'The two valid cuts both have absolute difference four.')],S_CASES,SPLIT,[SPLIT.replace('nums[index-1]<nums[index]','nums[index-1]<=nums[index]'),SPLIT.replace('nums[index]>nums[index+1]','nums[index]>=nums[index+1]')],['Accepts equal adjacent values in the increasing prefix.','Accepts equal adjacent values in the decreasing suffix.'],split_oracle,random_split,lesson('A cut is valid exactly when its entire prefix increases and its entire suffix decreases.','Precompute those two Boolean properties and scan all cuts while maintaining the left sum.','At every valid cut, compare the two sums and minimize their absolute difference.','The prefix and suffix flags certify every required adjacent comparison, and every possible nonempty split is inspected.'),'O(n)','O(n)',5),
3699:entry('count_zigzag_arrays',[('n','int'),('l','int'),('r','int')],'int',['dynamic programming','prefix sums'],['Three to 2,000 positions use values in the inclusive range left through right.','Adjacent values differ, and no three consecutive values are strictly monotone.','Return the count modulo 1,000,000,007.'],[([3,4,5],'Only 4,5,4 and 5,4,5 are valid.'),([3,1,3],'Ten length-three arrays satisfy the alternating-direction rule.')],Z1_CASES,ZIGZAG_ONE,[ZIGZAG_ONE.replace('new_up[index]=running;running=(running+down[index])','running=(running+down[index]);new_up[index]=running'),ZIGZAG_ONE.replace('return sum(up+down)%mod','return sum(up)%mod')],['Includes equal adjacent values in upward transitions.','Counts only arrays whose last comparison points upward.'],zigzag_oracle,random_zigzag_one,lesson('After the first comparison, validity means comparison directions must alternate.','Track counts ending at each value with the last move up or down.','Prefix sums of down states create new up states; suffix sums of up states create new down states.','Each transition chooses exactly the allowed opposite direction and excludes equality, so all and only ZigZag arrays are counted.'),'O(n(r-l+1))','O(r-l+1)',8),
3700:entry('count_large_zigzag_arrays',[('n','int'),('l','int'),('r','int')],'int',['dynamic programming','linear recurrences'],['Three to one billion positions use values in the inclusive range left through right.','The range contains at most 75 values; adjacent values differ and comparison directions alternate.','Return the count modulo 1,000,000,007.'],[([3,4,5],'Only 4,5,4 and 5,4,5 are valid.'),([3,1,3],'Ten length-three arrays satisfy the alternating-direction rule.')],Z2_CASES,ZIGZAG_TWO,[ZIGZAG_TWO.replace('if n<len(sequence):return sequence[n]','if n<len(sequence):return sequence[n-1]'),ZIGZAG_TWO.replace('if n<len(sequence):return sequence[n]','if n+1<len(sequence):return sequence[n+1]')],['Returns the preceding generated term for ordinary lengths.','Returns the following generated term for ordinary lengths.'],zigzag_oracle,random_zigzag_two,lesson('The small value range gives a finite linear transition even though n is enormous.','Generate enough exact terms, recover their modular linear recurrence with Berlekamp–Massey, then exponentiate that recurrence.','Prefix/suffix DP produces the training terms; polynomial binary exponentiation evaluates term n in logarithmic time.','The DP terms obey the fixed transition matrix, so their minimal recurrence remains valid for every later length.'),'O(m² log n + m²)','O(m²)',8),
3702:entry('longest_nonzero_xor_subsequence',[('nums','list[int]')],'int',['arrays','bit manipulation'],['nums contains one to 100,000 nonnegative integers.','Choose a subsequence whose bitwise XOR is nonzero.','Return its maximum length, or zero when none exists.'],[([[1,2,3]],'The full XOR is zero, but removing any nonzero value leaves a length-two valid subsequence.'),([[2,3,4]],'The XOR of all three values is five, so all elements can be kept.')],X_CASES,XOR,[XOR.replace('if total:return len(nums)','if total:return len(nums)-1'),XOR.replace('if all(value==0 for value in nums):return 0','if any(value==0 for value in nums):return 0')],['Drops an element even when the complete array already has nonzero XOR.','Treats the presence of any zero as proof that no solution exists.'],xor_oracle,random_xor,lesson('First test the XOR of the complete array.','If it is zero but some value is nonzero, removing that value makes the remaining XOR equal that nonzero value.','Return n for nonzero total XOR, zero for an all-zero array, and n-1 otherwise.','No length n answer exists when the total XOR is zero, while the removal argument always constructs the optimal length n-1 answer.'),'O(n)','O(1)',5),
3703:entry('remove_k_balanced_substrings',[('s','str'),('k','int')],'str',['strings','stacks','simulation'],['s has two to 100,000 parentheses and k is at most half its length.','Repeatedly remove every occurrence of exactly k opening parentheses followed by k closing parentheses.','Continue until no such substring remains and return the residual string.'],[(['(())',1],'Removing the inner pair creates another pair, so repeated removal leaves the empty string.'),(['(()(',1],'The middle pair is removed and the remaining string is ((.')],R_CASES,REMOVAL,[REMOVAL.replace("runs[-2][1]>=k","runs[-2][1]==k"),REMOVAL.replace("runs[-1][1]-=k","runs[-1][1]-=k-1")],['Fails when the opening run contains more than k parentheses.','Leaves one opening parenthesis behind after every removal.'],removal_oracle,random_removal,lesson('Only the final runs of equal parentheses can form a new removable block.','Compress the processed prefix into character/count runs and inspect the last two runs after each closing parenthesis.','When the closing run reaches k and the preceding opening run has at least k, delete both portions and discard empty runs.','All earlier runs were already stable; each deletion exposes precisely the new boundary that the same stack logic checks next.'),'O(n)','O(n)',6),
}
