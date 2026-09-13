from itertools import combinations
from .import_batch_003 import entry
def oracle(args):
    return sum(a+b>c for a,b,c in combinations(sorted(args[0]),3))
def gen(rng):return [[rng.randint(0,30) for _ in range(rng.randint(3,12))]]
REF='''\
def count_valid_triangles(nums):
    nums=sorted(nums);answer=0
    for right in range(len(nums)-1,1,-1):
        left,middle=0,right-1
        while left<middle:
            if nums[left]+nums[middle]>nums[right]:answer+=middle-left;middle-=1
            else:left+=1
    return answer
'''
BATCH={611:entry('count_valid_triangles',[('nums','list[int]')],'int',['arrays','two-pointers','sorting'],['3 <= len(nums) <= 1,000; 0 <= nums[i] <= 1,000.','Count index triplets whose three lengths satisfy the triangle inequality.'],[([[2,2,3,4]],'The valid triplets are 2,3,4 twice and 2,2,3.'),([[1,2,3]],'1+2 is not greater than 3, so none form a triangle.')],[[x] for x in ([0,0,0],[1,1,1],[2,2,2],[1,1,2],[3,4,5],[4,2,3,4],[10,1,2,3],[2,3,4,5],[1,1,1,1],[5,5,5,5],[0,1,1,2],[6,7,8,9])],REF,[REF.replace('nums=sorted(nums)','nums=list(nums)'),REF.replace('answer+=middle-left','answer+=1')],['Uses unsorted values with two pointers.','Counts one pair instead of all valid left positions.'],oracle,gen,['Sort first so one inequality controls the search.','Fix the largest side and move two pointers inward.','When left+middle exceeds right, add every index from left through middle-1.','Sorting makes every larger left value valid once the smallest current left is valid.'],'The independent oracle enumerates value triples; the reference uses sorted two pointers.', 'O(n^2)','O(n)',5)}
