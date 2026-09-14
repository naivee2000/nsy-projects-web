"""Array equalization, missing positives, task timing, distinct selection, and late fees."""
from .import_batch_055 import entry

def equal_oracle(a):return int(any(v!=a[0][0] for v in a[0]))
def random_equal(r):return [[r.randint(0,31) for _ in range(r.randint(1,30))]]
def absent_oracle(a):
    nums=a[0];candidate=max(1,sum(nums)//len(nums)+1);seen=set(nums)
    while candidate in seen:candidate+=1
    return candidate
def random_absent(r):return [[r.randint(1,100) for _ in range(r.randint(1,30))]]
def task_oracle(a):return min(start+duration for start,duration in a[0])
def random_task(r):return [[[r.randint(0,100),r.randint(1,50)] for _ in range(r.randint(1,30))]]
def maximize_oracle(a):return sorted(set(a[0]),reverse=True)[:a[1]]
def random_maximize(r):return [[r.randint(1,100) for _ in range(r.randint(1,30))],r.randint(1,10)]
def fee_oracle(a):return sum(1 if d==1 else 2*d if d<=5 else 3*d for d in a[0])
def random_fee(r):return [[r.randint(1,30) for _ in range(r.randint(1,30))]]

EQUAL='''def minimum_and_subarray_equalization_operations(nums):
    return 0 if len(set(nums))==1 else 1
'''
ABSENT='''def smallest_absent_positive_above_average(nums):
    candidate=max(1,sum(nums)//len(nums)+1)
    seen=set(nums)
    while candidate in seen:candidate+=1
    return candidate
'''
TASK='''def earliest_task_finish_time(tasks):
    return min(start+duration for start,duration in tasks)
'''
MAXIMIZE='''def maximum_k_distinct_elements(nums,k):
    return sorted(set(nums),reverse=True)[:k]
'''
FEE='''def total_library_late_fee(daysLate):
    return sum(1 if days==1 else 2*days if days<=5 else 3*days for days in daysLate)
'''

BATCH={
3674:entry('minimum_and_subarray_equalization_operations',[('nums','list[int]')],'int',['arrays','bit manipulation'],['One operation chooses a nonempty subarray and replaces every value in it by the bitwise AND of that entire subarray.','Return the minimum operations needed to make all array values equal.','Choosing the whole array is allowed.'],[([[1,2]],'The values differ, and one whole-array AND operation makes both zero.'),([[7,7,7]],'All values already match, so zero operations are needed.')],[[x] for x in [[1],[1,2],[7,7,7],[0,1],[3,1,3],[5,6,7],[0,0],[15,7],[2,2,3],[8,4,2,1],[9,9,8],[31,1],[10,12],[4,4,4,5]]],EQUAL,[EQUAL.replace('==1','==0'),EQUAL.replace('else 1','else 2')],['Treats an empty distinct set as the equal condition.','Claims two operations are needed when one whole-array operation suffices.'],equal_oracle,random_equal,['If all values already match, the answer is zero.','Otherwise at least one operation is necessary.','Choose the complete array; its AND is written to every position.','That one operation always equalizes a nonuniform array and is therefore optimal.'],'O(n)','O(n)',3),
3678:entry('smallest_absent_positive_above_average',[('nums','list[int]')],'int',['arrays','sets','math'],['Compute the arithmetic average of nums.','Find the smallest positive integer strictly greater than that average and absent from nums.','Return that integer.'],[([[3,5]],'The average is four; five is present, so the first absent greater integer is six.'),([[1,1]],'The average is one, and two is absent.')],[[x] for x in [[1],[1,1],[3,5],[2,4],[1,2,3],[5,5,5],[1,10],[2,3,4,5],[10,20,30],[4,6,8],[1,3,7],[9,10,11],[2,2,3],[100,1]]],ABSENT,[ABSENT.replace('+1)',')'),ABSENT.replace('return candidate','return candidate+1')],['Starts at the floor of the average rather than strictly above it.','Returns one more than the smallest absent candidate.'],absent_oracle,random_absent,['The first integer strictly above average is floor(sum/n)+1.','Place array values in a set.','Advance the candidate while it is present.','The first absent candidate reached is positive, above average, and minimal.'],'O(n+answer-start)','O(n)',3),
3683:entry('earliest_task_finish_time',[('tasks','list[list[int]]')],'int',['arrays','simulation'],['Each task record contains its start time and duration.','A task finishes at start plus duration.','Return the earliest finish time among all tasks.'],[([[[1,6],[2,3]]],'The tasks finish at seven and five, so the earliest time is five.'),([[[5,1]]],'The only task finishes at time six.')],[[x] for x in [[[0,1]],[[5,1]],[[1,6],[2,3]],[[10,2],[0,20]],[[3,3],[4,1]],[[1,10],[2,9]],[[100,1],[50,2]],[[0,5],[5,1]],[[7,7],[8,5]],[[1,1],[2,2],[3,3]],[[9,1],[1,9]],[[4,6],[2,2]],[[20,5],[10,20]],[[6,4],[7,2]]]],TASK,[TASK.replace('min(','max(',1),TASK.replace('start+duration','duration')],['Returns the latest finish.','Ignores task start times.'],task_oracle,random_task,['Compute start+duration for every record.','Track the minimum completion value.','Every task is independent for this question.','The minimum computed finish is exactly the earliest possible completion.'],'O(n)','O(1)',3),
3684:entry('maximum_k_distinct_elements',[('nums','list[int]'),('k','int')],'list[int]',['arrays','sets','sorting','greedy'],['Select at most k distinct values from the positive array.','Maximize their sum.','Return the selected values in strictly descending order.'],[([[84,93,100,77,90],3],'The three largest distinct values are 100, 93, and 90.'),([[5,5,4],3],'Only distinct values may be returned, giving [5,4].')],[[n,k] for n,k in [([1],1),([1,2],1),([1,2],2),([5,5,4],3),([84,93,100,77,90],3),([3,3,3],2),([1,5,2,5],2),([9,8,7,6],3),([2,1,2,3],5),([10,1],1),([4,4,2,2],1),([6,5,4],2),([100,99,100],2),([1,3,2,3,4],3)]],MAXIMIZE,[MAXIMIZE.replace('set(nums)','nums'),MAXIMIZE.replace('reverse=True','reverse=False')],['Retains duplicate occurrences.','Returns the smallest values in ascending order.'],maximize_oracle,random_maximize,['Remove duplicates with a set.','Because values are positive, adding a larger distinct value always improves the sum.','Sort distinct values descending and keep the first k.','The returned order is already strictly descending.'],'O(n log n)','O(n)',3),
3687:entry('total_library_late_fee',[('daysLate','list[int]')],'int',['arrays','simulation'],['Charge one unit for a book exactly one day late.','Charge twice the days for two through five days late, and three times the days beyond five.','Return the total fee across all books.'],[([[5,1,7]],'Fees are ten, one, and twenty-one, totaling thirty-two.'),([[1,2,6]],'The three fee bands contribute one, four, and eighteen.')],[[x] for x in [[1],[2],[5],[6],[5,1,7],[1,2,6],[3,4],[7,8],[1,1,1],[2,5,6],[10],[4,6,1],[9,2,5],[3,3,7]]],FEE,[FEE.replace('days<=5','days<5'),FEE.replace('3*days','2*days')],['Places day five in the highest fee band.','Charges only double for more than five days.'],fee_oracle,random_fee,['Evaluate each late return independently.','Select its multiplier from the three stated bands.','Add the resulting fee to the total.','The disjoint conditions cover every positive days-late value exactly once.'],'O(n)','O(1)',3),
}
