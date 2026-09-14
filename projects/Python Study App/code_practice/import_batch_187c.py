"""Easy binary, reverse-scan, triplet, arithmetic, and command-stream problems for batch 187."""
from itertools import permutations
from .import_batch_055 import entry as _entry

def entry(*args,**kwargs):
    """Accept source examples carrying a documented expected value; the builder recomputes it."""
    values=list(args)
    values[5]=[(item[0],item[-1]) for item in values[5]]
    return _entry(*values,**kwargs)

def odd_binary_oracle(a):
    s=a[0]
    return max((''.join(p) for p in set(permutations(s)) if p[-1]=='1'),default='')
def random_odd_binary(r):
    n=r.randint(1,8);ones=r.randint(1,n);chars=['1']*ones+['0']*(n-ones);r.shuffle(chars);return [''.join(chars)]
def collect_oracle(a):
    nums,k=a;needed=set(range(1,k+1))
    for count,value in enumerate(reversed(nums),1):
        needed.discard(value)
        if not needed:return count
def random_collect(r):
    k=r.randint(1,10);prefix=[r.randint(1,20) for _ in range(r.randint(0,20))];tail=list(range(1,k+1));r.shuffle(tail);return [prefix+tail,k]
def triplet_oracle(a):
    nums=a[0];best=0
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            for k in range(j+1,len(nums)):best=max(best,(nums[i]-nums[j])*nums[k])
    return best
def random_triplet(r):return [[r.randint(1,100) for _ in range(r.randint(3,20))]]
def difference_oracle(a):
    n,m=a;yes=no=0
    for value in range(1,n+1):
        if value%m==0:yes+=value
        else:no+=value
    return no-yes
def random_difference(r):return [r.randint(1,1000),r.randint(1,1000)]
def visited_oracle(a):
    numbers=[];answer=[];previous=0
    for value in a[0]:
        if value==-1:
            previous+=1;answer.append(numbers[-previous] if previous<=len(numbers) else -1)
        else:numbers.append(value);previous=0
    return answer
def random_visited(r):
    words=[];seen=0
    for _ in range(r.randint(1,50)):
        if r.random()<.45:words.append(-1)
        else:words.append(r.randint(1,100));seen+=1
    return [words]

ODD='''\
def maximum_odd_binary_number(s):
    ones=s.count('1')
    return '1'*(ones-1)+'0'*(len(s)-ones)+'1'
'''
COLLECT='''\
def operations_to_collect_one_through_k(nums,k):
    needed=set(range(1,k+1))
    for operations,value in enumerate(reversed(nums),1):
        needed.discard(value)
        if not needed:return operations
'''
TRIPLET='''\
def maximum_ordered_triplet_value(nums):
    largest=nums[0];best_difference=0;answer=0
    for value in nums[1:]:
        answer=max(answer,best_difference*value)
        best_difference=max(best_difference,largest-value)
        largest=max(largest,value)
    return answer
'''
DIFFERENCE='''\
def nondivisible_minus_divisible_sum(n,m):
    total=n*(n+1)//2
    count=n//m
    divisible=m*count*(count+1)//2
    return total-2*divisible
'''
VISITED='''\
def last_visited_integers(words):
    numbers=[];answer=[];offset=0
    for word in words:
        if word==-1:
            offset+=1;answer.append(numbers[-offset] if offset<=len(numbers) else -1)
        else:
            numbers.append(word);offset=0
    return answer
'''

BATCH={
2864:entry('maximum_odd_binary_number',[('s','str')],'str',['strings','greedy','sorting'],['Rearrange all bits of a binary string without adding or removing any.','The input contains at least one 1, so an odd rearrangement always exists.','Return the numerically largest odd binary string of the same length.'],[(['010'],'The only odd arrangement with the largest leading bits is 001.'),(['0101'],'Reserve one 1 for the final odd bit and place the other 1 first, producing 1001.')],[[s] for s in ['1','01','10','11','001','101','111','0001','1000','1100','10101','111000','010101','111111']],ODD,[ODD.replace("'1'*(ones-1)","'1'*ones"),ODD.replace("+'1'","+'0'")],['Uses every one in the prefix and therefore changes the output length/counts.','Places zero at the end, producing an even number.'],odd_binary_oracle,random_odd_binary,['An odd binary number must reserve one 1 for its final bit.','For the largest value, put every remaining 1 in the most significant positions.','Then place all zeros followed by the reserved final 1.','Any zero before an available prefix one makes the binary number smaller, so this arrangement is lexicographically and numerically maximal.'],'O(n)','O(n)',3),
2869:entry('operations_to_collect_one_through_k',[('nums','list[int]'),('k','int')],'int',['arrays','sets','reverse traversal'],['One operation removes the final element of nums.','Continue until every integer from one through k has been removed at least once.','Return the number of removals required; the input guarantees all required values occur.'],[([[3,1,5,4,2],2],4,'Removing 2,4,5,1 takes four operations and has then collected one and two.'),([[3,1,5,4,2],5],5,'All five removals are needed to see every value one through five.')],[[nums,k] for nums,k in [([1],1),([1,2],1),([1,2],2),([2,1],1),([2,1],2),([1,1,1],1),([3,2,1],2),([1,2,3,4],3),([4,3,2,1],4),([9,1,2,1],2),([5,4,3,2,1],3),([1,5,2,5,3],3),([10,9,1,2,3],3),([2,2,1,3,2],3)]],COLLECT,[COLLECT.replace('reversed(nums)','nums'),COLLECT.replace('needed.discard(value)','needed.remove(value) if value in needed else None')],['Scans from the front rather than removing from the end.','The altered control is paired with a stopping defect below.'],collect_oracle,random_collect,['Track the required values not yet encountered.','Traverse nums backward because removal always comes from the end.','Discard each removed value from the required set and stop when it becomes empty.','The first empty-set moment is exactly the shortest suffix containing every value one through k.'],'O(n+k)','O(k)',3),
2873:entry('maximum_ordered_triplet_value',[('nums','list[int]')],'int',['arrays','prefix maxima','greedy'],['Choose indices i<j<k and evaluate (nums[i]-nums[j])*nums[k].','Return the maximum value among all ordered triplets.','Return zero when every triplet value is negative.'],[([[12,6,1,2,7]],77,'Indices zero, two, and four give (12-1)*7=77.'),([[1,10,3,4,19]],133,'Indices one, two, and four give (10-3)*19=133.')],[[x] for x in [[1,2,3],[3,2,1],[1,1,1],[5,1,5],[2,3,1],[10,1,2],[1,10,1],[9,2,3,8],[4,7,2,9],[100,1,100],[5,4,3,2],[2,8,1,7],[6,1,5,2,4],[1,2,10,3,4]]],TRIPLET,[TRIPLET.replace('best_difference=0','best_difference=largest'),TRIPLET.replace('largest-value','value-largest')],['Treats a prefix value itself as an already formed difference.','Reverses the subtraction order required by i before j.'],triplet_oracle,random_triplet,['Before each k, retain the best difference nums[i]-nums[j] formed entirely to its left.','Also retain the largest prefix value to update that difference when j advances.','Use the current value as k before incorporating it into the prefix states.','The maintained maximum covers every valid i,j pair, so multiplying it at each later k examines the best triplet ending there.'],'O(n)','O(1)',3),
2894:entry('nondivisible_minus_divisible_sum',[('n','int'),('m','int')],'int',['math','arithmetic series'],['Consider every integer from one through n.','Let num1 be the sum of values not divisible by m and num2 the sum of values divisible by m.','Return num1-num2.'],[([10,3],19,'The nonmultiples sum to 37 and multiples 3+6+9 sum to 18, giving 19.'),([5,6],15,'No value through five is divisible by six, so the answer is their total 15.')],[[n,m] for n,m in [(1,1),(1,2),(2,1),(5,2),(5,5),(5,6),(10,3),(10,10),(10,11),(100,7),(20,4),(50,1),(50,100),(999,31)]],DIFFERENCE,[DIFFERENCE.replace('total-2*divisible','total-divisible'),DIFFERENCE.replace('count=n//m','count=(n-1)//m')],['Subtracts divisible values only once even though they must move from the total into the negative group.','Omits n itself when n is divisible by m.'],difference_oracle,random_difference,['Start with the sum of all integers one through n.','Multiples of m are m,2m,...,floor(n/m)m, whose sum is an arithmetic series.','Because those values should be negative rather than positive, subtract their sum twice from the total.','This partitions the full range into the two requested groups and applies the correct sign to each.'],'O(1)','O(1)',3),
2899:entry('last_visited_integers',[('words','list[str]')],'list[int]',['arrays','simulation','strings'],['Each word is either a positive integer string or prev.','An integer becomes the newest visited value and resets the consecutive-prev counter.','The first prev returns the newest integer, the second consecutive prev the second-newest, and so on; return -1 when unavailable.'],[([['1','2','prev','prev','prev']],[2,1,-1],'The three queries request the newest, second-newest, and a missing third value.'),([['1','prev','2','prev','prev']],[1,2,1],'Reading 2 resets the offset before the final two queries.')],[[x] for x in [[['prev']],[['1']],[['1','prev']],[['1','prev','prev']],[['1','2','prev']],[['1','2','prev','prev']],[['1','prev','2','prev']],[['5','6','7','prev','prev']],[['prev','1','prev']],[['1','prev','prev','2','prev']],[['10','20','30','prev','40','prev']],[['1','2','3','prev','prev','prev']],[['9','prev','prev','prev','10']],[['4','5','prev','6','prev','prev']]]],VISITED,[VISITED.replace('offset=0','offset=-1',1),VISITED.replace("numbers[-offset]","numbers[offset]")],['Starts the query offset incorrectly.','Indexes from the front instead of counting backward from the newest visit.'],visited_oracle,random_visited,['Store integer visits in their original order.','Track how many prev commands have occurred since the last integer.','For a query, use that count as a one-based offset from the end; reset it when an integer arrives.','The list is the complete visit history and the offset exactly encodes which most-recent entry the current query requests.'],'O(n)','O(number of integers)',3),
}
BATCH[2869]['wrong'][1]=COLLECT.replace('if not needed','if len(needed)<=1')
BATCH[2899].update(
    params=[('nums','list[int]','raw')],
    constraints=['Each element is either -1 or a positive integer.','A positive integer becomes the newest visited value and resets the consecutive -1 counter.','The first -1 returns the newest positive value, the second consecutive -1 the second-newest, and so on; return -1 when unavailable.'],
    examples=[([[1,2,-1,-1,-1]],'The three queries request the newest, second-newest, and a missing third value.'),([[1,-1,2,-1,-1]],'Reading 2 resets the offset before the final two queries.')],
    boundaries=[[x] for x in [[-1],[1],[1,-1],[1,-1,-1],[1,2,-1],[1,2,-1,-1],[1,-1,2,-1],[5,6,7,-1,-1],[-1,1,-1],[1,-1,-1,2,-1],[10,20,30,-1,40,-1],[1,2,3,-1,-1,-1],[9,-1,-1,-1,10],[4,5,-1,6,-1,-1]]],
    reference=VISITED,
    wrong=[VISITED.replace('offset=0','offset=-1',1),VISITED.replace('numbers[-offset]','numbers[offset]')],
)
BATCH[2899]['wrong'][0]=VISITED.replace('offset=0','offset=1')
