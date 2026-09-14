"""Log cutting, digit words, caption tags, prime frequencies, and base conversion."""
from collections import Counter
from .import_batch_055 import entry

WORDS=['zero','one','two','three','four','five','six','seven','eight','nine']
def logs_oracle(a):
    n,m,k=a
    for x in (n,m):
        if x>k:return min(i*(x-i) for i in range(1,x) if i<=k and x-i<=k)
    return 0
def random_logs(r):
    k=r.randint(1,30);large=r.randint(k,2*k);small=r.randint(1,k);return [large,small,k] if r.random()<.5 else [small,large,k]
def odd_letters_oracle(a):return sum(v%2 for v in Counter(''.join(WORDS[int(c)] for c in str(a[0]))).values())
def random_odd_letters(r):return [r.randint(0,10**9)]
def tag_oracle(a):
    words=a[0].split();body=''.join((w.lower() if i==0 else w[:1].upper()+w[1:].lower()) for i,w in enumerate(words));return ('#'+''.join(c for c in body if c.isalpha()))[:100]
def random_tag(r):return [' '.join(''.join(r.choice('abcXYZ') for _ in range(r.randint(1,12))) for _ in range(r.randint(1,15)))]
def prime(n):return n>1 and all(n%d for d in range(2,int(n**.5)+1))
def prime_oracle(a):return any(prime(v) for v in Counter(a[0]).values())
def random_prime(r):return [[r.randint(1,12) for _ in range(r.randint(1,50))]]
def base(n,b):
    chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';out=''
    while n:out=chars[n%b]+out;n//=b
    return out or '0'
def base_oracle(a):return base(a[0]**2,16)+base(a[0]**3,36)
def random_base(r):return [r.randint(1,1000)]

LOGS='''def minimum_log_transport_cut_cost(n,m,k):
    longest=max(n,m)
    return 0 if longest<=k else k*(longest-k)
'''
ODD='''def count_odd_digit_word_letters(n):
    from collections import Counter
    words=['zero','one','two','three','four','five','six','seven','eight','nine']
    counts=Counter(''.join(words[int(char)] for char in str(n)))
    return sum(count%2 for count in counts.values())
'''
TAG='''def generate_video_caption_tag(caption):
    words=caption.split()
    body=''.join(word.lower() if i==0 else word[:1].upper()+word[1:].lower() for i,word in enumerate(words))
    body=''.join(char for char in body if char.isalpha())
    return ('#'+body)[:100]
'''
PRIME='''def has_prime_element_frequency(nums):
    from collections import Counter
    def is_prime(value):return value>1 and all(value%d for d in range(2,int(value**0.5)+1))
    return any(is_prime(count) for count in Counter(nums).values())
'''
BASE='''def hexadecimal_and_base36_power_string(n):
    chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def convert(value,base):
        answer=''
        while value:
            answer=chars[value%base]+answer
            value//=base
        return answer or '0'
    return convert(n*n,16)+convert(n*n*n,36)
'''

BATCH={
3560:entry('minimum_log_transport_cut_cost',[('n','int'),('m','int'),('k','int')],'int',['math','greedy'],['Two logs must occupy at most three trucks, and each carried piece has length at most k.','A cut into lengths a and b costs a*b.','Return the minimum cost; valid inputs require at most one log to be cut once.'],[([6,5,5],'Cut length six into one and five for cost five; the other log already fits.'),([4,5,5],'Both logs fit without cutting, so cost is zero.')],[[n,m,k] for n,m,k in [(1,1,1),(4,5,5),(6,5,5),(10,1,5),(9,3,5),(8,5,5),(2,6,4),(7,2,6),(12,4,7),(3,2,2),(20,10,10),(11,8,10),(5,9,6),(2,2,5)]],LOGS,[LOGS.replace('k*(longest-k)','(longest//2)*(longest-longest//2)'),LOGS.replace('longest<=k','longest<=k+1')],['Uses a balanced cut even when it exceeds the minimum product.','Incorrectly treats a log one unit above the limit as fitting.'],logs_oracle,random_logs,['No cut is needed when both logs fit.','Otherwise the oversized log must be split into two pieces no longer than k.','For a fixed sum, product is minimized at the most unequal feasible split: k and length-k.','The source guarantee means only that single cut is required.'],'O(1)','O(1)',3),
3581:entry('count_odd_digit_word_letters',[('n','int')],'int',['strings','hash maps','counting'],['Spell every decimal digit of n as its lowercase English word and concatenate in digit order.','Count character frequencies in the concatenated text.','Return how many distinct letters have odd frequency.'],[([41],'fourone contains five letters with odd total frequency.'),([0],'zero has four distinct letters, each occurring once.')],[[n] for n in [0,1,2,9,10,11,41,99,101,123,909,2024,555,987654321]],ODD,[ODD.replace('count%2','count%2==0'),ODD.replace("for char in str(n)","for char in str(n)[:1]")],['Counts even-frequency letters.','Spells only the first digit.'],odd_letters_oracle,random_odd_letters,['Map each digit character to its fixed English word.','Concatenate words in original digit order.','Count letters across the complete result.','Sum one for each frequency with odd parity.'],'O(digits)','O(1)',3),
3582:entry('generate_video_caption_tag',[('caption','str')],'str',['strings','simulation'],['Split the caption into words and combine them in camelCase after a leading #.','Lowercase the first word; capitalize only the first letter of each later word and lowercase its remainder.','Remove non-English letters and truncate the final tag to at most 100 characters.'],[(['Leetcode daily streak achieved'],'The words become #leetcodeDailyStreakAchieved.'),(['  HELLO   world  '],'Whitespace is normalized and casing becomes #helloWorld.')],[[s] for s in ['a','Hello World','  HELLO   world  ','Leetcode daily streak achieved','ONE two THREE','abc DEF ghi','x y z','AlreadyCamel Case','spaces   between','Python 3 coding','UPPER lower','a'*120,'MiXeD CaSe Words','tag']],TAG,[TAG.replace("word.lower() if i==0","word.capitalize() if i==0"),TAG.replace("[:100]","[:99]")],['Capitalizes the first word instead of lowercasing it.','Limits the final tag to ninety-nine characters.'],tag_oracle,random_tag,['Split on whitespace to obtain words.','Normalize the first and later word casing separately.','Concatenate, retain letters, and prepend #.','Slice the complete tag to the maximum permitted length.'],'O(n)','O(n)',3),
3591:entry('has_prime_element_frequency',[('nums','list[int]')],'bool',['arrays','hash maps','math'],['Count how often each distinct array value occurs.','Return true if at least one occurrence count is prime.','One is not prime.'],[([[1,2,3,4,5,4]],'Value four occurs twice, and two is prime.'),([[1,2,3]],'Every value occurs once, so no frequency is prime.')],[[x] for x in [[1],[1,1],[1,2,3],[1,2,3,4,5,4],[1,1,1],[2,2,2,2],[1,1,2,2],[3,3,3,4],[5]*5,[1,1,1,1,2],[7,8,7,8,7],[0,0],[9,9,9,9,9,9],[1,2,2,3,3,3]]],PRIME,[PRIME.replace('value>1','value>=1'),PRIME.replace('any(','all(',1)],['Treats frequency one as prime.','Requires every distinct frequency to be prime.'],prime_oracle,random_prime,['Build an occurrence table.','Test a count for divisors only through its square root.','One is excluded; a larger count without a divisor is prime.','Return true as soon as any count passes that test.'],'O(n+d*sqrt n)','O(d)',3),
3602:entry('hexadecimal_and_base36_power_string',[('n','int')],'str',['math','base conversion','strings'],['Square n and encode the result in uppercase hexadecimal.','Cube n and encode the result in uppercase base 36 using digits then A through Z.','Concatenate the two encodings without a separator.'],[([13],'Thirteen squared is A9 in hexadecimal and cubed is 1P1 in base 36, producing A91P1.'),([1],'Both powers encode as one, producing 11.')],[[n] for n in [1,2,3,9,10,13,15,16,35,36,100,255,256,999]],BASE,[BASE.replace('convert(n*n,16)','convert(n*n,36)'),BASE.replace('convert(n*n*n,36)','convert(n*n*n,16)')],['Encodes the square in base 36.','Encodes the cube in hexadecimal.'],base_oracle,random_base,['Use repeated division to convert a nonnegative integer to a chosen base.','Map remainders 0-35 to uppercase digit symbols.','Convert n squared with base 16 and n cubed with base 36.','Concatenate in the required square-then-cube order.'],'O(log n)','O(log n)',3),
}
