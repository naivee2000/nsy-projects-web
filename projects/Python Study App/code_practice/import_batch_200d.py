"""Extreme sums, target updates, prefix groups, comma counts, and alternating arrays."""
from itertools import combinations
from .import_batch_055 import entry

def difference_oracle(a):
    nums,k=a;sums=[sum(group) for group in combinations(nums,k)];return max(sums)-min(sums)
def random_difference(r):
    n=r.randint(2,12);return [[r.randint(-50,50) for _ in range(n)],r.randint(1,n)]
def operations_oracle(a):
    nums,target=a;values=[]
    for x,y in zip(nums,target):
        if x!=y and x not in values:values.append(x)
    return len(values)
def random_operations(r):
    n=r.randint(1,30);return [[r.randint(0,8) for _ in range(n)],[r.randint(0,8) for _ in range(n)]]
def prefix_oracle(a):
    words,k=a;prefixes=[]
    for i,word in enumerate(words):
        if len(word)>=k and sum(other[:k]==word[:k] for other in words if len(other)>=k)>=2 and word[:k] not in prefixes:prefixes.append(word[:k])
    return len(prefixes)
def random_prefix(r):return [[''.join(r.choice('abcd') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,30))],r.randint(1,6)]
def commas_oracle(a):
    n=a[0]
    if n<=20000:return sum(f'{value:,}'.count(',') for value in range(1,n+1))
    answer=0
    for digits in range(4,len(str(n))+1):
        low=10**(digits-1);high=min(n,10**digits-1)
        if low<=high:answer+=(high-low+1)*((digits-1)//3)
    return answer
def random_commas(r):return [r.randint(1,20000)]
def alternating_oracle(a):
    nums=a[0];answer=0
    for i in range(len(nums)):
        for j in range(i,len(nums)):
            answer+=all(nums[p]!=nums[p+1] for p in range(i,j))
    return answer
def random_alternating(r):return [[r.randint(0,1) for _ in range(r.randint(1,40))]]

DIFFERENCE='''def extreme_k_sum_difference(nums,k):
    ordered=sorted(nums)
    return sum(ordered[-k:])-sum(ordered[:k])
'''
OPERATIONS='''def minimum_target_array_operations(nums,target):
    return len({value for value,wanted in zip(nums,target) if value!=wanted})
'''
PREFIX='''def count_prefix_connected_groups(words,k):
    counts={}
    for word in words:
        if len(word)>=k:counts[word[:k]]=counts.get(word[:k],0)+1
    return sum(count>=2 for count in counts.values())
'''
COMMAS='''def count_formatted_commas(n):
    answer=0;threshold=1000
    while threshold<=n:
        answer+=n-threshold+1;threshold*=1000
    return answer
'''
ALTERNATING='''def count_alternating_subarrays(nums):
    answer=ending=1
    for index in range(1,len(nums)):
        ending=ending+1 if nums[index]!=nums[index-1] else 1
        answer+=ending
    return answer
'''

BATCH={
3774:entry('extreme_k_sum_difference',[('nums','list[int]'),('k','int')],'int',['arrays','sorting'],['1 <= k <= len(nums); nums contains integers.','Compare the sum of the k largest elements with the sum of the k smallest elements.','Return their absolute difference; elements are chosen by position, including duplicates.'],[([[5,2,2,4],2],'The largest pair sums to nine and the smallest pair to four, giving five.'),([[1,1,1],2],'Every two-element selection has the same sum, so the difference is zero.')],[[a,k] for a,k in [([1],1),([1,2],1),([5,2,2,4],2),([1,1,1],2),([-5,-1,3],1),([-5,-1,3],2),([1,2,3,4],4),([9,0,9,0],2),([3,1,2],1),([10,-10,5,-5],3),([7,7,1,1,4],2),([100,1,50],2),([-3,-2,-1],1),([8,6,4,2,0],3)]],DIFFERENCE,[DIFFERENCE.replace('ordered[-k:]','ordered[:k]'),DIFFERENCE.replace('-sum(ordered[:k])','+sum(ordered[:k])')],['Uses the smallest group for both sides and always returns zero.','Adds the two extreme sums instead of taking their difference.'],difference_oracle,random_difference,['The minimum k-element sum uses the k smallest values; the maximum uses the k largest.','Sort once to expose both groups.','Subtract the first-k sum from the last-k sum.','An exchange argument shows replacing any chosen value by a more extreme available value can only improve its respective sum.'],'O(n log n)','O(n)',3),
3810:entry('minimum_target_array_operations',[('nums','list[int]'),('target','list[int]')],'int',['arrays','sets'],['nums and target have equal length.','One operation chooses a current value x and updates all mismatched occurrences selected by its maximal equal-value segments to their target values.','Return the least operations needed to make nums equal target.'],[([[1,2,3],[2,1,3]],'The mismatches have original values one and two, requiring two operations.'),([[1,1,2],[3,3,2]],'Both mismatches share original value one, so one operation updates them together.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,2,3],[2,1,3]),([1,1,2],[3,3,2]),([1,2],[1,3]),([1,1,1],[2,3,4]),([1,2,1],[3,2,3]),([0,0],[1,1]),([1,2,3],[1,2,3]),([5,6,5,6],[6,5,6,5]),([2,2,3,3],[2,4,3,5]),([9,8,7],[7,8,9]),([1,3,1,3],[2,3,2,3]),([4,5,6,4],[7,5,8,9])]],OPERATIONS,[OPERATIONS.replace('if value!=wanted',''),OPERATIONS.replace('{value for value,wanted','{wanted for value,wanted')],['Counts values at already-correct positions too.','Counts distinct target values instead of the original values selected by operations.'],operations_oracle,random_operations,['An operation is keyed by the original value it selects.','Correct positions require no work; among mismatches, all equal original values can be handled together.','Collect nums[i] where nums[i]!=target[i] and return the set size.','Each distinct mismatched source value needs one operation and one operation suffices for all of its segments.'],'O(n)','O(n)',5),
3839:entry('count_prefix_connected_groups',[('words','list[str]'),('k','int')],'int',['strings','hash-maps'],['words may contain duplicates, which count as separate entries; k is positive.','Ignore words shorter than k.','A group is a length-k prefix shared by at least two eligible words; return the number of such prefixes.'],[([['apple','apply','banana','bandit'],2],'Prefixes ap and ba each occur twice, producing two groups.'),([['a','ab','abc','abd'],3],'Only abc and abd are long enough, but their length-three prefixes differ, so return zero.')],[[w,k] for w,k in [(['a'],1),(['a','a'],1),(['a','a'],2),(['apple','apply','banana','bandit'],2),(['a','ab','abc','abd'],3),(['cat','car','dog'],2),(['same','same'],4),(['x','xy','xz'],1),(['abc','abd','abe'],2),(['ab','ac','ad'],2),(['short','shore','shop','other'],3),(['aa','aaa','aaaa'],2),(['one','two'],4),(['prefix','presto','prevent','post'],3),(['a','b','c','a'],1)]],PREFIX,[PREFIX.replace('count>=2','count>2'),PREFIX.replace("if len(word)>=k:","")],['Requires three members instead of two.','Includes short words using their entire value as a prefix.'],prefix_oracle,random_prefix,['Only the first k characters determine membership.','Count eligible words by their length-k prefix.','Ignore short words, then count frequency buckets of at least two.','Each eligible word belongs to exactly one prefix group, and duplicate entries increment its frequency independently.'],'O(total characters)','O(number of prefixes)',5),
3871:entry('count_formatted_commas',[('n','int')],'int',['math','counting'],['1 <= n <= 100,000,000.','Format every integer from one through n with a comma after each group of three digits from the right.','Return the total number of comma characters used.'],[([1002],'Values 1000, 1001, and 1002 each use one comma, totaling three.'),([1000000],'Every value from 1000 contributes one comma and 1,000,000 contributes a second comma.')],[[n] for n in [1,9,999,1000,1001,1002,9999,999999,1000000,1000001,2000000,9999999,10000000,100000000]],COMMAS,[COMMAS.replace('n-threshold+1','n-threshold'),COMMAS.replace('threshold*=1000','threshold*=100')],['Omits the threshold value itself at every comma level.','Introduces new comma levels every two digits instead of every three.'],commas_oracle,random_commas,['Every number at least 1,000 contributes its first comma, every number at least 1,000,000 contributes another, and so on.','Count how many values reach each power-of-1000 threshold.','For threshold t<=n, add n-t+1 and multiply t by 1000.','Summing threshold contributions counts each formatted comma exactly once.'],'O(log_1000 n)','O(1)',5),
3101:entry('count_alternating_subarrays',[('nums','list[int]')],'int',['arrays','dynamic programming'],['1 <= len(nums) <= 100,000; every value is zero or one.','A nonempty contiguous subarray is alternating when every adjacent pair differs.','Return the total number of alternating subarrays.'],[([[0,1,1,1]],'Four singleton subarrays and the initial [0,1] are alternating, totaling five.'),([[1,0,1,0]],'Every one of the ten subarrays alternates.')],[[x] for x in [[0],[1],[0,0],[0,1],[0,1,1,1],[1,0,1,0],[1,1,1],[0,1,0],[0,0,1,0],[1,0,0,1],[0,1,0,1,0],[1,1,0,0],[0,0,0,1],[1,0,1,1,0]]],ALTERNATING,[ALTERNATING.replace('else 1','else 0'),ALTERNATING.replace('range(1,len(nums))','range(2,len(nums))')],['Resets the number of alternating subarrays ending at a repeated value to zero instead of its singleton.','Skips the adjacency decision at index one.'],alternating_oracle,random_alternating,['Track how many alternating subarrays end at the current position.','If the new value differs from the previous one, extend every prior ending subarray and add its singleton; otherwise only the singleton remains.','Update ending and add it to the total.','Each alternating subarray is counted exactly once at its right endpoint.'],'O(n)','O(1)',5),
}
