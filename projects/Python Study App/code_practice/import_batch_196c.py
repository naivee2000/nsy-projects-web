"""Box choice, unique evens, comma counts, parity construction, and index distance."""
from collections import Counter
from .import_batch_055 import entry

def box_oracle(a):
    capacity,size=a;return min((i for i,v in enumerate(capacity) if v>=size),key=lambda i:(capacity[i],i),default=-1)
def random_box(r):return [[r.randint(1,100) for _ in range(r.randint(1,30))],r.randint(1,100)]
def unique_oracle(a):
    c=Counter(a[0]);return next((v for v in a[0] if v%2==0 and c[v]==1),-1)
def random_unique(r):return [[r.randint(0,20) for _ in range(r.randint(1,40))]]
def commas_oracle(a):return sum(max(0,a[0]-10**power+1) for power in range(3,len(str(a[0]))+1,3))
def random_commas(r):return [r.randint(1,2000000)]
def parity_oracle(a):
    nums=a[0]
    if len(nums)<=1:return True
    return all(v%2==nums[0]%2 for v in nums) or any(v%2 for v in nums)
def random_parity(r):return [r.sample(range(1,100),r.randint(1,15))]
def distance_oracle(a):
    nums=a[0];return min((abs(i-j) for i,v in enumerate(nums) if v==1 for j,w in enumerate(nums) if w==2),default=-1)
def random_distance(r):return [[r.randint(0,2) for _ in range(r.randint(1,50))]]

BOX='''def minimum_capacity_box_index(capacity,itemSize):
    candidates=[i for i,value in enumerate(capacity) if value>=itemSize]
    return min(candidates,key=lambda i:(capacity[i],i),default=-1)
'''
UNIQUE='''def first_unique_even_element(nums):
    from collections import Counter
    counts=Counter(nums)
    return next((value for value in nums if value%2==0 and counts[value]==1),-1)
'''
COMMAS='''def total_standard_format_commas(n):
    answer=0;threshold=1000
    while threshold<=n:
        answer+=n-threshold+1
        threshold*=1000
    return answer
'''
PARITY='''def can_construct_uniform_parity_array(nums1):
    return True
'''
DISTANCE='''def minimum_one_two_index_distance(nums):
    last_one=last_two=None;answer=None
    for i,value in enumerate(nums):
        if value==1:
            if last_two is not None:answer=i-last_two if answer is None else min(answer,i-last_two)
            last_one=i
        elif value==2:
            if last_one is not None:answer=i-last_one if answer is None else min(answer,i-last_one)
            last_two=i
    return -1 if answer is None else answer
'''

BATCH={
3861:entry('minimum_capacity_box_index',[('capacity','list[int]'),('itemSize','int')],'int',['arrays','greedy'],['Choose a box whose capacity is at least itemSize.','Minimize chosen capacity, breaking equal-capacity ties by smaller index.','Return -1 when no box fits.'],[([[1,5,3,7],3],'Capacity three at index two is the smallest fitting box.'),([[2,2,5],2],'The equal minimum fits at indices zero and one, so choose zero.')],[[c,s] for c,s in [([1],1),([1],2),([1,5,3,7],3),([2,2,5],2),([5,3,4],2),([5,3,4],4),([10,1],5),([4,4,4],4),([1,2,3],3),([9,7,8],6),([2,10,3],9),([100,50],50),([6,5,6],6),([1,9,2,8],7)]],BOX,[BOX.replace('value>=itemSize','value>itemSize'),BOX.replace('(capacity[i],i)','(i,capacity[i])')],['Rejects an exact-capacity fit.','Minimizes index before capacity.'],box_oracle,random_box,['Filter indices whose capacities meet the size.','Rank fitting indices by capacity then index.','Return the minimum-ranked index.','An empty candidate list yields the required -1.'],'O(n)','O(n)',3),
3866:entry('first_unique_even_element',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['Find an even value whose total array frequency is exactly one.','Return the first such value in original order.','Return -1 when none exists.'],[([[3,4,2,5,4,6]],'Four repeats; two is the first unique even value.'),([[1,3,5]],'No even value exists, so return -1.')],[[x] for x in [[2],[1],[2,2],[1,3,5],[3,4,2,5,4,6],[0,1],[0,0],[4,6,4],[2,3,6],[8,8,10],[1,2,4],[6,5,2,6],[9,8,7],[12,14,12]]],UNIQUE,[UNIQUE.replace('counts[value]==1','counts[value]>=1'),UNIQUE.replace('value%2==0','value%2==1')],['Accepts repeated even values.','Searches for unique odd values.'],unique_oracle,random_unique,['Count all values first.','Scan nums from left to right.','Return the first value that is even and has count one.','If the scan finishes, the sentinel -1 is required.'],'O(n)','O(n)',3),
3870:entry('total_standard_format_commas',[('n','int')],'int',['math','counting'],['Format every integer from one through n with commas after each three-digit group.','Count all comma characters used across those formatted integers.','Return the total.'],[([1002],'Numbers 1000, 1001, and 1002 each use one comma, totaling three.'),([999],'No number through 999 uses a comma.')],[[n] for n in [1,9,999,1000,1001,1002,1999,9999,10000,999999,1000000,1000001,1500000,2000000]],COMMAS,[COMMAS.replace('n-threshold+1','n-threshold'),COMMAS.replace('threshold*=1000','threshold*=100')],['Omits the threshold value itself at every comma level.','Introduces new comma levels every two digits.'],commas_oracle,random_commas,['Every number at least 1000 contributes its first comma.','Every number at least one million contributes one additional comma, and so on by factors of 1000.','At a threshold t, exactly n-t+1 values contribute that comma.','Sum these contributions for all thresholds no greater than n.'],'O(log n)','O(1)',3),
3875:entry('can_construct_uniform_parity_array',[('nums1','list[int]')],'bool',['arrays','parity','constructive'],['For every output position, either keep its original distinct value or subtract another input value from it.','Determine whether all constructed values can share one parity.','Return whether such a construction exists.'],[([[2,3]],'Keep odd three and replace two by two minus three, which is odd.'),([[2,4,6]],'Keeping all values already gives uniform even parity.')],[[x] for x in [[1],[2],[2,3],[2,4,6],[1,3,5],[1,2,3],[4,7,10],[8,2,5],[9,6],[1,4],[10,11,12,13],[3,8,14],[5,2,4],[7,9,2,6]]],PARITY,[PARITY.replace('return True','return all(v%2==nums1[0]%2 for v in nums1)'),PARITY.replace('return True','return len(nums1)==1')],['Allows only already-uniform inputs.','Claims only single-element arrays are constructible.'],parity_oracle,random_parity,['If all values share parity, keep them unchanged.','Otherwise at least one odd value exists.','Keep every odd value; for each even value subtract any odd input, producing odd.','Thus a uniform construction always exists under the allowed choices.'],'O(1)','O(1)',3),
3880:entry('minimum_one_two_index_distance',[('nums','list[int]')],'int',['arrays','indices'],['nums contains only zero, one, and two.','Return the minimum absolute index difference between an occurrence of one and an occurrence of two.','Return -1 if either value is absent.'],[([[1,0,0,2,0,1]],'The two at index three is two positions from the one at index five.'),([[0,1,0]],'No two exists, so return -1.')],[[x] for x in [[1],[2],[0],[1,2],[2,1],[0,1,0],[1,0,0,2,0,1],[1,0,2],[2,0,1],[1,1,2,2],[0,0,0],[2,0,0,0,1],[1,2,1,2],[0,2,0,1,0]]],DISTANCE,[DISTANCE.replace('min(answer,i-last_two)','max(answer,i-last_two)'),DISTANCE.replace('i-last_one','i-last_one+1')],['Keeps the greatest later distance after initialization.','Adds one to distances measured from a preceding one.'],distance_oracle,random_distance,['Track the latest indices of one and two.','When one appears, compare it with the latest two; do the symmetric check for a two.','The nearest opposite value to the left is always its latest occurrence.','Taking the minimum of these crossing distances finds the global minimum.'],'O(n)','O(1)',3),
}
