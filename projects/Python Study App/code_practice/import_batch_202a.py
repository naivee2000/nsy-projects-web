"""Backtracking, linked insertion sort, peak search, digit counting, and digit DFS."""
from itertools import product
from .import_batch_055 import entry,EXTRA_BOUNDARIES

EXTRA_BOUNDARIES['generate_parentheses']=[[n] for n in range(9,15)]
EXTRA_BOUNDARIES['count_unique_digit_numbers']=[[n] for n in range(9,14)]

def paren_oracle(a):
    n=a[0];return [''.join(x) for x in product('()',repeat=2*n) if all(''.join(x)[:i].count('(')>=''.join(x)[:i].count(')') for i in range(1,2*n+1)) and x.count('(')==n]
def random_paren(r):return [r.randint(1,7)]
def linked_oracle(a):return sorted(a[0])
def random_linked(r):return [[r.randint(-100,100) for _ in range(r.randint(0,40))]]
def peak_oracle(a):
    nums=a[0];return next(i for i,x in enumerate(nums) if (i==0 or x>nums[i-1]) and (i==len(nums)-1 or x>nums[i+1]))
def random_peak(r):
    nums=[r.randint(-100,100)]
    for _ in range(r.randint(0,40)):
        value=r.randint(-100,100)
        while value==nums[-1]:value=r.randint(-100,100)
        nums.append(value)
    return [nums]
def unique_oracle(a):
    n=a[0]
    if n<=5:return sum(len(set(str(x)))==len(str(x)) for x in range(10**n))
    answer=10;ways=9;available=9
    for length in range(2,min(n,10)+1):ways*=available;answer+=ways;available-=1
    return answer
def random_unique(r):return [r.randint(0,13)]
def digits_oracle(a):
    n,k=a;low=10**(n-1);high=10**n
    return [x for x in range(low,high) if all(abs(int(p)-int(q))==k for p,q in zip(str(x),str(x)[1:]))]
def random_digits(r):return [r.randint(2,4),r.randint(0,9)]

PAREN='''def generate_parentheses(n):
    answer=[]
    def visit(opened,closed,text):
        if len(text)==2*n:answer.append(text);return
        if opened<n:visit(opened+1,closed,text+'(')
        if closed<opened:visit(opened,closed+1,text+')')
    visit(0,0,'');return answer
'''
LINKED='''def insertion_sort_linked_list(head):
    dummy=ListNode(float('-inf'));current=head
    while current:
        following=current.next;place=dummy
        while place.next and place.next.val<=current.val:place=place.next
        current.next=place.next;place.next=current;current=following
    return dummy.next
'''
PEAK='''def find_peak_index(nums):
    left,right=0,len(nums)-1
    while left<right:
        middle=(left+right)//2
        if nums[middle]>nums[middle+1]:right=middle
        else:left=middle+1
    return left
'''
UNIQUE='''def count_unique_digit_numbers(n):
    if n==0:return 1
    answer=10;ways=9;available=9
    for length in range(2,min(n,10)+1):ways*=available;answer+=ways;available-=1
    return answer
'''
DIGITS='''def numbers_with_consecutive_difference(n,k):
    answer=[]
    def visit(value,length):
        if length==n:answer.append(value);return
        last=value%10
        for digit in {last+k,last-k}:
            if 0<=digit<=9:visit(value*10+digit,length+1)
    for first in range(1,10):visit(first,1)
    return answer
'''

BATCH={
22:entry('generate_parentheses',[('n','int')],'list[str]',['recursion','backtracking'],['1<=n<=8.','Return every balanced string containing exactly n opening and n closing parentheses.','Output order does not matter and duplicates are forbidden.'],[([3],'The five balanced arrangements of three pairs are returned.'),([1],'One pair has only the string ().')],[[n] for n in [1,2,3,4,5,6,7,8,2,3,4,5]],PAREN,[PAREN.replace('closed<opened','closed<=opened'),PAREN.replace('opened<n','opened<n-1')],['May place a closing parenthesis before a matching opener.','Allows only n-1 opening parentheses.'],paren_oracle,random_paren,['A prefix can never contain more closing than opening parentheses.','Track counts and branch only when an opener remains or a closer is currently legal.','Append at length 2n.','Each valid string follows one unique sequence of legal choices, so the search is complete without duplicates.'],'O(Catalan(n)*n)','O(n)',5),
147:entry('insertion_sort_linked_list',[('head','ListNode | None')],'ListNode | None',['linked lists','sorting'],['The linked list may be empty and contains integer values.','Sort nodes in nondecreasing order with insertion-sort logic.','Return the sorted head.'],[([[4,2,1,3]],'Inserting each node into the ordered prefix produces 1,2,3,4.'),([[-1,5,3,4,0]],'Negative and positive values become -1,0,3,4,5.')],[[x] for x in [[],[1],[2,1],[1,2],[4,2,1,3],[-1,5,3,4,0],[2,2],[3,1,2,1],[5,4,3,2,1],[0,-1,1],[1,3,2,4],[9,7,8,6],[1,1,1],[10,-10,0]]],LINKED,[LINKED.replace('<=current.val','<current.val'),LINKED.replace("float('-inf')","float('inf')")],['Inserts equal values before rather than after their existing run, breaking stable insertion behavior.','Uses a positive-infinity sentinel and inserts every node before it incorrectly.'],linked_oracle,random_linked,['Maintain a dummy-headed sorted output list.','Detach each input node, find its insertion predecessor, and splice it there.','Advance through the original chain using a saved next pointer.','The output prefix stays sorted after every insertion and eventually contains every input value.'],'O(n^2)','O(1)',5),
162:entry('find_peak_index',[('nums','list[int]')],'int',['arrays','binary search'],['nums is nonempty and adjacent values differ.','Return any index strictly greater than both existing neighbors; outside values are negative infinity.','Use logarithmic time.'],[([[1,2,3,1]],'Index two contains three, which exceeds both neighbors.'),([[1]],'The only element is a peak against two outside negative infinities.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3,1],[1,2,1,3,5,6,4],[3,2,1],[1,3,2],[2,1,3],[0,-1],[-2,-1,-3],[5,1,4,2],[1,4,3,2],[2,4,1,3,0],[10,20,10,30,5]]],PEAK,[PEAK.replace('>nums[middle+1]','<nums[middle+1]'),PEAK.replace('right=middle','right=middle-1')],['Moves toward a descending side instead of the guaranteed rising-side peak.','Skips the midpoint when the peak may be there.'],peak_oracle,random_peak,['A rising slope guarantees some peak to its right; a falling slope guarantees one at or left of the midpoint.','Binary-search using nums[mid] versus nums[mid+1].','Keep mid on a falling slope and mid+1 on a rising slope.','The retained interval always contains a peak and shrinks to one valid index.'],'O(log n)','O(1)',5),
357:entry('count_unique_digit_numbers',[('n','int')],'int',['math','dynamic programming'],['0<=n<=8.','Count integers x with 0<=x<10^n whose decimal digits are all distinct.','Leading zeros are not written as digits.'],[([2],'There are 91 valid values from zero through 99.'),([0],'The range contains only zero, so return one.')],[[n] for n in [0,1,2,3,4,5,6,7,8,2,3,4,5,6]],UNIQUE,[UNIQUE.replace('answer=10','answer=9'),UNIQUE.replace('choices-=1','choices-=2')],['Omits zero from the one-digit base count.','Removes two available digits per position instead of one.'],unique_oracle,random_unique,['Count by written digit length.','For length at least two, choose nine nonzero first digits, then 9,8,7... remaining digits.','Add these products to the ten one-digit values.','Every unique-digit number has exactly one length and one ordered selection of distinct digits.'],'O(n)','O(1)',5),
967:entry('numbers_with_consecutive_difference',[('n','int'),('k','int')],'list[int]',['recursion','backtracking'],['2<=n<=9 and 0<=k<=9.','Return all n-digit integers with no leading zero whose adjacent decimal digits differ by exactly k.','Order does not matter and duplicates are forbidden.'],[([3,7],'The valid results are 181, 292, 707, 818, and 929.'),([2,0],'The valid results repeat one nonzero digit: 11 through 99.')],[[n,k] for n,k in [(2,0),(2,1),(2,9),(3,7),(3,0),(3,1),(3,5),(4,2),(4,8),(5,3),(2,4),(3,9),(4,0),(5,1)]],DIGITS,[DIGITS.replace("{last+k,last-k}","[last+k,last-k]"),DIGITS.replace('range(1,10)','range(10)')],['Duplicates every branch when k is zero.','Allows a leading zero and returns shorter integers.'],digits_oracle,random_digits,['Build numbers from a nonzero leading digit.','At each step only last+k and last-k can be legal next digits; use a set to merge them when k=0.','Append after exactly n digits.','The recursion explores every locally required next digit and no other value.'],'O(output*n)','O(n)',5),
}
BATCH[22]['comparator']='unordered'
BATCH[147]['params'][0]=('head','ListNode | None','listnode');BATCH[147]['adapter']='listnode'
BATCH[147]['node_policy']='values'
BATCH[147]['wrong']=[LINKED.replace('return dummy.next','return dummy.next.next'),LINKED.replace('following=current.next','following=current.next.next if current.next else None')]
BATCH[147]['wrong_reasons']=['Drops the smallest node from the returned chain.','Skips every second input node while scanning.']
BATCH[967]['comparator']='unordered'
BATCH.pop(22)
BATCH[357]['constraints'][0]='0<=n<=13; counts saturate after ten written digits because no decimal digit may repeat.'
BATCH[357]['wrong']=[UNIQUE.replace('answer=10','answer=9'),UNIQUE.replace('available-=1','available-=2')]
BATCH[357]['wrong_reasons']=['Omits zero from the one-digit base count.','Removes two available digits per added position.']
EXTRA_BOUNDARIES.pop('generate_parentheses');EXTRA_BOUNDARIES.pop('count_unique_digit_numbers')
