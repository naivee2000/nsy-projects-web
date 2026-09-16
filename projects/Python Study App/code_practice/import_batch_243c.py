"""Greedy, monotonic-stack, sliding-window, and linked-number problems."""
from collections import Counter
from functools import lru_cache
from itertools import combinations_with_replacement
from .import_batch_055 import entry

MOD=1_000_000_007

def split_oracle(args):
    nums,m=args;prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    @lru_cache(None)
    def possible(left,right):
        if left==right:return True
        for cut in range(left,right):
            left_ok=cut==left or prefix[cut+1]-prefix[left]>=m
            right_ok=cut==right-1 or prefix[right+1]-prefix[cut+1]>=m
            if left_ok and right_ok and possible(left,cut) and possible(cut+1,right):return True
        return False
    return possible(0,len(nums)-1)
def random_split(rng):return [[rng.randint(1,10) for _ in range(rng.randint(1,9))],rng.randint(1,20)]

def double_oracle(args):return list(map(int,str(2*int(''.join(map(str,args[0]))))))
def random_double(rng):
    length=rng.randint(1,35);return [[rng.randint(1,9)]+[rng.randint(0,9) for _ in range(length-1)]]

def beautiful_oracle(args):
    n,target=args;chosen=[];value=1
    while len(chosen)<n:
        if all(value+other!=target for other in chosen):chosen.append(value)
        value+=1
    return sum(chosen)%MOD
def random_beautiful(rng):return [rng.randint(1,12),rng.randint(1,25)]

def digit_product_oracle(args):
    n=args[0]
    if n==1:return '1'
    best=None
    for length in range(1,9):
        for digits in combinations_with_replacement(range(2,10),length):
            product=1
            for digit in digits:product*=digit
            if product==n:
                candidate=''.join(map(str,digits))
                if best is None or (len(candidate),candidate)<(len(best),best):best=candidate
        if best is not None:return best
    return '-1'
def random_digit_product(rng):
    if rng.random()<.7:
        product=1
        for _ in range(rng.randint(0,5)):product*=rng.randint(2,9)
        return [product]
    return [rng.randint(1,1000)]

def towers_oracle(args):
    maximum=args[0];best=0
    for peak in range(len(maximum)):
        values=[0]*len(maximum);values[peak]=maximum[peak]
        for i in range(peak-1,-1,-1):values[i]=min(maximum[i],values[i+1])
        for i in range(peak+1,len(maximum)):values[i]=min(maximum[i],values[i-1])
        best=max(best,sum(values))
    return best
def random_towers(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,18))]]

def groups_oracle(args):
    counts=list(Counter(args[0]).values())
    for groups in range(1,sum(counts)+1):
        for small in range(1,max(counts)+1):
            large=small+1
            @lru_cache(None)
            def ways(index,remaining):
                if index==len(counts):return remaining==0
                count=counts[index]
                return any(ways(index+1,remaining-parts) for parts in range(1,remaining+1)
                           if parts*small<=count<=parts*large)
            if ways(0,groups):return groups
def random_groups(rng):return [[rng.randint(1,8) for _ in range(rng.randint(1,25))]]

def xor_oracle(args):
    a,b,n=args;return max((a^x)*(b^x) for x in range(1<<n))%MOD
def random_xor(rng):return [rng.randint(0,1000),rng.randint(0,1000),rng.randint(0,9)]

def power_oracle(args):
    nums,k=args;answer=[]
    for left in range(len(nums)-k+1):
        window=nums[left:left+k]
        answer.append(window[-1] if all(b==a+1 for a,b in zip(window,window[1:])) else -1)
    return answer
def random_power(rng):
    nums=[rng.randint(1,20) for _ in range(rng.randint(1,30))]
    return [nums,rng.randint(1,len(nums))]

def consecutive_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        total=0
        for right in range(left,len(nums)):
            total+=nums[right]
            if right==left or all(abs(nums[i]-nums[i-1])==1 and nums[i]-nums[i-1]==nums[left+1]-nums[left]
                                  for i in range(left+1,right+1)):answer+=total
    return answer%MOD
def random_consecutive(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,15))]]

def valid_substrings_oracle(args):
    first,second=args;need=Counter(second);answer=0
    for left in range(len(first)):
        have=Counter()
        for right in range(left,len(first)):
            have[first[right]]+=1
            if all(have[c]>=count for c,count in need.items()):answer+=1
    return answer
def random_valid_substrings(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,18))),''.join(rng.choice('abcd') for _ in range(rng.randint(1,8)))]

SPLIT='''def can_split_array(nums,m):
    return len(nums)<=2 or any(a+b>=m for a,b in zip(nums,nums[1:]))
'''
DOUBLE='''def double_linked_number(head):
    def visit(node):
        if node is None:return 0
        carry=visit(node.next);value=node.val*2+carry;node.val=value%10;return value//10
    carry=visit(head)
    return ListNode(carry,head) if carry else head
'''
BEAUTIFUL='''def minimum_beautiful_array_sum(n,target):
    modulus=1_000_000_007;first=min(n,target//2);remaining=n-first
    return (first*(first+1)//2+remaining*(2*target+remaining-1)//2)%modulus
'''
DIGITS='''def smallest_digit_product(n):
    digits=[]
    for digit in range(9,1,-1):
        while n%digit==0:digits.append(str(digit));n//=digit
    if n>1:return '-1'
    return ''.join(reversed(digits)) or '1'
'''
TOWERS='''def maximum_mountain_sum(max_heights):
    n=len(max_heights);left=[0]*n;stack=[]
    for i,value in enumerate(max_heights):
        while stack and max_heights[stack[-1]]>value:stack.pop()
        previous=stack[-1] if stack else -1
        left[i]=(left[previous] if previous>=0 else 0)+value*(i-previous);stack.append(i)
    right=[0]*n;stack=[]
    for i in range(n-1,-1,-1):
        value=max_heights[i]
        while stack and max_heights[stack[-1]]>=value:stack.pop()
        following=stack[-1] if stack else n
        right[i]=(right[following] if following<n else 0)+value*(following-i);stack.append(i)
    return max(left[i]+right[i]-max_heights[i] for i in range(n))
'''
GROUPS='''def minimum_valid_assignment_groups(nums):
    from collections import Counter
    counts=Counter(nums)
    for size in range(min(counts.values()),0,-1):
        total=0
        for count in counts.values():
            if count//size<count%size:break
            total+=(count+size)//(size+1)
        else:return total
'''
XOR='''def maximum_xor_product(a,b,n):
    modulus=1_000_000_007;first=(a>>n)<<n;second=(b>>n)<<n
    for bit in range(n-1,-1,-1):
        left=a>>bit&1;right=b>>bit&1
        if left==right:first|=1<<bit;second|=1<<bit
        elif first>second:second|=1<<bit
        else:first|=1<<bit
    return first*second%modulus
'''
POWER='''def k_subarray_powers(nums,k):
    run=1;answer=[]
    for index,value in enumerate(nums):
        if index and value==nums[index-1]+1:run+=1
        else:run=1
        if index>=k-1:answer.append(value if run>=k else -1)
    return answer
'''
CONSECUTIVE='''def sum_consecutive_subarrays(nums):
    modulus=1_000_000_007;answer=0;up_count=down_count=0;up_sum=down_sum=0
    for index,value in enumerate(nums):
        if index and value==nums[index-1]+1:up_count+=1;up_sum+=up_count*value
        else:up_count=1;up_sum=value
        if index and value==nums[index-1]-1:down_count+=1;down_sum+=down_count*value
        else:down_count=1;down_sum=value
        answer+=up_sum+down_sum-value
    return answer%modulus
'''
VALID='''def count_rearrangeable_substrings(word1,word2):
    from collections import Counter
    need=Counter(word2);missing=len(need);window=Counter();left=0;answer=0
    for char in word1:
        window[char]+=1
        if window[char]==need[char]:missing-=1
        while missing==0:
            outgoing=word1[left]
            if window[outgoing]==need[outgoing]:missing+=1
            window[outgoing]-=1;left+=1
        answer+=left
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

CASES={
2811:[[a,m] for a,m in [([2,2,1],4),([2,1,3],5),([1],10),([1,1],5),([1,1,1],2),([1,1,1],3),([5,1,1],6),([3,3,3],7),([10,1,1,1],10),([1,9,1],10),([2,3,1,2],5),([1,2,1,2],4),([4,1,4],8),([2,8,2,1],10)]],
2816:[[x] for x in ([1,8,9],[9,9,9],[1],[5],[4,5],[5,0],[1,0,0],[7,6,5],[2,5,0],[9,0,1],[3,3,3,3],[1,2,3,4,5],[8,8],[1,0,1,0])],
2834:[[n,t] for n,t in [(2,3),(3,3),(1,1),(1,10),(3,10),(5,4),(5,10),(10,1),(4,7),(8,12),(20,30),(7,2),(6,9),(12,15)]],
2847:[[n] for n in (105,7,1,2,10,12,13,36,100,256,17,72,48,999)],
2866:[[x] for x in ([5,3,4,1,1],[6,5,3,9,2,7],[3,2,5,5,2,3],[1],[1,2],[2,1],[3,3,3],[1,2,3,4],[4,3,2,1],[2,5,2],[10,1,10],[2,2,1,2,2],[5,1,4,2],[7,6,8,5,9])],
2910:[[x] for x in ([3,2,3,2,3],[10,10,10,3,1,1],[1],[1,2],[1,1],[1,1,2,2],[1,1,1,2,2],[1,1,1,1,2,2,2],[1,2,3,4],[5,5,5,5,5],[1,1,2,2,3,3,3],[1,1,1,2,2,2,3,3],[9,8,9,8,9,7],[4,4,4,5,5,6])],
2939:[[a,b,n] for a,b,n in [(12,5,4),(6,7,5),(1,6,3),(0,0,1),(1,1,1),(10,10,0),(8,3,2),(15,0,4),(100,200,7),(5,9,3),(31,16,5),(2,7,1),(50,75,6),(999,1,9)]],
3255:[[a,k] for a,k in [([1,2,3,4,3,2,5],3),([2,2,2,2,2],4),([3,2,3,2,3,2],2),([1],1),([1,2],1),([1,2],2),([2,3,4],2),([2,4,5],2),([5,4,3],3),([1,2,3,4],4),([10,11,12,5,6],2),([1,3,5],1),([7,8,9,10,4],3),([4,5,3,4,5],3)]],
3284:[[x] for x in ([1,2,3],[1,3,5,7],[7,6,1,2],[1],[1,2],[2,1],[1,2,1],[3,2,1],[1,2,4],[5,4,3,2],[2,3,2,1],[10,9,8,10],[1,1,1],[4,5,6,2,1])],
3297:[[a,b] for a,b in [('bcca','abc'),('abcabc','abc'),('a','a'),('a','b'),('aa','a'),('ab','ba'),('abc','d'),('aaaa','aa'),('abcd','ab'),('cabca','abc'),('xyzxyz','zy'),('abab','aab'),('leetcode','code'),('mississippi','issi')]],
}

BATCH={
2811:entry('can_split_array',[('nums','list[int]'),('m','int')],'bool',['arrays','greedy','dynamic programming'],['Repeatedly split arrays until singletons remain; every non-singleton part created must have sum at least m.','Return whether a complete sequence of valid splits exists.'],[([CASES[2811][0][0],CASES[2811][0][1]],'The adjacent pair 2+2 reaches four and can anchor a valid split sequence.'),([CASES[2811][1][0],CASES[2811][1][1]],'No adjacent pair reaches five, so no valid first-to-last splitting sequence exists.')],CASES[2811][2:],SPLIT,[SPLIT.replace('a+b>=m','a+b>m'),SPLIT.replace('len(nums)<=2','len(nums)<2')],['Rejects an adjacent pair whose sum equals m.','Rejects every two-element array even though it can split directly into singletons.'],split_oracle,random_split,lesson('A valid process exists exactly when a length-two core can survive until the final split.','Arrays of length at most two always work; otherwise find an adjacent pair with sum at least m.','Scan adjacent sums and return whether one reaches the threshold.','Keep that pair together while peeling off outside singleton elements; conversely every valid process has such a final pair.'),'O(n)','O(1)',5),
2816:entry('double_linked_number',[('head','ListNode')],'ListNode',['linked lists','recursion','math'],['Digits appear most-significant first with no leading zero.','Return the decimal linked list representing exactly twice the input number.'],[([[1,8,9]],'Twice 189 is 378, so the returned digits are 3,7,8.'),([[9,9,9]],'Twice 999 is 1998 and needs a new leading node.')],CASES[2816][2:],DOUBLE,[DOUBLE.replace('node.val*2+carry','node.val+carry'),DOUBLE.replace("return ListNode(carry,head) if carry else head","return head")],['Copies rather than doubles each digit.','Drops a final carry that requires a new leading digit.'],double_oracle,random_double,lesson('Carry flows from the least-significant tail toward the head.','Use postorder recursion to process next nodes before the current digit.','Return carry from each recursive call; prepend a node if the head produces carry.','Each node receives exactly its doubled digit plus the carry from all less-significant digits.'),'O(n)','O(n)',5),
2834:entry('minimum_beautiful_array_sum',[('n','int'),('target','int')],'int',['math','greedy'],['Choose n distinct positive integers with no two summing to target.','Return the minimum possible sum modulo 1,000,000,007.'],[([2,3],'Choose one and three; choosing one and two is forbidden because they sum to three.'),([3,3],'The minimum valid set is one, three, and four for total eight.')],CASES[2834][2:],BEAUTIFUL,[BEAUTIFUL.replace('target//2','(target+1)//2'),BEAUTIFUL.replace('2*target','2*target+2')],['Includes both members of a forbidden complementary pair around target.','Starts the upper safe range at target+1 and overstates the minimum.'],beautiful_oracle,random_beautiful,lesson('Among values below target, use only the smaller side of each forbidden complementary pair.','Take 1 through target//2, then continue from target upward if more values are needed.','Use arithmetic-series formulas for the two ranges and reduce modulo M.','Every skipped low complement conflicts with an already smaller chosen value, while target and above cannot form target with a positive number.'),'O(1)','O(1)',5),
2847:entry('smallest_digit_product',[('n','int')],'str',['math','greedy'],['Find the smallest positive decimal integer whose digit product equals n.','Return -1 when no such digits exist; for n=1 return 1.'],[([105],'Factoring into digits 3,5,7 gives the smallest number 357.'),([7],'The one-digit number seven already has the required product.')],CASES[2847][2:],DIGITS,[DIGITS.replace('range(9,1,-1)','range(8,1,-1)'),DIGITS.replace("''.join(reversed(digits))","''.join(digits)")],['Never uses digit nine, so it misses smaller factorizations containing 9.','Leaves extracted digits descending and returns a larger number.'],digit_product_oracle,random_digit_product,lesson('Replacing a composite product with the largest possible digit minimizes digit count.','Repeatedly divide by digits nine down through two, then sort the extracted digits ascending.','Return -1 for a leftover factor above one and 1 for an empty factorization.','Largest-digit factor extraction minimizes length; ascending those digits minimizes the number at that length.'),'O(log n)','O(log n)',5),
2866:entry('maximum_mountain_sum',[('max_heights','list[int]')],'int',['arrays','monotonic stack','dynamic programming'],['Choose positive tower heights no greater than max_heights.','Heights must be nondecreasing up to one peak and nonincreasing afterward; maximize their sum.'],[([[5,3,4,1,1]],'Using heights 5,3,3,1,1 with the first position as peak gives the maximum sum thirteen.'),([[6,5,3,9,2,7]],'The best capped mountain has sum twenty-two.')],CASES[2866][2:],TOWERS,[TOWERS.replace('>value','>=value',1),TOWERS.replace('-max_heights[i]','')],['Pops equal left bounds and misattributes their accumulated span.','Counts the peak twice when combining left and right sums.'],towers_oracle,random_towers,lesson('For each peak, each side is forced down only when a cap becomes smaller.','Use monotonic stacks to compute the maximum capped prefix and suffix sums for every peak.','Combine left[i]+right[i]-peak height and take the maximum.','The nearest lower cap controls a whole span, so stack jumps reuse the already optimal sum before that span.'),'O(n)','O(n)',5),
2910:entry('minimum_valid_assignment_groups',[('nums','list[int]')],'int',['hash maps','greedy','counting'],['Partition equal values into groups; a group cannot mix values.','Across all groups, sizes may differ by at most one; minimize the group count.'],[([[3,2,3,2,3]],'Counts three and two can form one group each, for two groups total.'),([[10,10,10,3,1,1]],'Frequencies three,one,two require four groups when sizes differ by at most one.')],CASES[2910][2:],GROUPS,[GROUPS.replace('range(min(counts.values()),0,-1)','range(min(counts.values())-1,0,-1)'),GROUPS.replace('(count+size)//(size+1)','count//(size+1)')],['Skips the largest feasible small-group size and may use too many groups.','Rounds group counts down and can leave items unassigned.'],groups_oracle,random_groups,lesson('For a chosen smaller size k, every group has size k or k+1.','Try k downward from the minimum frequency and test whether each frequency can be split into those sizes.','Feasibility is count//k >= count%k; add ceil(count/(k+1)).','The first feasible largest k creates the fewest groups, and the inequality exactly measures whether remainders can be distributed.'),'O(n+f²)','O(f)',5),
2939:entry('maximum_xor_product',[('a','int'),('b','int'),('n','int')],'int',['bit manipulation','greedy','math'],['Choose x with 0 <= x < 2^n.','Maximize (a XOR x)*(b XOR x) and return the product modulo 1,000,000,007.'],[([12,5,4],'The best low-bit choices produce factors fourteen and seven, whose product is 98.'),([6,7,5],'Balancing the two XOR results yields the maximum product 930.')],CASES[2939][2:],XOR,[XOR.replace('elif first>second','elif first<second'),XOR.replace('if left==right','if left!=right')],['Adds a differing bit to the larger factor instead of the smaller one.','Treats differing original bits as though both factors could receive that bit.'],xor_oracle,random_xor,lesson('Equal source bits can be made one in both factors; differing bits must go to exactly one factor.','Preserve fixed high bits, then process controllable bits from high to low while balancing the factors.','Set both on equal bits; on differing bits give the one-bit to the currently smaller prefix.','For a fixed sum contribution at a differing bit, the product is largest when the two factors are as balanced as possible.'),'O(n)','O(1)',5),
3255:entry('k_subarray_powers',[('nums','list[int]'),('k','int')],'list[int]',['arrays','sliding window'],['For every length-k subarray, return its last/maximum value only when values rise consecutively by one.','Return -1 for every other window, preserving window order.'],[([CASES[3255][0][0],CASES[3255][0][1]],'Only the first two length-three windows rise consecutively, producing 3,4,-1,-1,-1.'),([CASES[3255][1][0],CASES[3255][1][1]],'Equal neighboring values are not consecutive ascending, so both windows return -1.')],CASES[3255][2:],POWER,[POWER.replace('value==nums[index-1]+1','value>=nums[index-1]+1'),POWER.replace('run>=k','run>k')],['Accepts jumps larger than one as consecutive.','Requires one extra consecutive edge and rejects valid windows of exactly length k.'],power_oracle,random_power,lesson('A window is valid exactly when the ascending-by-one run ending there has length at least k.','Track the current consecutive run length in one pass.','Reset on any broken edge; from index k-1 onward emit value or -1 based on run length.','Every output window shares its right endpoint with one tracked run, so no separate window scan is needed.'),'O(n)','O(n)',5),
3284:entry('sum_consecutive_subarrays',[('nums','list[int]')],'int',['arrays','dynamic programming'],['A subarray is consecutive when all steps are +1 or all steps are -1; every singleton qualifies.','Sum the element sums of all qualifying subarrays modulo 1,000,000,007.'],[([[1,2,3]],'All six subarrays qualify and their element sums total twenty.'),([[1,3,5,7]],'Only four singleton subarrays qualify, totaling sixteen.')],CASES[3284][2:],CONSECUTIVE,[CONSECUTIVE.replace('value==nums[index-1]-1','value==nums[index-1]+1'),CONSECUTIVE.replace('-value','')],['Counts increasing runs twice and omits decreasing runs.','Counts each singleton twice when combining increasing and decreasing contributions.'],consecutive_oracle,random_consecutive,lesson('At each endpoint, track qualifying subarrays ending there separately for +1 and -1 runs.','Maintain each run length and the sum of sums contributed by its ending subarrays.','Extend the matching direction or reset to the singleton; add both directions minus one singleton copy.','Every qualifying subarray has one endpoint and one direction, while singletons belong to both states and are corrected once.'),'O(n)','O(1)',5),
3297:entry('count_rearrangeable_substrings',[('word1','str'),('word2','str')],'int',['strings','sliding window','hash maps'],['Count substrings of word1 whose characters can be rearranged so word2 is a prefix.','Equivalently, the substring must contain every character of word2 with required multiplicity.'],[(['bcca','abc'],'Only the complete substring bcca contains a,b,c and can be rearranged with abc first.'),(['abcabc','abc'],'Every substring containing at least one a,b,c contributes, for ten total.')],CASES[3297][2:],VALID,[VALID.replace('answer+=left','answer+=max(0,left-1)'),VALID.replace('window[char]==need[char]','window[char]>need[char]')],['Drops one valid starting position at every endpoint.','Marks a requirement satisfied only after exceeding its needed count.'],valid_substrings_oracle,random_valid_substrings,lesson('Once a window contains the required multiset, every earlier start also works.','Expand right while tracking unmet character kinds; shrink left past all valid starts.','After shrinking until invalid, add left, the number of valid starts for this endpoint.','The window counter enforces multiplicities, and the monotone left boundary counts each valid substring exactly at its right endpoint.'),'O(n+len(word2))','O(alphabet)',5),
}

BATCH[2816]['params'][0]=('head','ListNode','listnode');BATCH[2816]['adapter']='listnode'
BATCH[2866]['wrong'][0]=TOWERS.replace('while stack and max_heights[stack[-1]]>value','while stack and max_heights[stack[-1]]<value',1)
BATCH[2866]['wrong_reasons'][0]='Pops larger-boundary candidates instead of smaller caps, so prefix mountain sums are invalid.'
BATCH[2910]['sample_contract_adapter']={
    'source_sample':'Input balls = [3,2,3,2,3] → Output 2.',
    'arguments':[[3,2,3,2,3]],
    'expected':2,
    'reason':'The workbook labels the list balls while the reviewed callable uses the source signature name nums.',
}
