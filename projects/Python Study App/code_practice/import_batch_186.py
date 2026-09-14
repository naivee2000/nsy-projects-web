"""Stepping ranges, lucky numbers, rounded balances, GCD list insertion, and circular spreading batch 186."""
from math import gcd
from .import_batch_055 import entry
def stepping_oracle(a):
 low,high=a
 return sum(all(abs(int(x)-int(y))==1 for x,y in zip(str(n),str(n)[1:])) for n in range(int(low),int(high)+1))%1_000_000_007
def random_stepping(r):
 low=r.randint(1,4000);return [str(low),str(r.randint(low,5000))]
def lucky_oracle(a):
 k=a[0];values=[];level=['4','7']
 while len(values)<k:values+=level;level=[x+c for x in level for c in '47']
 return values[k-1]
def random_lucky(r):return [r.randint(1,1000)]
def balance_oracle(a):
 amount=a[0];choices=range(0,101,10);rounded=min(choices,key=lambda x:(abs(x-amount),-x));return 100-rounded
def random_balance(r):return [r.randint(0,100)]
def gcd_list_oracle(a):
 values=a[0];out=[]
 for i,v in enumerate(values):
  out.append(v)
  if i+1<len(values):out.append(gcd(v,values[i+1]))
 return out
def random_gcd_list(r):return [[r.randint(1,100) for _ in range(r.randint(1,20))]]
def seconds_oracle(a):
 nums=a[0];n=len(nums);answer=n
 for target in set(nums):
  sources=[i for i,v in enumerate(nums) if v==target]
  distance=0
  for i in range(n):distance=max(distance,min(min((i-j)%n,(j-i)%n) for j in sources))
  answer=min(answer,distance)
 return answer
def random_seconds(r):return [[r.randint(1,6) for _ in range(r.randint(1,30))]]
STEPPING='''\
def count_stepping_numbers(low,high):
    MOD=1_000_000_007
    def count(bound):
        if bound<0:return 0
        digits=list(map(int,str(bound)));memo={}
        def visit(index,previous,started,tight):
            if index==len(digits):return int(started)
            key=(index,previous,started,tight)
            if key in memo:return memo[key]
            limit=digits[index] if tight else 9;answer=0
            for digit in range(limit+1):
                new_tight=tight and digit==limit
                if not started and digit==0:answer+=visit(index+1,10,False,new_tight)
                elif not started or abs(digit-previous)==1:answer+=visit(index+1,digit,True,new_tight)
            memo[key]=answer%MOD;return memo[key]
        return visit(0,10,False,True)
    return (count(int(high))-count(int(low)-1))%MOD
'''
LUCKY='''\
def kth_lucky_number(k):
    bits=bin(k+1)[3:]
    return ''.join('7' if bit=='1' else '4' for bit in bits)
'''
BALANCE='''\
def balance_after_rounded_purchase(purchaseAmount):
    rounded=((purchaseAmount+5)//10)*10
    return 100-rounded
'''
GCD_LIST='''\
def insert_gcd_nodes(head):
    node=head
    while node and node.next:
        following=node.next;node.next=ListNode(__import__('math').gcd(node.val,following.val),following);node=following
    return head
'''
SECONDS='''\
def minimum_circular_equalization_seconds(nums):
    positions={};n=len(nums)
    for index,value in enumerate(nums):positions.setdefault(value,[]).append(index)
    answer=n
    for indexes in positions.values():
        largest=max(right-left for left,right in zip(indexes,indexes[1:]+[indexes[0]+n]))
        answer=min(answer,largest//2)
    return answer
'''
BATCH={
2801:entry('count_stepping_numbers',[('low','str'),('high','str')],'int',['strings','dynamic programming','digit DP'],['A positive integer is stepping when every adjacent decimal digit differs by exactly one.','Count stepping numbers in the inclusive range low through high.','Return the count modulo 1,000,000,007.'],[(['1','11'],'The values one through nine plus ten are stepping, giving ten.'),(['90','101'],'Only 98 and 101 qualify in this range.')],[[a,b] for a,b in [('1','1'),('1','11'),('10','10'),('11','11'),('12','12'),('90','101'),('100','200'),('1','9'),('20','30'),('98','123'),('500','600'),('1000','1200'),('321','456'),('1','1000')]],STEPPING,[STEPPING.replace('==1','<=1'),STEPPING.replace('count(int(low)-1)','count(int(low))')],['Allows equal adjacent digits as stepping.','Subtracts through low itself and incorrectly excludes an inclusive endpoint.'],stepping_oracle,random_stepping,['Count valid numbers no greater than one bound with digit DP.','State stores digit position, previous chosen digit, whether a nonleading digit has started, and tightness.','Allow a new significant digit only when its distance from the previous digit is one; subtract count(low-1) from count(high).','Every bounded representation follows one DP path, and the transition enforces the stepping condition at each adjacent significant digit.'],'O(digits*11*2*2*10)','O(digits*11)',8),
2802:entry('kth_lucky_number',[('k','int')],'str',['math','bit manipulation','strings'],['Lucky numbers contain only digits four and seven.','Order them first by numeric value: 4,7,44,47,74,77,444,...','Return the k-th lucky number as a string using one-based k.'],[([4],'The fourth sequence entry is 47.'),([1],'The first lucky number is 4.')],[[k] for k in [1,2,3,4,5,6,7,8,10,15,16,31,32,100]],LUCKY,[LUCKY.replace('k+1','k'),LUCKY.replace("'7' if bit=='1' else '4'","'4' if bit=='1' else '7'")],['Uses k directly and therefore loses the complete binary-tree level offset.','Maps binary one to four and zero to seven, reversing the within-level order.'],lucky_oracle,random_lucky,['Lucky strings form breadth-first nodes of a binary tree, appending four then seven.','The binary form of k+1 has a leading level marker; discard it.','Map each remaining zero to four and one to seven.','Binary counting lists fixed-length bit strings in the same order as lucky digits, while k+1 accounts for all shorter levels.'],'O(log k)','O(log k)',5),
2806:entry('balance_after_rounded_purchase',[('purchaseAmount','int')],'int',['math'],['Round purchaseAmount to the nearest multiple of ten; when equally close, round upward.','Begin with an account balance of one hundred.','Return the balance after subtracting the rounded purchase.'],[([9],'Nine rounds to ten, leaving ninety.'),([15],'The tie between ten and twenty rounds upward to twenty, leaving eighty.')],[[x] for x in [0,1,4,5,9,10,14,15,19,20,44,45,99,100]],BALANCE,[BALANCE.replace('+5','+4'),BALANCE.replace('*10','')],['Rounds a five-ending tie downward.','Forgets to restore the tens place after integer division.'],balance_oracle,random_balance,['Adding five before integer division implements nearest-ten rounding with upward ties.','Compute ((amount+5)//10)*10.','Subtract that rounded value from one hundred.','The five-unit shift places every rounding boundary at an integer quotient boundary, including the specified tie direction.'],'O(1)','O(1)',3),
2807:entry('insert_gcd_nodes',[('head','ListNode | None')],'ListNode | None',['linked lists','math','simulation'],['Between every adjacent pair of original linked-list nodes, insert a new node containing their greatest common divisor.','Preserve the original node order and do not insert after the final node.','Return the head of the modified list.'],[([[18,6,10,3]],'The inserted gcd values are six, two, and one, producing [18,6,6,2,10,1,3].'),([[7]],'A one-node list has no adjacent pair and remains unchanged.')],[[x] for x in [[1],[7],[2,4],[18,6,10,3],[5,10,15],[7,11],[12,18,24],[1,1,1],[100,25],[8,4,2,1],[9,6,3],[14,21,35],[6,10,15,25],[2,3,5,7]]],GCD_LIST,[GCD_LIST.replace("__import__('math').gcd(node.val,following.val)",'node.val+following.val'),GCD_LIST.replace(',following)',',None)')],['Inserts the adjacent sum instead of their greatest common divisor.','Fails to connect each inserted node to the following original suffix.'],gcd_list_oracle,random_gcd_list,['Save the next original node before inserting anything.','Create a node holding gcd(current.val,next.val) between current and next.','Advance to the saved original next node, not the inserted node.','Each loop processes exactly one original edge and replaces it by current→gcd→next without disturbing later edges.'],'O(n log M)','O(1)',5),
2808:entry('minimum_circular_equalization_seconds',[('nums','list[int]')],'int',['arrays','hash maps','circular arrays'],['Each second, every circular-array position may keep its value or copy either neighbor’s value, simultaneously.','Return the minimum seconds needed to make all positions equal.','The final common value must be one already present initially.'],[([[1,2,1,2]],'Either value spreads one step to cover the alternating circle, so one second is enough.'),([[1,2,3,1]],'Value one reaches both middle positions in one second.')],[[x] for x in [[1],[1,1],[1,2],[1,2,1,2],[1,2,3,1],[1,2,3],[1,1,2,2],[1,2,2,2,1],[5,1,5,1,5],[1,2,3,4,1],[7,7,7],[3,1,2,3,2,1],[1,1,1,2],[4,2,4,3,4,1]]],SECONDS,[SECONDS.replace('largest//2','(largest+1)//2'),SECONDS.replace('indexes[1:]+[indexes[0]+n]','indexes[1:]+indexes[:1]')],['Rounds an odd circular gap upward even though sources spread from both ends simultaneously.','Treats the final occurrence-to-first-occurrence gap as zero instead of wrapping across the array boundary.'],seconds_oracle,random_seconds,['Consider each distinct initial value as the final target.','Its occurrences spread outward simultaneously; the slowest region is the largest circular gap between consecutive sources.','Append the first index plus n to represent the wraparound occurrence, then halve the largest gap.','Every position adopts the target from its nearest source, and the midpoint of the largest source gap is exactly the last position reached.'],'O(n)','O(n)',5),
}
BATCH[2807]['params'][0]=('head','ListNode | None','listnode');BATCH[2807]['adapter']='listnode'
