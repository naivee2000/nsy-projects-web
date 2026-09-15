"""Frequency windows, road lights, task trees, weighted selections, and spaced pairs."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import gcd
from .import_batch_055 import entry

def balance_oracle(a):
    nums=a[0];best=0
    for i in range(len(nums)):
        counts=Counter()
        for j in range(i,len(nums)):
            counts[nums[j]]+=1;freq=set(counts.values())
            if len(counts)==1 or (len(freq)==2 and max(freq)==2*min(freq)):best=max(best,j-i+1)
    return best
def random_balance(r):return [[r.randint(1,6) for _ in range(r.randint(1,25))]]
def lights_oracle(a):
    lights=a[0];n=len(lights);covered=set()
    for i,radius in enumerate(lights):
        if radius>0:covered.update(range(max(0,i-radius),min(n,i+radius+1)))
    for used in range(n+1):
        for chosen in combinations(range(n),used):
            reach=covered|{p for i in chosen for p in range(max(0,i-1),min(n,i+2))}
            if len(reach)==n:return used
def random_lights(r):return [[r.randint(0,4) for _ in range(r.randint(1,10))]]
def finish_oracle(a):
    n,edges,base=a;children=[[] for _ in range(n)]
    for u,v in edges:children[u].append(v)
    def solve(node):
        values=[solve(child) for child in children[node]]
        return base[node] if not values else max(values)+(max(values)-min(values))+base[node]
    return solve(0)
def random_finish(r):
    n=r.randint(1,12);return [n,[[r.randrange(i),i] for i in range(1,n)],[r.randint(1,20) for _ in range(n)]]
def selected_oracle(a):
    nums,k,mul=a;factors=[max(1,mul-i) for i in range(k)];return max(sum(x*f for x,f in zip(sorted(group,reverse=True),factors)) for group in combinations(nums,k))
def random_selected(r):
    n=r.randint(1,10);return [[r.randint(1,30) for _ in range(n)],r.randint(1,n),r.randint(1,8)]
def pair_oracle(a):
    nums,k=a;return max((nums[i]+nums[j] for i in range(len(nums)) for j in range(i+k,len(nums))),default=0)
def random_pair(r):
    n=r.randint(2,30);return [[r.randint(0,100) for _ in range(n)],r.randint(1,n-1)]

BALANCE='''def longest_frequency_balance_subarray(nums):
    answer=1
    for left in range(len(nums)):
        counts={}
        for right in range(left,len(nums)):
            value=nums[right];counts[value]=counts.get(value,0)+1;frequencies=set(counts.values())
            if len(counts)==1 or (len(frequencies)==2 and max(frequencies)==2*min(frequencies)):answer=max(answer,right-left+1)
    return answer
'''
LIGHTS='''def minimum_added_road_lights(lights):
    n=len(lights);delta=[0]*(n+1)
    for i,radius in enumerate(lights):
        if radius>0:
            left=max(0,i-radius);right=min(n-1,i+radius);delta[left]+=1;delta[right+1]-=1
    active=gap=answer=0
    for change in delta[:-1]:
        active+=change
        if active==0:gap+=1
        else:answer+=(gap+2)//3;gap=0
    return answer+(gap+2)//3
'''
FINISH='''def root_task_finish_time(n,edges,baseTime):
    children=[[] for _ in range(n)]
    for parent,child in edges:children[parent].append(child)
    def finish(node):
        if not children[node]:return baseTime[node]
        values=[finish(child) for child in children[node]]
        return max(values)+(max(values)-min(values))+baseTime[node]
    return finish(0)
'''
SELECTED='''def maximum_k_selection_sum(nums,k,mul):
    ordered=sorted(nums,reverse=True);answer=0
    for i in range(k):answer+=ordered[i]*max(1,mul-i)
    return answer
'''
PAIR='''def maximum_spaced_pair_sum(nums,k):
    answer=best=0
    for right in range(k,len(nums)):
        best=max(best,nums[right-k]);answer=max(answer,best+nums[right])
    return answer
'''

BATCH={
3960:entry('longest_frequency_balance_subarray',[('nums','list[int]')],'int',['arrays','hash-maps'],['nums is nonempty.','A subarray is balanced when it has one distinct value, or its distinct-value frequencies have exactly two levels and the larger is twice the smaller.','Return the maximum balanced subarray length.'],[([[1,2,2,1,2,3,3,3]],'A longest valid window has length five with frequency levels in a two-to-one ratio.'),([[4,4,4]],'A single distinct value is balanced, so the whole array qualifies.')],[[x] for x in [[1],[1,1],[1,2],[1,2,2,1,2,3,3,3],[4,4,4],[1,1,2],[1,1,2,2],[1,1,1,2],[1,2,3,4],[1,2,2,3,3,3],[1,1,1,1,2,2],[3,1,3,1,3],[1,2,1,2,3],[5,4,5,4,5,4],[1,1,2,2,2,2]]],BALANCE,[BALANCE.replace('2*min(frequencies)','3*min(frequencies)'),BALANCE.replace('len(counts)==1 or ','')],['Requires a three-to-one frequency ratio.','Rejects valid single-value windows.'],balance_oracle,random_balance,['Only the frequency multiset matters for a fixed window.','Enumerate left endpoints and extend right while maintaining value counts.','Accept one value, or two frequency levels whose maximum is twice their minimum.','Every candidate window is examined and its maintained counts are exact.'],'O(n^2)','O(n)',5),
3964:entry('minimum_added_road_lights',[('lights','list[int]')],'int',['arrays','greedy'],['lights[i]=0 means no working light; a positive value is that light’s illumination radius.','An added bulb has radius one.','Return the fewest added bulbs needed to illuminate every road position.'],[([[0,0,0,0]],'Two added radius-one bulbs cover all four positions.'),([[0,1,0]],'The existing center light already covers the road, so return zero.')],[[x] for x in [[0],[1],[0,0],[0,0,0,0],[0,1,0],[1,0,0,0],[0,0,0,1],[2,0,0,0,0],[0,0,1,0,0],[1,0,0,1],[0,2,0,0,0,0],[0,0,0,0,0,0],[3,0,0,0,0,0,0],[0,1,0,0,0,1,0]]],LIGHTS,[LIGHTS.replace('(gap+2)//3','gap//3'),LIGHTS.replace('if radius>0:','if radius>1:')],['Rounds uncovered runs down and misses their remainder.','Incorrectly ignores existing radius-one bulbs.'],lights_oracle,random_lights,['Mark every position covered by existing variable-radius lights using a difference array.','Uncovered positions form independent runs; one added radius-one bulb covers at most three consecutive positions.','For each uncovered run add ceil(length/3).','Greedily placing bulbs every third position covers a run with exactly that lower-bound number.'],'O(n)','O(n)',5),
3965:entry('root_task_finish_time',[('n','int'),('edges','list[list[int]]'),('baseTime','list[int]')],'int',['trees','recursion'],['Directed edges parent-child form a rooted tree at task zero.','A leaf finishes at its base time; an internal task finishes at latest child + (latest-earliest) + its base time.','Return task zero’s finish time.'],[([3,[[0,1],[1,2]],[9,5,3]],'The chain finishes bottom-up at 3, then 8, then 17.'),([3,[[0,1],[0,2]],[2,4,7]],'Child times four and seven give root finish 7+(7-4)+2=12.')],[[n,e,b] for n,e,b in [(1,[],[5]),(2,[[0,1]],[1,2]),(3,[[0,1],[1,2]],[9,5,3]),(3,[[0,1],[0,2]],[2,4,7]),(4,[[0,1],[0,2],[0,3]],[1,2,3,4]),(4,[[0,1],[1,2],[1,3]],[5,4,2,8]),(5,[[0,1],[0,2],[2,3],[2,4]],[1,2,3,4,5]),(3,[[0,2],[2,1]],[3,2,1]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]],[1,1,1,1,1,1]),(5,[[0,1],[0,2],[1,3],[1,4]],[10,1,2,3,4]),(2,[[0,1]],[100,1]),(3,[[0,1],[0,2]],[1,9,9]),(4,[[0,1],[1,2],[2,3]],[4,3,2,1]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[1,2,3,4,5,6,7])]],FINISH,[FINISH.replace('max(values)-min(values)','0'),FINISH.replace('return baseTime[node]','return 0')],['Omits the spread between child completion times.','Treats leaf tasks as taking zero time.'],finish_oracle,random_finish,['Child subtrees must finish before their parent formula can be evaluated.','Use postorder recursion to collect all child finish times.','Return base time for leaves; otherwise latest+(latest-earliest)+base.','Postorder computes each dependency exactly once before its parent.'],'O(n)','O(n)',5),
3974:entry('maximum_k_selection_sum',[('nums','list[int]'),('k','int'),('mul','int')],'int',['arrays','greedy','sorting'],['nums contains positive integers and 1<=k<=len(nums).','Select exactly k values; successive chosen values may be multiplied by current mul, which decreases by one, or left unchanged.','Return the maximum total.'],[([[6,1,2,9],3,2],'Use the largest values with effective factors two, one, and one: 18+6+2=26.'),([[1,2,3],2,4],'Assign factors four and three to values three and two, totaling eighteen.')],[[n,k,m] for n,k,m in [([1],1,1),([5],1,3),([6,1,2,9],3,2),([1,2,3],2,4),([1,2],2,1),([9,8,7],1,5),([3,3,3],2,2),([1,10,2,9],2,3),([5,4,3,2,1],5,2),([2,8,4],2,1),([100,1,1],2,2),([7,6,5,4],3,5),([1,1,9,9],3,3),([2,4,6,8],4,4)]],SELECTED,[SELECTED.replace('sorted(nums,reverse=True)','sorted(nums)'),SELECTED.replace('max(1,mul-i)','mul-i')],['Selects the smallest values.','Uses zero or negative multipliers even though leaving a value unchanged is allowed.'],selected_oracle,random_selected,['All effective multipliers are at least one and nonincreasing.','Choose the k largest values and pair the largest values with the largest multipliers.','Sort descending and sum value*max(1,mul-index).','Exchange arguments improve any plan that omits a larger value or pairs larger value with smaller factor.'],'O(n log n)','O(n)',5),
3979:entry('maximum_spaced_pair_sum',[('nums','list[int]'),('k','int')],'int',['arrays','prefix maxima'],['nums contains nonnegative integers and 1<=k<len(nums).','A pair i<j is valid when j-i>=k.','Return the maximum nums[i]+nums[j].'],[([[1,3,5,2,8],2],'The pair values five and eight is separated by two indices and sums to thirteen.'),([[9,1,2],2],'Only indices zero and two qualify, giving eleven.')],[[n,k] for n,k in [([1,2],1),([1,3,5,2,8],2),([9,1,2],2),([5,4,3],1),([0,0],1),([1,10,1,9],2),([8,1,1,8],3),([2,4,6,8],1),([2,4,6,8],3),([100,1,2,3],2),([1,2,100,3,4],2),([7,7,7],1),([0,9,0,8,0],3),([4,1,6,2,9,3],2)]],PAIR,[PAIR.replace('nums[right-k]','nums[right-k+1]'),PAIR.replace('return answer','return answer+1')],['Allows pairs whose index gap is only k-1.','Adds one to every maximum pair sum.'],pair_oracle,random_pair,['At right index j, eligible left indices end at j-k.','Maintain the maximum value among that growing eligible prefix.','Add nums[j] to the prefix maximum and retain the best pair sum.','Every valid pair is considered when its right endpoint is processed.'],'O(n)','O(1)',5),
}
