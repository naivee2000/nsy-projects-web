"""Zero-free counts, monotone queries, expression evaluation, waviness, and signed permutations."""
from functools import lru_cache
from itertools import permutations,product
from .import_batch_055 import entry


def distinct_oracle(args):
    n=args[0];return len({int(str(value).replace('0','')) for value in range(1,n+1)})

def random_distinct(rng):return [rng.randint(1,5000)]

def stable_oracle(args):
    nums,queries=args;answer=[]
    for left,right in queries:
        total=0
        for start in range(left,right+1):
            for end in range(start,right+1):total+=all(nums[i]<=nums[i+1] for i in range(start,end))
        answer.append(total)
    return answer

def random_stable(rng):
    n=rng.randint(1,14);nums=[rng.randint(1,12) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,10)):
        left=rng.randrange(n);queries.append([left,rng.randint(left,n-1)])
    return [nums,queries]

def expression_oracle(args):
    text=args[0]
    def parse(index):
        if text[index]=='-' or text[index].isdigit():
            end=index+1
            while end<len(text) and text[end].isdigit():end+=1
            return int(text[index:end]),end
        end=text.index('(',index);operation=text[index:end];first,pos=parse(end+1);second,pos=parse(pos+1)
        if operation=='add':value=first+second
        elif operation=='sub':value=first-second
        elif operation=='mul':value=first*second
        else:value=first//second
        return value,pos+1
    return parse(0)[0]

def make_expression(rng,depth=0):
    if depth>=3 or rng.random()<.35:return str(rng.randint(-20,20))
    operation=rng.choice(('add','sub','mul'))
    return f'{operation}({make_expression(rng,depth+1)},{make_expression(rng,depth+1)})'

def random_expression(rng):return [make_expression(rng)]

def wave(value):
    digits=list(map(int,str(value)))
    return sum((a<b>c) or (a>b<c) for a,b,c in zip(digits,digits[1:],digits[2:]))

def waviness_oracle(args):return sum(wave(value) for value in range(args[0],args[1]+1))
def random_waviness(rng):
    first=rng.randint(1,5000);return [first,first+rng.randint(0,200)]

def signed_oracle(args):
    n,target=args;answer=None
    for order in permutations(range(1,n+1)):
        for signs in product((-1,1),repeat=n):
            candidate=tuple(value*sign for value,sign in zip(order,signs))
            if sum(candidate)==target and (answer is None or candidate<answer):answer=candidate
    return [] if answer is None else list(answer)

def random_signed(rng):return [rng.randint(1,7),rng.randint(-30,30)]


DISTINCT='''def count_distinct_after_removing_zeros(n):
    digits=str(n)
    from functools import lru_cache
    @lru_cache(None)
    def count(position,started,tight):
        if position==len(digits):return int(started)
        limit=int(digits[position]) if tight else 9;answer=0
        for digit in range(limit+1):
            if started and digit==0:continue
            answer+=count(position+1,started or digit>0,tight and digit==limit)
        return answer
    return count(0,False,True)
'''

STABLE='''def count_nondecreasing_subarrays_in_ranges(nums,queries):
    from bisect import bisect_right
    starts=[];totals=[0];start=0
    for end in range(len(nums)):
        if end==len(nums)-1 or nums[end]>nums[end+1]:
            starts.append(start);length=end-start+1;totals.append(totals[-1]+length*(length+1)//2);start=end+1
    answer=[]
    for left,right in queries:
        first=bisect_right(starts,left);last=bisect_right(starts,right)-1
        if first>last:
            length=right-left+1;answer.append(length*(length+1)//2)
        else:
            a=starts[first]-left;b=right-starts[last]+1
            answer.append(a*(a+1)//2+totals[last]-totals[first]+b*(b+1)//2)
    return answer
'''

EXPRESSION='''def evaluate_nested_expression(expression):
    stack=[];index=0;operations={'add':lambda a,b:a+b,'sub':lambda a,b:a-b,'mul':lambda a,b:a*b,'div':lambda a,b:a//b}
    while index<len(expression):
        character=expression[index]
        if character.isalpha():
            end=index
            while end<len(expression) and expression[end].isalpha():end+=1
            stack.append(expression[index:end]);index=end
        elif character=='(':
            stack.append(character);index+=1
        elif character==')':
            second=stack.pop();first=stack.pop();stack.pop();operation=stack.pop();stack.append(operations[operation](first,second));index+=1
        elif character==',':index+=1
        else:
            end=index+1
            while end<len(expression) and expression[end].isdigit():end+=1
            stack.append(int(expression[index:end]));index=end
    return stack[0]
'''

WAVINESS='''def total_number_waviness(num1,num2):
    answer=0
    for value in range(num1,num2+1):
        digits=str(value)
        for index in range(1,len(digits)-1):
            answer+=(digits[index-1]<digits[index]>digits[index+1]) or (digits[index-1]>digits[index]<digits[index+1])
    return answer
'''

SIGNED='''def smallest_signed_permutation(n,target):
    total=n*(n+1)//2
    if abs(target)>total or (total-target)%2:return []
    remaining=(total-target)//2;negative=[];positive=[]
    for value in range(n,0,-1):
        capacity=value*(value-1)//2
        if remaining>=value and remaining-value<=capacity:
            negative.append(-value);remaining-=value
        else:positive.append(value)
    if remaining:return []
    return negative+sorted(positive)
'''

def lesson(a,b,c,d):return [a,b,c,d]

D_CASES=[[n] for n in (1,4,9,11,19,20,99,100,101,105,999,1005)]
S_CASES=[[a,b] for a,b in (([1],[[0,0]]),([2,2],[[0,0]]),([3,1,2],[[0,1],[1,2]]),([1,2,3],[[0,2],[1,2]]),([3,2,1],[[0,2],[0,1]]),([1,3,2,4],[[0,3],[1,3]]),([5,5,4,4,6],[[0,4],[2,4],[0,1]]),([2,1,1,2],[[0,3],[1,3]]),([1,2,2,3,1],[[0,4],[0,3],[2,4]]),([4,3,5,6,2,7],[[0,5],[1,3],[3,5]]),([1,1,1,1],[[0,3],[1,2]]),([9,8,7,7,8,9],[[0,5],[2,5],[3,4]]))]
E_CASES=[[s] for s in ('0','-42','add(2,4)','sub(2,3)','mul(-4,5)','div(20,4)','add(mul(2,3),4)','sub(10,mul(2,3))','div(mul(6,sub(8,4)),add(1,2))','mul(add(1,2),sub(8,3))','add(-5,sub(-2,7))','sub(add(10,20),div(18,3))')]
W_CASES=[[a,b] for a,b in ((1,99),(101,110),(120,129),(198,202),(4847,4848),(111,111),(909,919),(1000,1020),(1234,1250),(9890,9900),(500,550),(9990,10000))]
P_CASES=[[n,t] for n,t in ((1,1),(1,-1),(1,0),(2,3),(2,0),(3,2),(3,6),(4,2),(4,-10),(5,3),(6,7),(7,-4))]

BATCH={
3747:entry('count_distinct_after_removing_zeros',[('n','int')],'int',['dynamic programming','digit dp','math'],['n is between one and 10^15.','For every x from one through n, delete all zero digits from its decimal representation.','Return the number of distinct resulting positive integers.'],[([10],'Values one through nine remain distinct while ten also becomes one, giving nine results.'),([3],'The results one, two, and three are all distinct.')],D_CASES,DISTINCT,[DISTINCT.replace('if started and digit==0:continue','if digit==0:continue'),DISTINCT.replace('return int(started)','return 1')],['Forbids leading zero padding and undercounts shorter zero-free integers.','Counts the all-leading-zero path as a positive result.'],distinct_oracle,random_distinct,lesson('Every result is a zero-free integer no greater than n, and every such integer occurs by choosing x equal to itself.','Count positive integers at most n whose decimal digits contain no zero.','A tight digit DP tracks position, whether the number has started, and whether the prefix equals n.','The bijection reduces the original many-to-one deletion process to this exact zero-free count.'),'O(log n·states·10)','O(log n)',6),
3748:entry('count_nondecreasing_subarrays_in_ranges',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','binary search','prefix sums'],['nums and queries each contain up to 100,000 entries.','A stable subarray is contiguous and nondecreasing; single elements qualify.','For each inclusive query range, count stable subarrays lying wholly inside it.'],[([[3,1,2],[[0,1],[1,2],[0,2]]],'The three ranges contain two, three, and four nondecreasing subarrays.'),([[2,2],[[0,1],[0,0]]],'Equal values form one length-two stable subarray, giving counts three and one.')],S_CASES,STABLE,[STABLE.replace('nums[end]>nums[end+1]','nums[end]>=nums[end+1]'),STABLE.replace('bisect_right(starts,left)','bisect_right(starts,left)-1')],['Breaks runs at equal adjacent values and loses valid nondecreasing subarrays.','Chooses the segment before the query’s left boundary when locating partial runs.'],stable_oracle,random_stable,lesson('Split nums into maximal nondecreasing runs; every stable subarray lies inside exactly one run.','Prefix-sum each full run’s triangular subarray count and store its start.','For a query, binary-search the first and last touched runs, add full interior runs, and use triangular counts for clipped edge pieces.','The run partition is disjoint and exhaustive, so these pieces count every contained stable subarray once.'),'O((n+q) log n)','O(n)',8),
3749:entry('evaluate_nested_expression',[('expression','str')],'int',['strings','stacks','parsing'],['expression is a valid integer literal or nested add, sub, mul, or div call up to 100,000 characters.','Each operation has exactly two comma-separated operands.','All divisions are exact and all intermediate values fit a signed long integer.'],[(['add(2,3)'],'Adding the two literals produces five.'),(['div(mul(4,sub(9,5)),add(1,1))'],'The inner values produce 16 divided by 2, giving eight.')],E_CASES,EXPRESSION,[EXPRESSION.replace("'sub':lambda a,b:a-b","'sub':lambda a,b:b-a"),EXPRESSION.replace('second=stack.pop();first=stack.pop()','first=stack.pop();second=stack.pop()')],['Reverses subtraction operands.','Pops every binary operation’s operands in the wrong order.'],expression_oracle,random_expression,lesson('The grammar is fully parenthesized, so a closing parenthesis completes exactly one pending binary operation.','Scan tokens onto a stack; on a close, pop the two values, marker, and operator, then push the result.','Parse signed integer literals and operation names directly without recursion.','Stack nesting mirrors grammar nesting, so each reduction evaluates one complete innermost expression before its parent.'),'O(|expression|)','O(|expression|)',8),
3751:entry('total_number_waviness',[('num1','int'),('num2','int')],'int',['math','enumeration'],['1≤num1≤num2≤100,000.','A middle digit contributes one when it is strictly greater than both neighbors or strictly less than both.','Sum this waviness across the inclusive range.'],[([120,130],'Only 120, 121, and 130 contribute one each, totaling three.'),([4848,4848],'Digits eight and four are a peak and valley, so the waviness is two.')],W_CASES,WAVINESS,[WAVINESS.replace('range(1,len(digits)-1)','range(1,max(1,len(digits)-2))'),WAVINESS.replace("digits[index-1]<digits[index]>digits[index+1]","digits[index-1]<=digits[index]>=digits[index+1]")],['Skips the final internal digit when checking longer numbers.','Counts non-strict plateaus as peaks.'],waviness_oracle,random_waviness,lesson('Only internal digit positions can be peaks or valleys.','Enumerate the modest numeric range, convert each value to digits, and compare every internal digit with its two neighbors.','Add one for either strict greater-than-both or strict less-than-both.','Each qualifying position is examined once and the endpoint exclusions follow directly from the loop bounds.'),'O((num2-num1+1)·digits)','O(digits)',5),
3752:entry('smallest_signed_permutation',[('n','int'),('target','int')],'list[int]',['arrays','greedy','math'],['n is at most 100,000 and target has magnitude at most 10^10.','Absolute values must be a permutation of one through n and signed values must sum to target.','Return the lexicographically smallest valid array, or an empty list.'],[([3,0],'Choosing negative three and positive one and two yields the smallest array [-3,1,2].'),([1,10000000000],'The target lies outside the possible sum range, so no array exists.')],P_CASES,SIGNED,[SIGNED.replace('(total-target)%2','target%2'),SIGNED.replace('for value in range(n,0,-1)','for value in range(1,n+1)')],['Tests target parity alone instead of parity relative to the total sum.','Chooses negative magnitudes from smallest upward and loses lexicographic minimality.'],signed_oracle,random_signed,lesson('Starting with all values positive gives total S; negating a subset of sum q changes the total to S-2q.','Feasibility requires q=(S-target)/2 to be an integer in [0,S].','Choose negative magnitudes greedily from n downward whenever the remaining sum is achievable by smaller values, then sort the positive remainder.','This maximizes the earliest negative magnitude lexicographically, while consecutive integers can realize every residual sum through their triangular capacity.'),'O(n)','O(n)',6),
}
