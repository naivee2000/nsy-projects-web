"""Greater-value counts, directional mirrors, range medians, threshold tasks, and complete primes."""
from itertools import product
from math import isqrt
from .import_batch_055 import entry


def greater_oracle(args):
    nums,k=args;return sum(sum(other>value for other in nums)>=k for value in nums)

def random_greater(rng):
    n=rng.randint(1,16);return [[rng.randint(1,12) for _ in range(n)],rng.randrange(n)]

def mirror(value):return int(str(value)[::-1])
def mirror_oracle(args):
    nums=args[0];answer=None
    for first in range(len(nums)):
        for second in range(first+1,len(nums)):
            if mirror(nums[first])==nums[second]:
                distance=second-first;answer=distance if answer is None else min(answer,distance)
    return -1 if answer is None else answer

def random_mirror(rng):return [[rng.randint(1,999) for _ in range(rng.randint(1,18))]]

def equalize_oracle(args):
    nums,k,queries=args;answer=[]
    for left,right in queries:
        values=nums[left:right+1]
        if len({value%k for value in values})>1:answer.append(-1);continue
        normalized=sorted(value//k for value in values);median=normalized[len(normalized)//2]
        answer.append(sum(abs(value-median) for value in normalized))
    return answer

def random_equalize(rng):
    n=rng.randint(1,14);nums=[rng.randint(1,40) for _ in range(n)];k=rng.randint(1,8);queries=[]
    for _ in range(rng.randint(1,10)):
        left=rng.randrange(n);queries.append([left,rng.randint(left,n-1)])
    return [nums,k,queries]

def threshold_oracle(args):
    nums,limits=args;n=len(nums)
    best=0
    def visit(step,used,total):
        nonlocal best
        best=max(best,total)
        for index in range(n):
            if not (used>>index&1) and limits[index]<=step:visit(step+1,used|1<<index,total+nums[index])
    visit(1,0,0);return best

def random_threshold(rng):
    n=rng.randint(1,9);return [[rng.randint(1,20) for _ in range(n)],[rng.randint(1,n) for _ in range(n)]]

def prime(value):return value>=2 and all(value%factor for factor in range(2,isqrt(value)+1))
def complete_oracle(args):
    text=str(args[0]);return all(prime(int(text[:i])) and prime(int(text[-i:])) for i in range(1,len(text)+1))

def random_prime(rng):return [rng.randint(1,100000)]


GREATER='''def count_elements_with_k_greater(nums,k):
    if k==0:return len(nums)
    values=sorted(nums);threshold=values[len(values)-k]
    return sum(value<threshold for value in values)
'''

MIRROR='''def minimum_directional_mirror_distance(nums):
    def reverse(value):
        answer=0
        while value:answer=answer*10+value%10;value//=10
        return answer
    expected={};answer=None
    for index,value in enumerate(nums):
        if value in expected:
            distance=index-expected[value];answer=distance if answer is None else min(answer,distance)
        expected[reverse(value)]=index
    return -1 if answer is None else answer
'''

EQUALIZE='''def minimum_equalize_query_operations(nums,k,queries):
    residues=[value%k for value in nums];changes=[0]
    for index in range(1,len(nums)):changes.append(changes[-1]+(residues[index]!=residues[index-1]))
    values=[value//k for value in nums];ordered=sorted(set(values));position={value:index for index,value in enumerate(ordered)}
    left_child=[0];right_child=[0];count=[0];total=[0]
    def update(previous,low,high,target,value):
        node=len(count);left_child.append(left_child[previous]);right_child.append(right_child[previous]);count.append(count[previous]+1);total.append(total[previous]+value)
        if low<high:
            middle=(low+high)//2
            if target<=middle:left_child[node]=update(left_child[previous],low,middle,target,value)
            else:right_child[node]=update(right_child[previous],middle+1,high,target,value)
        return node
    roots=[0]
    for value in values:roots.append(update(roots[-1],0,len(ordered)-1,position[value],value))
    def kth(right_root,left_root,low,high,rank):
        if low==high:return low
        amount=count[left_child[right_root]]-count[left_child[left_root]];middle=(low+high)//2
        if rank<=amount:return kth(left_child[right_root],left_child[left_root],low,middle,rank)
        return kth(right_child[right_root],right_child[left_root],middle+1,high,rank-amount)
    def prefix(right_root,left_root,low,high,end):
        if end<low:return (0,0)
        if high<=end:return (count[right_root]-count[left_root],total[right_root]-total[left_root])
        middle=(low+high)//2;a=prefix(left_child[right_root],left_child[left_root],low,middle,end)
        if end<=middle:return a
        b=prefix(right_child[right_root],right_child[left_root],middle+1,high,end);return (a[0]+b[0],a[1]+b[1])
    answer=[]
    for start,end in queries:
        if changes[end]-changes[start]:answer.append(-1);continue
        length=end-start+1;middle_index=kth(roots[end+1],roots[start],0,len(ordered)-1,(length+1)//2);median=ordered[middle_index]
        left_count,left_sum=prefix(roots[end+1],roots[start],0,len(ordered)-1,middle_index)
        whole_sum=total[roots[end+1]]-total[roots[start]];right_count=length-left_count
        answer.append(median*left_count-left_sum+(whole_sum-left_sum)-median*right_count)
    return answer
'''

THRESHOLD='''def maximum_threshold_task_sum(nums,threshold):
    import heapq
    order=sorted(range(len(nums)),key=lambda index:threshold[index]);heap=[];position=0;step=1;answer=0
    while True:
        while position<len(order) and threshold[order[position]]<=step:
            heapq.heappush(heap,-nums[order[position]]);position+=1
        if not heap:break
        answer-=heapq.heappop(heap);step+=1
    return answer
'''

PRIME='''def is_complete_prime(num):
    from math import isqrt
    def prime(value):return value>=2 and all(value%factor for factor in range(2,isqrt(value)+1))
    text=str(num)
    return all(prime(int(text[:length])) and prime(int(text[-length:])) for length in range(1,len(text)+1))
'''

def lesson(a,b,c,d):return [a,b,c,d]

G_CASES=[[a,k] for a,k in (([1],0),([1,2,3],0),([1,2],1),([3,1,2],2),([5,5,5],1),([1,1,2,3],1),([1,2,2,3],2),([9,8,7,6],3),([4,4,5,6,6],2),([10,1,10,2,10,3],1),([2,7,3,7,4,7],3),([1,5,2,5,3,5,4],4))]
M_CASES=[[[*values]] for values in ([12,21],[21,120],[120,22],[12,21,45,33,55],[10,1],[101,101],[12,12,21],[100,1,10,1],[45,54,450,54],[7,7,7],[123,321,12,21],[90,9,900,9,99])]
Q_CASES=[[a,k,q] for a,k,q in (([1],1,[[0,0]]),([1,4,10],3,[[0,1],[0,2]]),([1,2,4],2,[[0,1],[1,2]]),([2,6,10,14],4,[[0,3],[1,2]]),([5,5,5],7,[[0,2],[1,1]]),([1,3,5,7],2,[[0,3],[0,2]]),([10,1,19],9,[[0,2],[1,2]]),([8,12,16,20,24],4,[[0,4],[1,3]]),([3,10,17,24],7,[[0,3],[2,3]]),([6,7,8,9],1,[[0,3],[1,2]]),([100,50,75,25],25,[[0,3],[1,3]]),([2,9,16,23,30],7,[[0,4],[0,3],[2,4]]))]
T_CASES=[[a,b] for a,b in (([1],[1]),([4,1,5,2,4],[3,3,2,3,3]),([2,6,10,13],[2,1,1,1]),([5,4,3],[1,2,3]),([9,1,8],[2,1,2]),([3,7,2,6],[1,3,2,4]),([10,9,8,7],[1,1,4,4]),([1,20,2,19,3],[5,1,4,2,3]),([6,5,4,3,2,1],[2,2,3,4,5,6]),([8,1,7,2,6,3],[1,6,2,5,3,4]),([11,22,33,44],[2,1,3,4]),([5,15,25,35,45],[3,2,1,5,4]))]
P_CASES=[[n] for n in (2,3,5,7,11,13,43,29,31,37,53,73)]

BATCH={
3759:entry('count_elements_with_k_greater',[('nums','list[int]'),('k','int')],'int',['arrays','sorting'],['nums contains up to 100,000 positive integers and 0≤k<n.','An occurrence qualifies only when at least k other occurrences have strictly greater values.','Return the number of qualified occurrences.'],[([[3,1,2],1],'Values one and two each have a larger element, so two qualify.'),([[5,5,5],2],'No value has any strictly larger occurrence, so none qualify.')],G_CASES,GREATER,[GREATER.replace('value<threshold','value<=threshold'),GREATER.replace('len(values)-k','len(values)-k-1')],['Counts values tied with the kth-largest threshold.','Uses the wrong order-statistic position for the threshold.'],greater_oracle,random_greater,lesson('For k>0, an occurrence qualifies exactly when it is below the kth-largest occurrence value.','Sort the array and read the value at index n-k as the strict threshold.','Count sorted values strictly smaller than that threshold; for k=0 every occurrence qualifies.','At least k positions lie at or above the threshold, and strict comparison correctly excludes ties that are not greater.'),'O(n log n)','O(n)',5),
3761:entry('minimum_directional_mirror_distance',[('nums','list[int]')],'int',['arrays','hash maps','math'],['nums contains up to 100,000 positive integers.','A pair i<j qualifies when reversing decimal nums[i] (dropping leading zeros) equals nums[j].','Return the minimum j-i, or negative one when no directional pair exists.'],[([[12,21,45,33,54]],'Pairs 12→21 and 45→54 have gaps one and two, so the minimum is one.'),([[120,21]],'Reversing the earlier 120 gives the later 21 at distance one.')],M_CASES,MIRROR,[MIRROR.replace('expected[reverse(value)]=index','expected[value]=index'),MIRROR.replace('expected[reverse(value)]=index','expected[reverse(value)]=expected.get(reverse(value),index)')],['Stores original values rather than the future reversed values being awaited.','Keeps the earliest producer of a reversed value instead of the latest and can miss a shorter gap.'],mirror_oracle,random_mirror,lesson('Scanning left to right handles the required direction i<j.','Map each reversed earlier value to the latest index that is waiting for that future value.','At index j, look up nums[j], update the minimum gap, then register reverse(nums[j]).','The latest matching producer always gives the smallest gap ending at j, and every directional pair is checked at its endpoint.'),'O(n·digits)','O(n)',5),
3762:entry('minimum_equalize_query_operations',[('nums','list[int]'),('k','int'),('queries','list[list[int]]')],'list[int]',['arrays','persistent segment trees','range queries'],['nums and queries each contain up to 40,000 entries and k is positive.','One operation changes one value by exactly +k or -k.','For each inclusive query, return minimum operations to equalize its values, or negative one if impossible.'],[([[1,4,7],3,[[0,1],[0,2]]],'Normalized values 0,1,2 require one and two median moves.'),([[1,2,4],2,[[0,2],[0,0],[1,2]]],'Mixed residues make the first query impossible; the others cost zero and one.')],Q_CASES,EQUALIZE,[EQUALIZE.replace('residues[index]!=residues[index-1]','residues[index]==residues[index-1]'),EQUALIZE.replace('(length+1)//2','1')],['Counts equal adjacent residues as incompatibility breaks.','Always chooses the smallest normalized value instead of a median.'],equalize_oracle,random_equalize,lesson('Values can meet only when all have the same remainder modulo k; then divide away k and minimize unit moves.','A prefix count of adjacent remainder changes tests feasibility for each range.','Persistent order-statistic trees find the range median and prefix count/sum, which give total absolute deviation.','The median minimizes absolute distance, and persistent root differences represent exactly the queried subarray.'),'O((n+q) log n)','O(n log n)',8),
3763:entry('maximum_threshold_task_sum',[('nums','list[int]'),('threshold','list[int]')],'int',['arrays','greedy','heaps'],['nums and threshold have equal length up to 100,000 and all nums are positive.','At step one and later, choose one unused index whose threshold is at most the current step; stop when none is available.','Maximize the total chosen value.'],[([[1,10,4,2,1,6],[5,1,5,5,2,2]],'The best eligible choices score 10, then 6, then 1 before the process blocks, totaling seventeen.'),([[4,1,5,2,3],[3,3,2,3,3]],'No task is eligible at step one, so the score is zero.')],T_CASES,THRESHOLD,[THRESHOLD.replace('heapq.heappush(heap,-nums[order[position]])','heapq.heappush(heap,nums[order[position]])'),THRESHOLD.replace('threshold[order[position]]<=step','threshold[order[position]]<step')],['Uses a min-heap and repeatedly chooses the smallest available value.','Requires thresholds to be strictly below the current step.'],threshold_oracle,random_threshold,lesson('Choosing a task always advances the step, so among currently eligible tasks only its value affects optimality.','Sort indices by threshold, add newly eligible values to a max-heap, and take the largest each step.','Stop exactly when the heap is empty before another threshold is unlocked.','An exchange argument replaces any smaller chosen eligible task with the heap maximum without changing future eligibility and never lowers the score.'),'O(n log n)','O(n)',6),
3765:entry('is_complete_prime',[('num','int')],'bool',['math','number theory'],['num is between one and one billion.','Every nonempty decimal prefix and every nonempty decimal suffix must be prime.','Single-digit inputs qualify exactly when that digit is prime.'],[([23],'Prefixes 2 and 23 and suffixes 3 and 23 are all prime.'),([39],'The full value 39 and suffix nine are composite, so it fails.')],P_CASES,PRIME,[PRIME.replace('value>=2','value>=1'),PRIME.replace("text[-length:]","text[:length]")],['Treats one as a prime number.','Checks prefixes twice and never validates suffixes.'],complete_oracle,random_prime,lesson('The number has only logarithmically many prefixes and suffixes.','Generate each decimal slice and test primality by trial division through its integer square root.','Return false on the first composite slice and true only after every length passes both sides.','The enumeration is exactly the definition, while trial division is a complete primality test for these bounded values.'),'O(digits·sqrt(num))','O(digits)',5),
}
