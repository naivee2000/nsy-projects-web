"""Replacement for the twice-failed brightness-energy candidate."""
from .import_batch_055 import entry

def multiplier_oracle(a):
    nums,k=a;best=float('-inf')
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            for mode in ('multiply','divide'):
                changed=nums[:]
                for i in range(left,right+1):changed[i]=changed[i]*k if mode=='multiply' else int(changed[i]/k)
                for i in range(len(nums)):
                    total=0
                    for j in range(i,len(nums)):total+=changed[j];best=max(best,total)
    return best
def random_multiplier(r):return [[r.randint(-20,20) for _ in range(r.randint(1,8))],r.randint(1,6)]

REFERENCE='''def maximum_subarray_after_multiplier(nums,k):
    negative=float('-inf');before=0;multiplied=divided=after=negative;answer=negative
    for value in nums:
        old_before,old_multiplied,old_divided=before,multiplied,divided
        before=max(old_before,0)+value
        multiplied=max(old_before,old_multiplied,0)+value*k
        divided=max(old_before,old_divided,0)+int(value/k)
        after=max(old_multiplied,old_divided,after)+value
        answer=max(answer,before,multiplied,divided,after)
    return answer
'''
MULTIPLY_ONLY=REFERENCE.replace("divided=max(old_before,old_divided,0)+int(value/k)","divided=negative")
DIVIDE_ONLY=REFERENCE.replace("multiplied=max(old_before,old_multiplied,0)+value*k","multiplied=negative")

BATCH={
3976:entry('maximum_subarray_after_multiplier',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming'],['nums is nonempty and k is positive.','Choose one contiguous segment and either multiply all of it by k or divide all of it by k with truncation toward zero.','After that operation, return the maximum sum of any nonempty contiguous subarray.'],[([[1,-2,3,4,-5],2],'Multiplying the segment [3,4] produces a maximum subarray sum of fourteen.'),([[-5,-2],2],'Dividing the second value toward zero makes the best nonempty subarray sum negative one.')],[[n,k] for n,k in [([1],1),([1],2),([-1],2),([1,-2,3,4,-5],2),([-5,-2],2),([1,2,3],3),([-1,-2,-3],3),([5,-10,5],2),([0,0],4),([10,-1,-1],2),([-10,1,1],3),([2,-3,4,-1,2],2),([7],5),([-7],5)]],REFERENCE,[MULTIPLY_ONLY,DIVIDE_ONLY],['Never considers the divide operation, which can improve negative values.','Never considers multiplying a positive segment.'],multiplier_oracle,random_multiplier,['Track where the eventual maximum subarray lies relative to the transformed segment.','Maintain states before, inside multiplied, inside divided, and after the transformed segment.','Update the four Kadane-style states for each value and retain their maximum.','Every valid solution crosses these phases in order, and each transition represents starting, extending, or ending exactly one transformed segment.'],'O(n)','O(1)',6),
}
