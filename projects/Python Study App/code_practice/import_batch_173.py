"""String reduction, palindrome edits, punishment splits, batch decrements, and shopping batch 173."""

from collections import deque
from itertools import combinations,product

from .import_batch_055 import entry


def reduction_oracle(args):
    start=args[0];queue=deque([start]);seen={start};best=len(start)
    while queue:
        value=queue.popleft();best=min(best,len(value))
        for index in range(len(value)-1):
            if value[index:index+2] in ('AB','CD'):
                following=value[:index]+value[index+2:]
                if following not in seen:seen.add(following);queue.append(following)
    return best


def random_reduction(rng):return [''.join(rng.choice('ABCDXYZ') for _ in range(rng.randint(1,12)))]


def palindrome_oracle(args):
    s=args[0];pairs=len(s)//2;best=None
    choices=[tuple(sorted({s[index],s[-index-1]})) for index in range(pairs)]
    for selected in product(*choices):
        chars=list(s)
        for index,char in enumerate(selected):chars[index]=chars[-index-1]=char
        candidate=''.join(chars)
        changes=sum(a!=b for a,b in zip(s,candidate))
        key=(changes,candidate)
        if best is None or key<best:best=key
    return best[1]


def random_palindrome(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,7)))]


def punishment_oracle(args):
    def valid(number):
        digits=str(number*number);gaps=len(digits)-1
        for mask in range(1<<gaps):
            parts=[];start=0
            for gap in range(gaps):
                if mask>>gap&1:parts.append(int(digits[start:gap+1]));start=gap+1
            parts.append(int(digits[start:]))
            if sum(parts)==number:return True
        return False
    return sum(number*number for number in range(1,args[0]+1) if valid(number))


def random_punishment(rng):return [rng.randint(1,80)]


def nonpositive_oracle(args):
    nums,x,y=args;start=tuple(nums);queue=deque([(start,0)]);seen={start}
    while queue:
        values,distance=queue.popleft()
        if all(value<=0 for value in values):return distance
        for chosen in range(len(values)):
            following=tuple(value-(x if index==chosen else y) for index,value in enumerate(values))
            capped=tuple(max(-x,value) for value in following)
            if capped not in seen:seen.add(capped);queue.append((capped,distance+1))


def random_nonpositive(rng):
    y=rng.randint(1,4);x=rng.randint(y+1,y+5)
    return [[rng.randint(1,12) for _ in range(rng.randint(1,5))],x,y]


def chocolate_oracle(args):
    prices,money=args;first,second=sorted(prices)[:2];cost=first+second
    return money-cost if cost<=money else money


def random_chocolate(rng):return [[rng.randint(1,30) for _ in range(rng.randint(2,12))],rng.randint(1,60)]


REDUCTION="""\
def minimum_ab_cd_remainder(s):
    stack=[]
    for char in s:
        if stack and (stack[-1]+char in ('AB','CD')):stack.pop()
        else:stack.append(char)
    return len(stack)
"""

PALINDROME="""\
def smallest_minimum_edit_palindrome(s):
    chars=list(s);left=0;right=len(chars)-1
    while left<right:
        chars[left]=chars[right]=min(chars[left],chars[right]);left+=1;right-=1
    return ''.join(chars)
"""

PUNISHMENT="""\
def punishment_number_sum(n):
    def valid(digits,index,remaining):
        if index==len(digits):return remaining==0
        value=0
        for end in range(index,len(digits)):
            value=value*10+int(digits[end])
            if value>remaining:break
            if valid(digits,end+1,remaining-value):return True
        return False
    return sum(number*number for number in range(1,n+1) if valid(str(number*number),0,number))
"""

NONPOSITIVE="""\
def minimum_nonpositive_operations(nums,x,y):
    def possible(operations):
        extra=x-y;needed=0
        for value in nums:
            remaining=value-operations*y
            if remaining>0:needed+=(remaining+extra-1)//extra
        return needed<=operations
    low=0;high=(max(nums)+y-1)//y
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
"""

CHOCOLATE="""\
def money_after_two_chocolates(prices,money):
    first,second=sorted(prices)[:2];cost=first+second
    return money-cost if cost<=money else money
"""


BATCH={
2696:entry('minimum_ab_cd_remainder',[('s','str')],'int',['strings','stacks','simulation'],
 ['Repeatedly remove any contiguous occurrence of AB or CD.','Removals may expose new removable pairs.','Return the minimum possible remaining string length.'],
 [(['ABFCACDB'],'Removing AB and CD exposes another CD, leaving FB of length two.'),(['ACBBD'],'No AB or CD pair is present, so the full length five remains.')],
 [[s] for s in ['A','AB','CD','AC','ABCD','CDAB','AABB','CCDD','ABFCACDB','CABD','ACDB','ABCDBA','CDCDCD','AXBYCZ']],
 REDUCTION,[REDUCTION.replace("('AB','CD')","('BA','DC')"),REDUCTION.replace('stack.pop()','stack=[]')],
 ['Removes reversed pairs BA and DC instead of the specified pairs.','Clears the entire stack whenever one removable pair is found.'],reduction_oracle,random_reduction,
 ['Scan left to right with a stack representing the irreducible processed prefix.','When the top plus current character is AB or CD, pop it; otherwise push current.','A removal can interact only with the new boundary at the stack top, which the next step checks automatically.','Every removed pair is legal, and an irreducible stack contains no legal pair; local cancellation is confluent for these disjoint pair endings.'],'O(n)','O(n)',3),
2697:entry('smallest_minimum_edit_palindrome',[('s','str')],'str',['strings','greedy','two pointers'],
 ['Replace any character with another lowercase letter at cost one.','First minimize the number of replacements needed to make s a palindrome.','Among all minimum-edit palindromes, return the lexicographically smallest.'],
 [(['egcfe'],'The outer e pair stays; replacing g by f yields the minimum-edit palindrome efcfe.'),(['abcd'],'Both mismatched pairs require one edit, and choosing the smaller character in each produces abba.')],
 [[s] for s in ['a','aa','ab','ba','aba','abc','abcd','egcfe','racecar','leetcode','zzaz','azby','cbaabc','abcdefg']],
 PALINDROME,[PALINDROME.replace('min(chars[left],chars[right])','max(chars[left],chars[right])'),PALINDROME.replace('while left<right','while left+1<right')],
 ['Chooses the larger character in each mismatched pair, losing lexicographic minimality.','Stops before processing the innermost pair of an even-length string.'],palindrome_oracle,random_palindrome,
 ['Each mirrored pair can be handled independently.','Equal characters need no edit; unequal characters require exactly one edit in every palindrome.','For an unequal pair, replace the larger character with the smaller one.','This uses the forced minimum one edit per mismatch and makes the earliest differing position as small as possible, which gives the lexicographically least optimum.'],'O(n)','O(n)',3),
2698:entry('punishment_number_sum',[('n','int')],'int',['math','backtracking','recursion'],
 ['For each integer i from one through n, write the decimal digits of i squared.','i qualifies when those digits can be partitioned into contiguous nonempty pieces whose integer values sum to i.','Return the sum of i squared over all qualifying integers.'],
 [([10],'Qualifying values one, nine, and ten contribute 1 + 81 + 100 = 182.'),([37],'Additional qualifying value 36 has square 1296 split as 1+29+6, raising the sum to 1478.')],
 [[n] for n in [1,2,8,9,10,11,20,36,37,45,50,75,99,100]],
 PUNISHMENT,[PUNISHMENT.replace('remaining-value','remaining+value'),PUNISHMENT.replace('number*number','number',1)],
 ['Adds each chosen piece to the remaining target instead of subtracting it.','Tests the digits of i rather than i squared.'],punishment_oracle,random_punishment,
 ['For each square, recursively choose where its next decimal piece ends.','Carry the digit index and remaining sum required.','Stop successfully only when every digit is consumed and remaining equals zero; prune a piece exceeding remaining.','Every digit partition has one sequence of chosen endpoints, so exhaustive backtracking accepts exactly the qualifying squares.'],'O(n*2^digits)','O(digits)',5),
2702:entry('minimum_nonpositive_operations',[('nums','list[int]'),('x','int'),('y','int')],'int',['arrays','binary search'],
 ['Each operation chooses one index to decrease by x and decreases every other index by y, where x is greater than y.','Values may fall below zero.','Return the minimum operations required to make every array value non-positive.'],
 [([[3,4,1,7,6],4,2],'Three operations can assign the larger decrease where needed while baseline decreases handle the rest.'),([[1,2,1],2,1],'One operation targeting the value two makes every value non-positive.')],
 [[a,x,y] for a,x,y in [([1],2,1),([10],4,2),([1,2,1],2,1),([3,4,1,7,6],4,2),([5,5],3,1),([10,1,1],5,2),([2,8,2],6,1),([9,9,9],4,3),([1,1,1,1],10,1),([12,3,7],5,2),([6,10,14],7,3),([20,1],6,5),([4,8,12,16],9,2),([7,7,1,1],3,1)]],
 NONPOSITIVE,[NONPOSITIVE.replace('needed<=operations','needed<operations'),NONPOSITIVE.replace('remaining=value-operations*y','remaining=value-operations*x')],
 ['Requires fewer targeted decreases than available rather than allowing equality.','Applies the large decrease x to every index as the baseline.'],nonpositive_oracle,random_nonpositive,
 ['Binary-search the number of operations.','After t operations, every value receives t*y baseline decrease.','A still-positive value needs ceil(remaining/(x-y)) of the t chosen-index bonuses; sum these needs and compare with t.','The allocation is feasible exactly when total required choices fits the t operations, and feasibility remains true for every larger t.'],'O(n log M)','O(1)',8),
2706:entry('money_after_two_chocolates',[('prices','list[int]'),('money','int')],'int',['arrays','greedy','sorting'],
 ['Identify the two distinct chocolates with the lowest prices.','Buy both when their combined cost does not exceed money.','Return the remaining money after that purchase, or the original money when those two are unaffordable.'],
 [([[1,2,2],3],'Buying prices one and two spends all three dollars, leaving zero.'),([[3,2,3],3],'The two cheapest chocolates cost five, so no pair is affordable and all three dollars remain.')],
 [[p,m] for p,m in [([1,1],2),([1,2],2),([1,2],3),([5,5],10),([5,5],9),([1,2,2],3),([3,2,3],3),([10,1,5],6),([4,3,2,1],7),([8,2,6,4],5),([1,100,2],50),([7,7,1,1],2),([9,3,5,2],8),([20,10,30],100)]],
 CHOCOLATE,[CHOCOLATE.replace('sorted(prices)[:2]','sorted(prices)[-2:]'),CHOCOLATE.replace('cost<=money','cost<money')],
 ['Buys the two most expensive chocolates rather than the cheapest affordable pair.','Rejects a pair whose cost equals the available money.'],chocolate_oracle,random_chocolate,
 ['Find the two smallest prices.','If their sum exceeds money, every other pair also exceeds money.','Otherwise subtract exactly that sum from the available money.','The two order statistics uniquely determine the requested cheapest pair, and the affordability check handles both possible outcomes.'],'O(n log n)','O(n)',3),
}
