"""Grid OR, constrained distinct windows, email normalization, products, and substring sorting."""
from collections import Counter,deque
from itertools import product
from .import_batch_055 import entry


def grid_oracle(args):return min((__import__('functools').reduce(int.__or__,chosen,0) for chosen in product(*args[0])))
def random_grid(rng):return [[[rng.randint(0,63) for _ in range(rng.randint(1,5))] for _ in range(rng.randint(1,6))]]

def distinct_oracle(args):
    nums,k,m=args;answer=0
    for left in range(len(nums)):
        counts={}
        for right in range(left,len(nums)):
            counts[nums[right]]=counts.get(nums[right],0)+1
            answer+=len(counts)==k and min(counts.values())>=m
    return answer
def random_distinct(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,22))],rng.randint(1,5),rng.randint(1,5)]

def email_oracle(args):
    groups=set()
    for email in args[0]:
        local,domain=email.rsplit('@',1);clean=[]
        for character in local:
            if character=='+':break
            if character!='.':clean.append(character.lower())
        groups.add(''.join(clean)+'@'+domain.lower())
    return len(groups)
def random_email(rng):
    emails=[]
    for _ in range(rng.randint(1,20)):
        base=''.join(rng.choice('abcXYZ') for _ in range(rng.randint(1,6)))
        local='.'.join(base) if rng.random()<.3 else base
        if rng.random()<.4:local+='+tag'+str(rng.randint(0,3))
        emails.append(local+'@'+rng.choice(['Example.com','test.org','mail.net']))
    return [emails]

def balance_oracle(args):
    nums=args[0]
    for i in range(len(nums)):
        right=1
        for value in nums[i+1:]:right*=value
        if sum(nums[:i])==right:return i
    return -1
def random_balance(rng):return [[rng.randint(1,8) for _ in range(rng.randint(1,14))]]

def sorting_oracle(args):
    start=args[0];target=''.join(sorted(start))
    if start==target:return 0
    queue=deque([(start,0)]);seen={start}
    while queue:
        value,distance=queue.popleft()
        for left in range(len(value)):
            for right in range(left+1,len(value)+1):
                if left==0 and right==len(value):continue
                nxt=value[:left]+''.join(sorted(value[left:right]))+value[right:]
                if nxt==target:return distance+1
                if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
    return -1
def random_sorting(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,7)))]

GRID='''def minimum_row_choice_or(grid):
    answer=0;bits=max(map(max,grid)).bit_length()
    for bit in range(bits-1,-1,-1):
        allowed=answer|((1<<bit)-1)
        if any(not any(value|allowed==allowed for value in row) for row in grid):answer|=1<<bit
    return answer
'''

DISTINCT='''def count_k_distinct_with_frequency(nums,k,m):
    from collections import Counter
    def at_least(limit):
        counts=Counter();qualified=0;left=0;answer=0
        for value in nums:
            counts[value]+=1
            if counts[value]==m:qualified+=1
            while len(counts)>=limit and qualified>=k:
                removed=nums[left];counts[removed]-=1;left+=1
                if counts[removed]==m-1:qualified-=1
                if counts[removed]==0:del counts[removed]
            answer+=left
        return answer
    return at_least(k)-at_least(k+1)
'''

EMAIL='''def count_unique_email_groups(emails):
    groups=set()
    for email in emails:
        local,domain=email.rsplit('@',1)
        local=local.split('+',1)[0].replace('.','').lower()
        groups.add(local+'@'+domain.lower())
    return len(groups)
'''

BALANCE='''def smallest_balanced_index(nums):
    left_sum=sum(nums);right_product=1
    for index in range(len(nums)-1,-1,-1):
        left_sum-=nums[index]
        if left_sum==right_product:return index
        right_product*=nums[index]
        if right_product>=left_sum:break
    return -1
'''

SORTING='''def minimum_proper_substring_sorts(s):
    if all(s[i]<=s[i+1] for i in range(len(s)-1)):return 0
    if len(s)==2:return -1
    low=min(s);high=max(s)
    if s[0]==low or s[-1]==high:return 1
    if any(character==low or character==high for character in s[1:-1]):return 2
    return 3
'''

def lesson(a,b,c,d):return [a,b,c,d]
O_CASES=[[[*rows]] for rows in ([[1,5],[2,4]],[[0]],[[1],[2]],[[1,2]],[[7,3],[5,1]],[[8,4],[2,1]],[[3,6],[5,9],[10,12]],[[0,7],[4,2]],[[15,8],[7,3]],[[1,3,7],[2,6,10]],[[32,1],[16,2],[8,4]],[[5,5],[5,5]],[[9,10],[12,3],[6,5]],[[0,1],[0,2],[0,4]],[[63,31],[47,15]])]
D_CASES=[[a,k,m] for a,k,m in (([1,2,1,2,2],2,2),([1],1,1),([1],1,2),([1,1],1,2),([1,2],2,1),([1,2,1],2,1),([1,2,1],2,2),([1,1,2,2],2,2),([1,2,3,1,2,3],3,1),([1,1,1],1,2),([1,2,2,3,3,1],2,2),([4,4,5,4,5],2,2),([1,2,3,4],1,1),([2,1,2,1,3],2,2),([1,1,2,2,3,3],3,2))]
E_CASES=[[v] for v in (['test.email+alex@leetcode.com','test.e.mail+bob.cathy@leetcode.com','testemail+david@lee.tcode.com'],['a@b.com'],['A@B.COM'],['a.b@x.com','ab@x.com'],['a+z@x.com','a@x.com'],['a@bc.com','ab@c.com'],['x.y+tag@Test.Org','xy@test.org'],['u@a.com','u@b.com'],['a+b+c@x.com'],['first.last@mail.net','firstlast+z@MAIL.NET'],['a@x.com','A@X.COM','a.@x.com'],['one@domain.com','two@domain.com'],['dots...here@x.com','dotshere@x.com'],['z+ignore@a.org','z+other@a.org'],['abc@x.org','abc@x.org'])]
B_CASES=[[[*v]] for v in ([2,1,2],[1],[2],[1,1],[1,2],[2,2],[1,2,3],[3,1,3],[2,3,1],[5,2,1,2],[1,1,1,1],[4,2,2,2],[6,3,2,1],[2,4,2,2],[8,1,2,4])]
S_CASES=[[s] for s in ('dog','a','ab','ba','abc','cba','bca','cab','dcba','badc','bbca','dacb','fedcba','azby','ccbbaa')]

BATCH={
3858:entry('minimum_row_choice_or',[('grid','list[list[int]]')],'int',['matrices','bit manipulation','greedy'],['grid is nonempty, every row is nonempty, and values are nonnegative.','Choose exactly one value from every row.','Return the minimum possible bitwise OR of the chosen values.'],[([[[1,5],[2,4]]],'Choosing one and two produces OR three, the minimum.'),([[[0]]],'The only selected value is zero, so the result is zero.')],O_CASES,GRID,[GRID.replace('range(bits-1,-1,-1)','range(bits)'),GRID.replace('any(not any','all(not any')],['Tests bits from least significant to most significant, breaking greedy significance.','Sets a required bit only when every row fails instead of when any row lacks an allowed choice.'],grid_oracle,random_grid,lesson('Decide result bits from most significant to least significant.','Tentatively keep the current bit zero while allowing all undecided lower bits to be one.','The bit may remain zero only if every row contains at least one value using no forbidden bit.','Row choices are independent once an allowed mask is fixed; the first infeasible high bit must be included, giving the lexicographically smallest bit pattern.'),'O(Bmn)','O(1)',6),
3859:entry('count_k_distinct_with_frequency',[('nums','list[int]'),('k','int'),('m','int')],'int',['arrays','hash maps','sliding window'],['nums has up to 100,000 integers; k and m are positive.','Count contiguous subarrays with exactly k distinct values.','Every one of those distinct values must occur at least m times in the subarray.'],[([[1,2,1,2,2],2,2],'The qualifying subarrays are [1,2,1,2] and [1,2,1,2,2], giving two.'),([[1,1],1,2],'Only the full array has one distinct value occurring at least twice.')],D_CASES,DISTINCT,[DISTINCT.replace('at_least(k)-at_least(k+1)','at_least(k)'),DISTINCT.replace('counts[value]==m','counts[value]>=m')],['Counts windows with at least k distinct values instead of exactly k.','Increments the qualified-value counter repeatedly after a frequency exceeds m.'],distinct_oracle,random_distinct,lesson('Count a difference of two thresholded window families to isolate exactly k distinct values.','For each distinct-count limit, track both map size and how many values have reached frequency m.','Shrink while both thresholds hold; each removed prefix contributes one valid start for the current right endpoint.','Subtracting the k+1-distinct family removes every window with extra values, leaving exactly k whose frequencies all meet m.'),'O(n)','O(n)',8),
3860:entry('count_unique_email_groups',[('emails','list[str]')],'int',['arrays','hash sets','strings'],['emails is a nonempty list of valid addresses with one @ separator each.','Before @, ignore dots and everything from the first + onward; lowercase both local and domain parts.','Count distinct normalized addresses.'],[([['test.email+alex@leetcode.com','test.e.mail+bob.cathy@leetcode.com','testemail+david@lee.tcode.com']],'The first two normalize together, while the third has another domain, giving two groups.'),([['A@B.COM']],'Lowercasing produces a@b.com, so the single address forms one group.')],E_CASES,EMAIL,[EMAIL.replace("local+'@'+domain.lower()","local+domain.lower()"),EMAIL.replace(".replace('.','')",'')],['Drops the @ separator and can collide different local/domain splits.','Leaves dots in the local name instead of ignoring them.'],email_oracle,random_email,lesson('Normalization must retain the boundary between local and domain parts.','Split at @, truncate the local part at +, remove its dots, lowercase both pieces, and rejoin with @.','Insert each canonical address into a set.','Two addresses share a group exactly when all normalization rules yield the same boundary-preserving canonical string.'),'O(total characters)','O(total characters)',5),
3862:entry('smallest_balanced_index',[('nums','list[int]')],'int',['arrays','prefix sums','products'],['nums is a nonempty array of positive integers.','At index i, compare the sum strictly left of i with the product strictly right of i; an empty product is one.','Return the smallest balanced index or -1.'],[([[2,1,2]],'At index one, the left sum two equals the right product two.'),([[1]],'The empty left sum is zero and empty right product is one, so no index is balanced.')],B_CASES,BALANCE,[BALANCE.replace('right_product=1','right_product=0'),BALANCE.replace('return index','return len(nums)-1-index')],['Uses zero rather than the multiplicative identity for an empty suffix.','Returns distance from the right instead of the original array index.'],balance_oracle,random_balance,lesson('Scan from right to left while maintaining the sum to the left and product to the right.','Remove the current value from the total before comparing, then multiply it into the suffix after comparing.','With positive values, once the suffix product is at least the left sum, moving left cannot restore equality.','The invariants give the exact two sides at every index; positivity makes the early stop safe and also makes a balanced index unique.'),'O(n)','O(1)',5),
3863:entry('minimum_proper_substring_sorts',[('s','str')],'int',['strings','greedy'],['s is a nonempty lowercase string.','One operation sorts any contiguous substring except the entire string in nondecreasing order.','Return the minimum operations to sort all of s, or -1 if impossible.'],[(['dog'],'Sorting the proper substring do places d,o in order and yields dgo, so one operation suffices.'),(['ba'],'The only useful substring would be the entire two-character string, which is forbidden, so return -1.')],S_CASES,SORTING,[SORTING.replace('if len(s)==2:return -1','if len(s)==2:return 1'),SORTING.replace('return 3','return 2')],['Allows sorting the entire length-two string despite the proper-substring restriction.','Claims every remaining arrangement is solvable in two operations, missing the three-operation case.'],sorting_oracle,random_sorting,lesson('Whether one or two operations work depends on where the global minimum and maximum already occur.','Sorted strings need zero; an unsorted length-two string is impossible because only its whole span could change.','An extreme at the matching end enables one operation; an extreme in the interior enables two; otherwise three suffice.','Proper prefix and suffix sorts realize these bounds, while absent extremes prevent any smaller sequence from placing both ends correctly.'),'O(n)','O(1)',6),
}
