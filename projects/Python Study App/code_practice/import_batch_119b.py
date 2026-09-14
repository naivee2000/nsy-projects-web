"""Second reviewed group of workbook batch 119."""
from math import log10
from .import_batch_055 import entry

def product_o(a):
 left,right=a;value=1
 for x in range(left,right+1):value*=x
 zeros=0
 while value%10==0:zeros+=1;value//=10
 digits=str(value)
 return (digits if len(digits)<=10 else digits[:5]+'...'+digits[-5:])+f'e{zeros}'
def reversal_o(a):
 value=a[0]
 def rev(x):return int(str(x)[::-1])
 return rev(rev(value))==value
def instructions_o(a):
 n,start,s=a;moves={'L':(0,-1),'R':(0,1),'U':(-1,0),'D':(1,0)};answer=[]
 for begin in range(len(s)):
  row,col=start;done=0
  for char in s[begin:]:
   dr,dc=moves[char];row+=dr;col+=dc
   if not (0<=row<n and 0<=col<n):break
   done+=1
  answer.append(done)
 return answer
def distances_o(a):
 arr=a[0];return [sum(abs(i-j) for j,x in enumerate(arr) if x==value) for i,value in enumerate(arr)]
def order_o(a):return 'ba' not in a[0]
def rproduct(r):
 left=r.randint(1,30);return [left,r.randint(left,min(45,left+12))]
def rreversal(r):return [r.randint(0,10**8)]
def rinstructions(r):
 n=r.randint(1,7);return [n,[r.randrange(n),r.randrange(n)],''.join(r.choice('LRUD') for _ in range(r.randint(1,15)))]
def rdistances(r):return [[r.randint(0,6) for _ in range(r.randint(1,25))]]
def rorder(r):return [''.join(r.choice('ab') for _ in range(r.randint(1,30)))]

PRODUCT='''\
def abbreviate_range_product(left,right):
    from math import log10
    twos=fives=0;tail=1;log_sum=0.0
    for value in range(left,right+1):
        log_sum+=log10(value);x=value
        while x%2==0:twos+=1;x//=2
        while x%5==0:fives+=1;x//=5
        tail=tail*x%100000
    zeros=min(twos,fives);tail=tail*pow(2,twos-zeros,100000)*pow(5,fives-zeros,100000)%100000
    nonzero_log=log_sum-zeros;digits=int(nonzero_log)+1
    if digits<=10:
        value=1
        for x in range(left,right+1):value*=x
        value//=10**zeros
        return str(value)+'e'+str(zeros)
    leading=int(10**(nonzero_log-int(nonzero_log)+4))
    return str(leading)+'...'+str(tail).zfill(5)+'e'+str(zeros)
'''
REVERSAL='''\
def same_after_double_reversal(num):
    return num==0 or num%10!=0
'''
INSTRUCTIONS='''\
def executable_suffix_lengths(n,start_pos,s):
    moves={'L':(0,-1),'R':(0,1),'U':(-1,0),'D':(1,0)};answer=[]
    for begin in range(len(s)):
        row,column=start_pos;count=0
        for char in s[begin:]:
            dr,dc=moves[char];nr,nc=row+dr,column+dc
            if not (0<=nr<n and 0<=nc<n):break
            row,column=nr,nc;count+=1
        answer.append(count)
    return answer
'''
DISTANCES='''\
def identical_value_distances(arr):
    positions={}
    for index,value in enumerate(arr):positions.setdefault(value,[]).append(index)
    answer=[0]*len(arr)
    for group in positions.values():
        total=sum(group);left_sum=0;size=len(group)
        for rank,index in enumerate(group):
            answer[index]=index*rank-left_sum+(total-left_sum-index)-index*(size-rank-1)
            left_sum+=index
    return answer
'''
ORDER='''\
def all_a_before_b(s):
    return 'ba' not in s
'''
def L(*x):return list(x)
BATCH={
2117:entry('abbreviate_range_product',[('left','int'),('right','int')],'str',['math','number theory'],['left and right are positive with left at most right.','Multiply the inclusive range, remove all trailing zeros, and append e followed by the removed-zero count.','If the nonzero product exceeds ten digits, keep its first five and last five digits separated by ....'],[([1,4],'The product is twenty-four with no trailing zero, producing 24e0.'),([2,11],'The product has two trailing zeros; its nonzero part has seven digits, producing 399168e2.')],[[l,r] for l,r in [(1,1),(5,5),(10,10),(1,5),(1,10),(3,8),(10,20),(20,25),(25,30),(7,19),(15,27),(30,40),(2,20),(40,45)]],PRODUCT,[PRODUCT.replace('zeros=min(twos,fives)','zeros=max(twos,fives)'),PRODUCT.replace("str(tail).zfill(5)","str(tail)")],['Removes the larger prime-factor count rather than the number of complete ten factors.','Fails to zero-pad a short last-five-digit suffix in abbreviated output.'],product_o,rproduct,L('Trailing zeros come from matched factors of two and five; the rest can be tracked modulo 100000.','Accumulate factor counts, a factor-stripped suffix, and the base-ten logarithm of the full product.','Remove min(twos,fives), restore unmatched powers modulo 100000, and derive digit count and leading five from the adjusted logarithm.','Factor accounting gives the exact suffix and zero count, while logarithm integer/fractional parts determine total digits and leading digits without constructing the huge product.'),'O(right-left+1 times log right)','O(1)',8),
2119:entry('same_after_double_reversal',[('num','int')],'bool',['math','digits'],['num is a nonnegative integer.','Decimal reversal discards leading zeros in the reversed representation.','Return whether reversing num twice recovers num.'],[([526],'Neither reversal loses a significant zero, so the original number is recovered.'),([1800],'The first reversal drops two zeros, so the second reversal cannot restore 1800.')],[[x] for x in [0,1,10,100,101,120,1000,1001,999,90,9090,123456,50005,7000001]],REVERSAL,[REVERSAL.replace('num==0 or','num==0 and'),REVERSAL.replace('num%10!=0','num%10==0')],['Requires both zero and a nonzero last digit, rejecting every input.','Accepts exactly the positive numbers ending in zero, reversing the condition.'],reversal_o,rreversal,L('Only zeros at the end of the original can be lost as leading zeros after the first reversal.','Zero itself is unchanged; every positive number must have a nonzero last digit.','Return num==0 or num%10!=0.','A nonzero final digit becomes a nonzero leading digit and survives both reversals; a trailing zero is irrecoverably discarded.'),'O(1)','O(1)',3),
2120:entry('executable_suffix_lengths',[('n','int'),('start_pos','list[int]'),('s','str')],'list[int]',['grids','strings','simulation'],['The grid is n by n and start_pos is valid.','For each suffix s[i:], reset to start_pos and execute until the next move would leave the grid.','Return the number of successfully executed instructions for every suffix.'],[([3,[0,1],'RRDDLU'],'The six suffixes permit 1,5,4,3,1,0 moves respectively.'),([2,[1,1],'LURD'],'Resetting for each suffix yields lengths four, one, zero, zero.')],[[n,p,s] for n,p,s in [(1,[0,0],'L'),(1,[0,0],'UD'),(2,[0,0],'R'),(2,[0,0],'D'),(2,[0,0],'L'),(2,[1,1],'U'),(3,[1,1],'LRUD'),(3,[0,0],'RRDD'),(3,[2,2],'LLUU'),(4,[1,2],'RDLU'),(2,[0,1],'DDLL'),(5,[2,2],'UUU'),(3,[1,0],'RRR'),(4,[3,0],'URRDLL')]],INSTRUCTIONS,[INSTRUCTIONS.replace('row,column=start_pos','row,column=0,0'),INSTRUCTIONS.replace('answer.append(count)','answer.append(count+1)')],['Starts every suffix at the grid origin instead of start_pos.','Counts the first invalid instruction as successfully executed.'],instructions_o,rinstructions,L('Every suffix is an independent simulation from the same initial cell.','For each starting instruction, apply moves until the proposed next cell is out of bounds.','Reset row,column; increment count only after a valid move; append count when stopped or exhausted.','The loop follows precisely the suffix prefix that stays inside, so its count is the requested maximum executable length.'),'O(len(s)^2)','O(output)',5),
2121:entry('identical_value_distances',[('arr','list[int]')],'list[int]',['arrays','prefix sums','hash maps'],['For each index, sum its absolute distance to every other index holding the same value.','The element at the index contributes zero and duplicates are handled independently.','Return one distance sum per original index.'],[([[2,1,3,1,2,3,3]],'The equal-value index groups produce [4,2,7,2,4,4,5].'),([[10,5,10,10]],'Indices zero, two, and three holding ten have sums five, three, and four.')],[[x] for x in [[1],[1,1],[1,2],[1,2,1],[1,1,1],[2,1,3,1,2,3,3],[0,1,0,1],[5,5,6,5],[1,2,3,4],[-1,-1,0,-1],[7,8,7,8,7],[2,2,1,2,1],[9,0,9,0,9,0],[3,1,3,3,1,3]]],DISTANCES,[DISTANCES.replace('index*rank-left_sum','index*(rank+1)-left_sum'),DISTANCES.replace('size-rank-1','size-rank')],['Counts the current index once on the left side.','Counts the current index once on the right side.'],distances_o,rdistances,L('Within each value group, sorted indices let left and right absolute differences be computed from sums.','Group positions, then sweep each group while maintaining the sum of earlier indices and the total sum.','Left contribution=i*rank-left_sum; right=(total-left_sum-i)-i*(size-rank-1).','All earlier indices are at most i and later indices at least i, so removing absolute values yields exactly these two formulas.'),'O(n)','O(n)',5),
2124:entry('all_a_before_b',[('s','str')],'bool',['strings','state tracking'],['s is nonempty and contains only a and b.','Return true exactly when no a appears after any b.','Strings containing only one character type satisfy the condition.'],[(['aaabbb'],'All a characters occur before the first b.'),(['abab'],'The a at index two occurs after a b, so the condition fails.')],[[s] for s in ['a','b','ab','ba','aa','bb','aab','abb','bba','aba','aaaaab','abbbbb','baaab','aabbaabb']],ORDER,[ORDER.replace("'ba' not in s","'ab' not in s"),ORDER.replace('not in','in')],['Checks for the opposite adjacent transition and rejects valid ordered strings.','Returns true when a forbidden ba transition exists.'],order_o,rorder,L('Once a b has appeared, any later a creates an adjacent ba boundary somewhere in the string.','The condition is equivalent to forbidding substring ba.','Return "ba" not in s.','If an a follows any b, the transition from the last preceding b-run to that a contains ba; conversely ba directly violates the order.'),'O(n)','O(1)',3)
}
BATCH[2117]['wrong'][0]=PRODUCT.replace('zeros=min(twos,fives)','zeros=0')
BATCH[2117]['wrong_reasons'][0]='Never removes or reports trailing zeros from the product.'
BATCH[2117]['boundaries'][-1]=[1,18]
