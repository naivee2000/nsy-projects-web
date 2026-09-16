"""Seat probability, number encoding, binary pairs, Frobenius cost, and XOR flips."""
from fractions import Fraction
from functools import reduce
from operator import xor
from .import_batch_055 import entry

def seat_oracle(a):
    n=a[0]
    # Exact state enumeration checks every seeded small case. For larger n,
    # symmetry leaves the last assigned seat and the first passenger's seat
    # equally likely to be the final unclaimed one.
    if n>5:return 0.5
    states={(tuple(range(n)),0):Fraction(1)}
    for passenger in range(n):
        nxt={}
        for (free,_),probability in states.items():
            choices=free if passenger==0 or passenger not in free else (passenger,)
            for seat in choices:
                remain=tuple(x for x in free if x!=seat);key=(remain,seat)
                nxt[key]=nxt.get(key,Fraction())+probability/len(choices)
        states=nxt
    return float(sum(p for (free,last),p in states.items() if last==n-1))
def random_seat(r):return [r.randint(1,5)]
def encode_oracle(a):
    values=[''];level=['0','1']
    while len(values)<=a[0]:values.extend(level);level=[x+c for x in level for c in '01']
    return values[a[0]]
def random_encode(r):return [r.randint(0,10000)]
def changes_oracle(a):return sum(a[0][i]!=a[0][i+1] for i in range(0,len(a[0]),2))
def random_changes(r):return [''.join(r.choice('01') for _ in range(2*r.randint(1,50)))]
def expensive_oracle(a):
    p,q=a;reachable={i*p+j*q for i in range(q) for j in range(p)}
    return max(x for x in range(p*q) if x not in reachable)
def random_expensive(r):
    primes=[2,3,5,7,11,13,17,19];p,q=r.sample(primes,2);return [p,q]
def xor_flips_oracle(a):
    value=reduce(xor,a[0],0)^a[1];answer=0
    while value:answer+=value&1;value>>=1
    return answer
def random_xor_flips(r):return [[r.randint(0,1000) for _ in range(r.randint(1,30))],r.randint(0,1023)]

SEAT='''def last_passenger_seat_probability(n):
    return 1.0 if n==1 else 0.5
'''
ENCODE='''def encode_secret_number(num):
    return bin(num+1)[3:]
'''
CHANGES='''def minimum_beautiful_binary_changes(s):
    return sum(s[i]!=s[i+1] for i in range(0,len(s),2))
'''
EXPENSIVE='''def most_expensive_unbuyable_item(primeOne,primeTwo):
    return primeOne*primeTwo-primeOne-primeTwo
'''
XOR_FLIPS='''def minimum_xor_bit_flips(nums,k):
    from functools import reduce
    from operator import xor
    return reduce(xor,nums,k).bit_count()
'''

BATCH={
1227:entry('last_passenger_seat_probability',[('n','int')],'float',['probability','math'],['Passenger one chooses a random seat; later passengers take their own seat when free and otherwise choose randomly.','There are exactly n passengers and seats.','Return the probability that the last passenger gets their assigned seat.'],[([1],'The only passenger necessarily sits in the only assigned seat.'),([2],'The first passenger chooses either seat equally, so the last succeeds with probability one half.')],[[n] for n in [1,2,3,4,5,6,7,8,10,25,100,1000,10000,100000]],SEAT,[SEAT.replace('n==1','n<=2'),SEAT.replace('0.5','0.0')],['Returns certainty for two passengers.','Claims the last passenger always fails once n exceeds one.'],seat_oracle,random_seat,['Only the first passenger’s seat and the last passenger’s seat matter as absorbing choices.','Intermediate displaced passengers preserve symmetry between those two outcomes.','Return one for n=1 and one half otherwise.','The random displacement chain ends at either special seat with equal probability.'],'O(1)','O(1)',5),
1256:entry('encode_secret_number',[('num','int')],'str',['math','binary strings'],['Enumerate codewords by increasing length, and lexicographically within a length, beginning with the empty code for zero.','Return the codeword at zero-based index num.','Equivalently use the binary representation of num+1 without its leading one.'],[([23],'Twenty-four is binary 11000; removing its leading one gives 1000.'),([0],'The first codeword is the empty string.')],[[n] for n in [0,1,2,3,4,5,6,7,8,15,16,23,100,999]],ENCODE,[ENCODE.replace('num+1','num'),ENCODE.replace('[3:]','[2:]')],['Uses num rather than num+1 and shifts the enumeration.','Keeps the leading one instead of removing it.'],encode_oracle,random_encode,['Adding one maps the zero-based breadth-first code index to a positive binary integer.','The leading binary one records the completed shorter levels.','Remove that leading one.','The remaining bits are exactly the within-level lexicographic code.'],'O(log num)','O(log num)',5),
2914:entry('minimum_beautiful_binary_changes',[('s','str')],'int',['strings','greedy'],['s has even length.','A beautiful result can be divided into even-length blocks of equal characters.','Return the fewest single-character changes needed.'],[(['1001'],'Both pairs 10 and 01 need one change, totaling two.'),(['0000'],'The whole string is already a valid even constant block.')],[[s] for s in ['00','01','10','11','1001','0000','0101','0011','1100','111000','101010','000111','0110','110011']],CHANGES,[CHANGES.replace('range(0,len(s),2)','range(2,len(s),2)'),CHANGES.replace('s[i]!=s[i+1]','s[i]==s[i+1]')],['Ignores the first fixed pair.','Counts already-equal pairs rather than mismatched pairs.'],changes_oracle,random_changes,['Any valid even-block partition respects the fixed pairs (0,1),(2,3), and so on.','A mismatched pair needs exactly one change; a matched pair needs none.','Count mismatched fixed pairs.','After fixing each pair, grouping adjacent equal pairs into larger even blocks is always valid.'],'O(n)','O(1)',3),
2979:entry('most_expensive_unbuyable_item',[('primeOne','int'),('primeTwo','int')],'int',['math','number theory'],['primeOne and primeTwo are distinct primes and unlimited coins of both values are available.','An item is buyable when its price is a nonnegative combination of the two denominations.','Return the greatest positive price that is not buyable.'],[([2,5],'Prices one and three are unreachable, and three is the greatest.'),([3,5],'Seven is the Frobenius number for denominations three and five.')],[[p,q] for p,q in [(2,3),(2,5),(3,5),(3,7),(5,7),(2,11),(5,11),(7,11),(11,13),(3,13),(13,17),(5,19),(17,19),(2,97)]],EXPENSIVE,[EXPENSIVE.replace('-primeTwo','+primeTwo'),EXPENSIVE.replace('primeOne*primeTwo','primeOne+primeTwo')],['Adds one denomination instead of subtracting it.','Uses a sum where the product term is required.'],expensive_oracle,random_expensive,['Two distinct primes are coprime.','For coprime denominations p and q, the Frobenius number is pq-p-q.','Evaluate that closed form.','Every larger integer has a nonnegative representation, while this value cannot have one modulo either denomination.'],'O(1)','O(1)',5),
2997:entry('minimum_xor_bit_flips',[('nums','list[int]'),('k','int')],'int',['bit manipulation','arrays'],['Flip any individual bit in any array element.','Make the XOR of all elements equal k.','Return the minimum number of bit flips.'],[([[2,1,3,4],1],'The current XOR differs from one in two bit positions, so two flips suffice.'),([[1,2,3],0],'The current XOR is already zero.')],[[n,k] for n,k in [([2,1,3,4],1),([1,2,3],0),([0],0),([0],7),([1],2),([5,5],0),([7,3],4),([1,1,1],1),([8,4,2,1],15),([10,20],30),([31],0),([3,6,9],12),([100,200,300],400),([0,0,1],0)]],XOR_FLIPS,[XOR_FLIPS.replace('reduce(xor,nums,k)','reduce(xor,nums,0)'),XOR_FLIPS.replace('.bit_count()','>>1 .bit_count()')],['Ignores the target k and only counts current XOR bits.','Drops the lowest differing bit before counting.'],xor_flips_oracle,random_xor_flips,['XOR all nums together, then XOR with k to mark differing target bits.','One input-bit flip changes exactly one bit of the aggregate XOR.','Count set bits in that difference mask.','Every differing bit needs one flip, and flipping it in any one element is sufficient.'],'O(n)','O(1)',5),
}
