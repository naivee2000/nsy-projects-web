"""Disjoint subarrays, generated strings, task profits, grouped top-k, and fruit baskets."""
from itertools import product

from .import_batch_055 import entry


def subarrays_oracle(args):
    nums,k,m=args;n=len(nums);best=-10**30
    def choose(start,remaining,total):
        nonlocal best
        if remaining==0:best=max(best,total);return
        for left in range(start,n):
            for right in range(left+m,n+1):choose(right,remaining-1,total+sum(nums[left:right]))
    choose(0,k,0);return best


def random_subarrays(rng):
    n=rng.randint(1,10);m=rng.randint(1,n);k=rng.randint(1,n//m)
    return [[rng.randint(-9,9) for _ in range(n)],k,m]


def generated_oracle(args):
    flags,target=args;length=len(flags)+len(target)-1;alphabet=sorted(set(target)|{'a','b'})
    for letters in product(alphabet,repeat=length):
        word=''.join(letters)
        if all((word[i:i+len(target)]==target)==(flag=='T') for i,flag in enumerate(flags)):return word
    return ''


def random_generated(rng):
    flags=''.join(rng.choice('TF') for _ in range(rng.randint(1,4)));target=''.join(rng.choice('ab') for _ in range(rng.randint(1,3)))
    return [flags,target]


def profit_oracle(args):
    workers,tasks=args;best=0;used=[False]*len(workers)
    def assign(index,extra,total):
        nonlocal best
        if index==len(tasks):best=max(best,total);return
        assign(index+1,extra,total);skill,profit=tasks[index]
        for worker,value in enumerate(workers):
            if not used[worker] and value==skill:
                used[worker]=True;assign(index+1,extra,total+profit);used[worker]=False
        if not extra:assign(index+1,True,total+profit)
    assign(0,False,0);return best


def random_profit(rng):
    return [[rng.randint(1,4) for _ in range(rng.randint(1,6))],[[rng.randint(1,5),rng.randint(1,20)] for _ in range(rng.randint(1,7))]]


def sums_oracle(args):
    nums1,nums2,k=args
    return [sum(sorted((nums2[j] for j in range(len(nums1)) if nums1[j]<nums1[i]),reverse=True)[:k]) for i in range(len(nums1))]


def random_sums(rng):
    n=rng.randint(1,15);return [[rng.randint(1,10) for _ in range(n)],[rng.randint(1,20) for _ in range(n)],rng.randint(1,n)]


def fruit_oracle(args):
    fruits,baskets=args;available=[True]*len(baskets);unplaced=0
    for fruit in fruits:
        index=next((i for i,capacity in enumerate(baskets) if available[i] and capacity>=fruit),-1)
        if index<0:unplaced+=1
        else:available[index]=False
    return unplaced


def random_fruit(rng):
    n=rng.randint(1,15);return [[rng.randint(1,20) for _ in range(n)],[rng.randint(1,20) for _ in range(n)]]


SUBARRAYS='''def maximum_k_disjoint_subarray_sum(nums,k,m):
    n=len(nums);prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    previous=[0]*(n+1);negative=-10**30
    for _ in range(k):
        current=[negative]*(n+1);best=negative
        for end in range(1,n+1):
            current[end]=current[end-1]
            if end>=m:
                start=end-m;best=max(best,previous[start]-prefix[start]);current[end]=max(current[end],prefix[end]+best)
        previous=current
    return previous[n]
'''

GENERATED='''def lexicographically_smallest_generated_string(str1,str2):
    length=len(str1)+len(str2)-1;answer=['a']*length;fixed=[False]*length
    for start,flag in enumerate(str1):
        if flag=='T':
            for offset,char in enumerate(str2):
                index=start+offset
                if fixed[index] and answer[index]!=char:return ''
                answer[index]=char;fixed[index]=True
    for start,flag in enumerate(str1):
        if flag=='F' and ''.join(answer[start:start+len(str2)])==str2:
            for index in range(start+len(str2)-1,start-1,-1):
                if not fixed[index]:answer[index]='b';break
            else:return ''
    return ''.join(answer)
'''

PROFIT='''def maximum_exact_skill_task_profit(workers,tasks):
    import heapq
    available={}
    for skill,profit in tasks:heapq.heappush(available.setdefault(skill,[]),-profit)
    answer=0
    for skill in workers:
        if available.get(skill):answer-=heapq.heappop(available[skill])
    extra=max((-heap[0] for heap in available.values() if heap),default=0)
    return answer+extra
'''

SUMS='''def maximum_smaller_key_sums(nums1,nums2,k):
    import heapq
    ordered=sorted((value,index) for index,value in enumerate(nums1));answer=[0]*len(nums1);heap=[];total=0;added=0
    for position,(value,index) in enumerate(ordered):
        while added<position and ordered[added][0]<value:
            candidate=nums2[ordered[added][1]];heapq.heappush(heap,candidate);total+=candidate
            if len(heap)>k:total-=heapq.heappop(heap)
            added+=1
        answer[index]=total
    return answer
'''

FRUIT='''def count_unplaced_fruits(fruits,baskets):
    n=len(baskets);tree=[0]*(4*n)
    def build(node,left,right):
        if left==right:tree[node]=baskets[left];return
        middle=(left+right)//2;build(node*2,left,middle);build(node*2+1,middle+1,right);tree[node]=max(tree[node*2],tree[node*2+1])
    def take(node,left,right,value):
        if tree[node]<value:return False
        if left==right:tree[node]=0;return True
        middle=(left+right)//2
        found=take(node*2,left,middle,value) if tree[node*2]>=value else take(node*2+1,middle+1,right,value)
        tree[node]=max(tree[node*2],tree[node*2+1]);return found
    build(1,0,n-1)
    return sum(not take(1,0,n-1,fruit) for fruit in fruits)
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


SUBARRAY_CASES=[[nums,k,m] for nums,k,m in [([1,2,-1,3,3,4],2,2),([1],1,1),([-5],1,1),([1,2,3],1,2),([-1,-2,-3],1,1),([5,-10,5,-10,5],2,1),([1,2,3,4],2,2),([4,-1,2,-7,3,4],2,2),([10,-2,-3,10],2,1),([0,0,0,0],2,1),([2,-1,2,-1,2,-1],3,1),([9,1,-20,8,2,7],2,2),([-5,10,-5,10,-5],1,3),([3,4,-2,5,-1,6,2],2,3)]]
GENERATED_CASES=[[flags,target] for flags,target in [('TFTF','ab'),('TT','a'),('F','a'),('T','z'),('TF','aa'),('FT','ab'),('TT','ab'),('FFF','a'),('TFT','aba'),('FTF','bb'),('TFF','abc'),('FFTT','a'),('TFTF','ba'),('FFFF','ab')]]
PROFIT_CASES=[[workers,tasks] for workers,tasks in [([1,2,3,4,5],[[1,100],[2,400],[3,100],[3,400]]),([1],[[2,10]]),([1],[[1,5]]),([1],[[1,5],[1,9]]),([1,1],[[1,5],[1,9],[2,20]]),([2,3],[[2,7],[3,8],[4,9]]),([1,2],[[1,10],[1,8],[2,7]]),([3,3,3],[[3,1],[3,2],[3,3],[3,4]]),([1,4],[[2,100],[3,90]]),([1,2,3],[[1,5],[2,6],[3,7],[4,20]]),([2],[[2,10],[3,100],[2,9]]),([5,5],[[5,4],[5,8],[1,20]]),([1,2,2],[[2,5],[2,6],[2,7],[1,1]]),([4,3,2,1],[[1,9],[2,8],[3,7],[4,6],[5,10]])]]
SUM_CASES=[[a,b,k] for a,b,k in [([4,2,1,5,3],[10,20,30,40,50],2),([1],[5],1),([1,1],[5,7],1),([2,1],[3,4],1),([3,2,1],[1,2,3],2),([1,2,3],[10,1,1],1),([5,4,3,2,1],[1,2,3,4,5],3),([2,2,3],[9,8,7],2),([10,1,9,2],[4,10,5,8],2),([1,3,2,4],[5,6,7,8],4),([4,1,4,1],[3,9,8,7],2),([6,5,4,3,2,1],[6,5,4,3,2,1],1),([2,7,3,8,4],[10,1,9,2,8],3),([1,5,2,6,3,7],[7,6,5,4,3,2],2)]]
FRUIT_CASES=[[fruits,baskets] for fruits,baskets in [([4,2,5],[3,5,4]),([1],[1]),([2],[1]),([1,2],[2,1]),([2,1],[1,2]),([3,3,3],[3,3,3]),([5,1,4],[4,5,1]),([2,4,1],[3,3,4]),([10,2,8,1],[9,10,2,8]),([1,1,2,2],[1,2,1,2]),([6,5,4],[4,5,6]),([3,7,2,9],[8,3,10,2]),([5,5,1,6],[5,1,5,6]),([8,1,7,2,6],[6,8,2,7,1])]]


BATCH={
3473:entry('maximum_k_disjoint_subarray_sum',[('nums','list[int]'),('k','int'),('m','int')],'int',['arrays','dynamic programming','prefix sums'],['nums is nonempty and k*m <= len(nums).','Choose exactly k pairwise non-overlapping contiguous subarrays, each of length at least m.','Return their maximum total sum.'],[([[1,2,-1,3,3,4],2,2],'Choosing [1,2] and [3,3,4] produces the optimal sum thirteen.'),([[1,2,3,4],2,2],'The only way to fit two length-two subarrays uses the whole array, totaling ten.')],SUBARRAY_CASES,SUBARRAYS,[SUBARRAYS.replace('best=max(best,previous[start]-prefix[start])','best=previous[start]-prefix[start]'),SUBARRAYS.replace('previous[start]-prefix[start]','current[start]-prefix[start]')],['Considers only subarrays of exactly m by discarding earlier start candidates.','Builds a new subarray from the current layer and permits overlap between selected subarrays.'],subarrays_oracle,random_subarrays,lesson('Prefix sums turn a subarray contribution into prefix[end] plus a best prior boundary value.','Build one DP layer per selected subarray while maintaining the best eligible start as the end advances.','Carry the skip value; once end reaches m, add previous[start]-prefix[start] to the running start maximum and compare taking.','Each transition ends the newest subarray after all earlier selections, which enforces non-overlap and covers every length at least m.'),'O(k*n)','O(n)',6),
3474:entry('lexicographically_smallest_generated_string',[('str1','str'),('str2','str')],'str',['strings','greedy','constraints'],['str1 contains T and F flags and str2 is a nonempty lowercase pattern.','The result length is len(str1)+len(str2)-1; a T window must equal str2 and an F window must differ.','Return the lexicographically smallest valid result, or an empty string if constraints conflict.'],[(['TFTF','ab'],'Forced T windows and the smallest changes for F windows produce ababa.'),(['TT','ab'],'The overlapping forced copies require incompatible letters, so no result exists.')],GENERATED_CASES,GENERATED,[GENERATED.replace("answer=['a']*length","answer=['b']*length"),GENERATED.replace("if flag=='F' and", "if False and")],['Initializes free positions to b instead of the lexicographically smallest letter a.','Enforces forced T windows but ignores the requirement that every F window differ from the pattern.'],generated_oracle,random_generated,lesson('T windows force letters; all other positions should begin as a, and an equal F window must be broken as far right as possible.','Apply and consistency-check every forced pattern copy, then scan forbidden windows left to right.','When an F window still equals the pattern, change its rightmost unfixed position to b; fail if every position is fixed.','Changing the latest possible free position preserves the earliest lexicographic prefix, and earlier processed windows cannot be restored by that change.'),'O(len(str1)*len(str2))','O(len(str1)+len(str2))',8),
3476:entry('maximum_exact_skill_task_profit',[('workers','list[int]'),('tasks','list[list[int]]')],'int',['arrays','greedy','heaps'],['Each worker may perform at most one task whose required skill exactly equals that worker’s skill.','Each task may be assigned once, and one additional worker can perform any one remaining task.','Maximize total assigned-task profit.'],[([[1,2,3,4,5],[[1,100],[2,400],[3,100],[3,400]]],'Matching workers take profits 100, 400, and 400; the extra worker takes the remaining 100, totaling one thousand.'),([[1],[[2,10]]],'The regular worker cannot match the task, but the extra worker earns ten.')],PROFIT_CASES,PROFIT,[PROFIT.replace('heapq.heappush(available.setdefault(skill,[]),-profit)','heapq.heappush(available.setdefault(skill,[]),profit)').replace('answer-=heapq.heappop(available[skill])','answer+=heapq.heappop(available[skill])').replace('-heap[0]','heap[0]'),PROFIT.replace('extra=max((-heap[0] for heap in available.values() if heap),default=0)','extra=0')],['Uses min-heaps without negation and assigns the least profitable matching tasks.','Omits the unrestricted extra worker entirely.'],profit_oracle,random_profit,lesson('Regular workers partition by exact skill, while the extra worker chooses the best task left across all partitions.','Store each skill’s profits in a max-heap, give every regular worker its highest available match, then inspect heap tops.','Pop once per matching worker and finally add the largest remaining profit from any skill bucket.','Within a skill, assigning larger profits first cannot hurt; after those independent choices, the unrestricted worker optimally takes the global best remainder.'),'O((w+t) log t)','O(t)',6),
3478:entry('maximum_smaller_key_sums',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'list[int]',['arrays','sorting','heaps'],['nums1 and nums2 have equal nonzero length and k is positive.','For each i, only indices j with nums1[j] strictly less than nums1[i] are eligible.','Return the maximum sum of at most k eligible nums2 values for every i.'],[([[4,2,1,5,3],[10,20,30,40,50],2],'Processing smaller keys yields sums [80,30,0,80,50].'),([[1,1],[5,7],1],'Equal nums1 values are not strictly smaller, so both answers are zero.')],SUM_CASES,SUMS,[SUMS.replace('ordered[added][0]<value','ordered[added][0]<=value'),SUMS.replace('if len(heap)>k:','if len(heap)>=k:')],['Includes equal-key indices even though eligibility requires a strict inequality.','Retains at most k-1 values because it pops when the heap first reaches size k.'],sums_oracle,random_sums,lesson('Sorting indices by nums1 lets each query reuse all previously activated strictly smaller keys.','Sweep equal-value groups while a min-heap retains the k largest activated nums2 values.','Before answering a key, add only earlier groups with smaller keys; update the heap sum and write it to every original index in the group.','The heap exactly represents the optimal top-k eligible values, and delaying equal keys enforces strictness.'),'O(n log n+n log k)','O(n)',6),
3479:entry('count_unplaced_fruits',[('fruits','list[int]'),('baskets','list[int]')],'int',['arrays','segment trees','binary search'],['fruits and baskets have equal nonzero length and positive values.','Process fruits in order, placing each in the leftmost unused basket whose capacity is at least its amount.','Count fruits for which no qualifying basket remains.'],[([[4,2,5],[3,5,4]],'Four uses capacity five, two uses the first basket, and no basket can then hold five, so one fruit is unplaced.'),([[2,1],[1,2]],'Two uses the second basket; the first basket then holds one, so both are placed.')],FRUIT_CASES,FRUIT,[FRUIT.replace('tree[node*2]>=value','tree[node*2]>value'),FRUIT.replace('else take(node*2+1,middle+1,right,value)','else take(node*2+1,middle+1,right,0)')],['Skips a left basket whose capacity equals the fruit amount.','Searches the right subtree without enforcing the required capacity.'],fruit_oracle,random_fruit,lesson('A segment maximum tells whether any basket in an interval can hold the current fruit.','Build a max segment tree and descend left first whenever that half has sufficient capacity.','If the root maximum is too small, count failure; otherwise find the leftmost qualifying leaf, set it to zero, and update ancestors.','Left-first descent gives the required earliest basket, while clearing leaves enforces one-time use.'),'O(n log n)','O(n)',6),
}
