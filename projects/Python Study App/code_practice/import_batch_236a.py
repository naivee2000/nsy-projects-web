"""Large-range waviness, balanced XOR, digit queries, effective removals, and word digits."""
from itertools import combinations
from .import_batch_055 import entry

MOD=10**9+7

def wave(value):
    digits=list(map(int,str(value)))
    return sum((a<b>c) or (a>b<c) for a,b,c in zip(digits,digits[1:],digits[2:]))

def waviness_oracle(args):return sum(wave(value) for value in range(args[0],args[1]+1))
def random_waviness(rng):
    first=rng.randint(1,10000);return [first,first+rng.randint(0,250)]

def balanced_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        xor=even=odd=0
        for right in range(left,len(nums)):
            xor^=nums[right]
            if nums[right]%2:odd+=1
            else:even+=1
            if xor==0 and even==odd:answer=max(answer,right-left+1)
    return answer

def random_balanced(rng):return [[rng.randint(0,31) for _ in range(rng.randint(1,16))]]

def concatenate_oracle(args):
    s,queries=args;answer=[]
    for left,right in queries:
        digits=[int(c) for c in s[left:right+1] if c!='0'];value=0
        for digit in digits:value=(value*10+digit)%MOD
        answer.append(value*sum(digits)%MOD)
    return answer

def random_concatenate(rng):
    n=rng.randint(1,30);s=''.join(str(rng.randrange(10)) for _ in range(n));queries=[]
    for _ in range(rng.randint(1,12)):
        left=rng.randrange(n);queries.append([left,rng.randint(left,n-1)])
    return [s,queries]

def effective_oracle(args):
    nums=args[0];full=0
    for value in nums:full|=value
    answer=0
    for removed in range(1,1<<len(nums)):
        remaining=0
        for index,value in enumerate(nums):
            if not (removed>>index&1):remaining|=value
        answer+=remaining<full
    return answer%MOD

def random_effective(rng):return [[rng.randint(1,63) for _ in range(rng.randint(1,15))]]

WORDS=('zero','one','two','three','four','five','six','seven','eight','nine')
def words_oracle(args):
    text=args[0];answer=[];index=0
    while index<len(text):
        found=False
        for digit,word in enumerate(WORDS):
            if text.startswith(word,index):answer.append(str(digit));index+=len(word);found=True;break
        if not found:index+=1
    return ''.join(answer)

def random_words(rng):
    pieces=[]
    for _ in range(rng.randint(1,12)):
        pieces.append(rng.choice(WORDS) if rng.random()<.6 else ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,5))))
    return [''.join(pieces)]


WAVINESS='''def total_number_waviness_large(num1,num2):
    from functools import lru_cache
    def total(limit):
        if limit<0:return 0
        digits=str(limit)
        @lru_cache(None)
        def visit(position,older,previous,started,tight):
            if position==len(digits):return (int(started),0)
            upper=int(digits[position]) if tight else 9;count=waves=0
            for digit in range(upper+1):
                next_tight=tight and digit==upper;added=0
                if not started and digit==0:next_started=False;next_older=next_previous=10
                elif not started:next_started=True;next_older=10;next_previous=digit
                else:
                    next_started=True;next_older=previous;next_previous=digit
                    if older!=10 and ((previous>older and previous>digit) or (previous<older and previous<digit)):added=1
                ways,value=visit(position+1,next_older,next_previous,next_started,next_tight)
                count+=ways;waves+=value+ways*added
            return count,waves
        return visit(0,10,10,False,True)[1]
    return total(num2)-total(num1-1)
'''

BALANCED='''def maximum_balanced_xor_subarray(nums):
    earliest={(0,0):-1};xor=balance=answer=0
    for index,value in enumerate(nums):
        xor^=value;balance+=1 if value%2==0 else -1;state=(xor,balance)
        if state in earliest:answer=max(answer,index-earliest[state])
        else:earliest[state]=index
    return answer
'''

CONCATENATE='''def nonzero_digit_query_products(s,queries):
    mod=10**9+7;n=len(s);powers=[1]*(n+1)
    for index in range(n):powers[index+1]=powers[index]*10%mod
    sums=[0]*(n+1);counts=[0]*(n+1);prefix=[0]*(n+1)
    for index,character in enumerate(s,1):
        digit=int(character);sums[index]=sums[index-1]+digit;counts[index]=counts[index-1]+(digit>0)
        prefix[index]=(prefix[index-1]*10+digit)%mod if digit else prefix[index-1]
    answer=[]
    for left,right in queries:
        count=counts[right+1]-counts[left];digit_sum=sums[right+1]-sums[left]
        value=(prefix[right+1]-prefix[left]*powers[count])%mod;answer.append(value*digit_sum%mod)
    return answer
'''

EFFECTIVE='''def count_effective_or_removals(nums):
    mod=10**9+7;full=0
    for value in nums:full|=value
    bits=max(1,full.bit_length());size=1<<bits;frequencies=[0]*size
    for value in nums:frequencies[value]+=1
    subset_counts=frequencies[:]
    for bit in range(bits):
        step=1<<bit
        for mask in range(size):
            if mask&step:subset_counts[mask]+=subset_counts[mask^step]
    powers=[1]*(len(nums)+1)
    for index in range(len(nums)):powers[index+1]=powers[index]*2%mod
    answer=0;chosen=full
    while chosen:
        disjoint=subset_counts[(size-1)^chosen];term=powers[disjoint]
        if chosen.bit_count()%2:answer+=term
        else:answer-=term
        chosen=(chosen-1)&full
    return answer%mod
'''

CONVERT='''def convert_number_words(s):
    words=('zero','one','two','three','four','five','six','seven','eight','nine');answer=[];index=0
    while index<len(s):
        for digit,word in enumerate(words):
            if s.startswith(word,index):answer.append(str(digit));index+=len(word);break
        else:index+=1
    return ''.join(answer)
'''

def lesson(a,b,c,d):return [a,b,c,d]

W_CASES=[[a,b] for a,b in ((1,99),(101,110),(120,129),(198,202),(4847,4848),(111,111),(909,919),(1000,1020),(1234,1250),(9890,9900),(500,550),(9990,10000))]
B_CASES=[[[*values]] for values in ([0],[1],[1,1],[1,2],[3,1,3,2,1],[3,2,8,5,4,14,9,14],[2,2,2,2],[0,1,1,0],[5,7,2,0,4,4],[8,3,11,0,8,3],[1,2,3,0,3,2,1,0],[6,5,3,0,6,5,3,0])]
C_CASES=[[s,q] for s,q in (('0',[[0,0]]),('1000',[[0,2],[1,1]]),('10203004',[[0,6],[1,3],[4,6]]),('9876543210',[[0,8]]),('123',[[0,0],[0,2],[1,2]]),('00000',[[0,4],[2,3]]),('10509',[[0,4],[1,3]]),('9001002',[[0,6],[2,5]]),('31415926',[[0,7],[2,6]]),('101010101',[[0,8],[1,7]]),('7650004321',[[0,9],[3,8]]),('9081726354',[[1,9],[0,5],[4,7]]))]
E_CASES=[[[*values]] for values in ([1],[1,2],[1,2,4],[8,8,1],[2,2,1],[7,4,6],[3,3,3],[1,1,2,2],[5,10,12],[1,3,7,15],[6,9,12,3],[31,16,8,4,2,1])]
T_CASES=[[s] for s in ('one','zero','tw','zeero','ninexseven','onefourtwo','zeroonetwo','abcsevenxyz','eightwo','fourfivejunkzero','ninenineeight','xxoneighttwothreezz')]

BATCH={
3753:entry('total_number_waviness_large',[('num1','int'),('num2','int')],'int',['dynamic programming','digit dp','math'],['1≤num1≤num2≤10^15.','A middle digit contributes when it is strictly above both neighbors or strictly below both.','Return total waviness across the inclusive range.'],[([120,130],'Only 120, 121, and 130 contribute one each, totaling three.'),([4848,4848],'The internal eight and four are a peak and valley, giving two.')],W_CASES,WAVINESS,[WAVINESS.replace('previous>older and previous>digit','previous>=older and previous>=digit'),WAVINESS.replace('return total(num2)-total(num1-1)','return total(num2)-total(num1)')],['Counts equal-neighbor plateaus as peaks.','Excludes num1 by subtracting its inclusive prefix total.'],waviness_oracle,random_waviness,lesson('Compute a prefix total F(x), then answer F(num2)-F(num1-1).','A digit-DP state keeps the last two significant digits, whether the number has started, and tightness.','When appending a digit, the previous digit becomes internal and contributes if it is a strict peak or valley.','The DP enumerates every integer once and accumulates both suffix counts and their added waviness.'),'O(digits·11²·states·10)','O(digits·states)',8),
3755:entry('maximum_balanced_xor_subarray',[('nums','list[int]')],'int',['arrays','bit manipulation','prefix sums'],['nums contains up to 100,000 nonnegative integers.','A qualifying subarray has XOR zero and equal counts of even and odd values.','Return its maximum length, or zero when none exists.'],[([[3,1,3,2,0]],'The subarray [1,3,2,0] has XOR zero and two values of each parity.'),([[3,2,8,5,4,14,9,15]],'The full array has XOR zero and four values of each parity.')],B_CASES,BALANCED,[BALANCED.replace('1 if value%2==0 else -1','1 if value%2==0 else 0'),BALANCED.replace('else:earliest[state]=index','earliest[state]=index')],['Adds nothing for odd values instead of subtracting one.','Overwrites the earliest state occurrence and loses maximum-length candidates.'],balanced_oracle,random_balanced,lesson('A subarray XOR is zero when its endpoint prefix XORs match.','Its parity counts match when the endpoint even-minus-odd prefix balances also match.','Store the earliest index for every pair (prefix XOR, balance) and maximize distance on repeats.','Equality of both prefix components is exactly the two required subarray conditions, and the earliest match gives the longest span.'),'O(n)','O(n)',6),
3756:entry('nonzero_digit_query_products',[('s','str'),('queries','list[list[int]]')],'list[int]',['strings','prefix sums','modular arithmetic'],['s and queries each contain up to 100,000 entries.','For each inclusive range, concatenate its nonzero digits, multiply by their digit sum, and reduce modulo 1,000,000,007.','A range containing only zeros returns zero.'],[(['10203004',[[0,7],[1,3],[4,6]]],'The ranges form 1234, 2, and 3, producing 12340, 4, and 9.'),(['1000',[[0,3],[1,1]]],'The whole range produces one while the zero-only range produces zero.')],C_CASES,CONCATENATE,[CONCATENATE.replace('counts[index-1]+(digit>0)','counts[index-1]+1'),CONCATENATE.replace('digit_sum=sums[right+1]-sums[left]','digit_sum=sums[right]-sums[left]')],['Counts zeros as concatenated digit positions and shifts substring extraction.','Omits the query’s final digit from its digit sum.'],concatenate_oracle,random_concatenate,lesson('Maintain prefix digit sums, prefix nonzero counts, and the concatenation of nonzero digits modulo M.','For [l,r], its concatenation is prefix[r+1]-prefix[l]·10^(nonzero count), while its sum is a standard prefix difference.','Multiply those two range values modulo M.','The power removes exactly the suffix positions contributed after l, and zeros affect neither concatenation length nor sum.'),'O(|s|+queries)','O(|s|)',6),
3757:entry('count_effective_or_removals',[('nums','list[int]')],'int',['arrays','bit manipulation','inclusion exclusion','subset dp'],['nums contains up to 100,000 positive integers below 2^20.','A removed nonempty subsequence is effective when the OR of remaining indices is strictly below the original OR.','Count index-distinct removal subsequences modulo 1,000,000,007.'],[([[1,2,3]],'Removing all carriers of bit zero or bit one gives three distinct effective subsequences.'),([[8,8]],'Only removing both copies clears the sole present bit, giving one.')],E_CASES,EFFECTIVE,[EFFECTIVE.replace('if chosen.bit_count()%2','if chosen.bit_count()%2==0'),EFFECTIVE.replace('(size-1)^chosen','chosen')],['Reverses inclusion–exclusion signs.','Counts elements contained in the selected bit mask instead of elements disjoint from it.'],effective_oracle,random_effective,lesson('The remaining OR drops exactly when at least one original bit loses every element carrying it.','For a chosen nonempty bit subset, all elements intersecting it must be removed, while disjoint elements are optional.','Use SOS subset sums to count disjoint elements for every bit subset, then inclusion–exclude over subsets of the original OR.','Each event is one cleared bit; their intersections have 2^(optional disjoint elements) removals, so inclusion–exclusion counts their union exactly.'),'O(20·2^20 + n)','O(2^20+n)',8),
3758:entry('convert_number_words',[('s','str')],'str',['strings','tries','parsing'],['s contains up to 100,000 lowercase letters.','Scan left to right; when a complete English digit word begins at the current position, append its digit and consume the word.','Otherwise skip one character; return empty when no word is found.'],[(['onefourthree'],'The consecutive words one, four, and three produce 143.'),(['ninexsix'],'Parse nine, skip x, then parse six to produce 96.')],T_CASES,CONVERT,[CONVERT.replace('index+=len(word)','index+=len(word)-1'),CONVERT.replace("('zero','one','two','three','four','five','six','seven','eight','nine')","('one','two','three','four','five','six','seven','eight','nine','zero')")],['Advances one character too little after a match and can reuse its final letter.','Maps word positions to the wrong digits by rotating the dictionary order.'],words_oracle,random_words,lesson('Only a complete number word beginning at the current scan position may be consumed.','Try the ten fixed words, append the matching digit, and jump by its full length; otherwise advance once.','Continue until the input is exhausted.','This directly follows the required left-to-right priority and prevents characters inside a consumed word from starting another match.'),'O(10·|s|)','O(1) beyond output',5),
}
