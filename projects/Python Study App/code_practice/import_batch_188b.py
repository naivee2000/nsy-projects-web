"""Matrix shifts, peaks, cross-membership, battery tests, and removable-subarray batch."""
from .import_batch_055 import entry

def matrix_oracle(a):
    mat,k=a
    for i,row in enumerate(mat):
        shift=(-k if i%2==0 else k)%len(row)
        moved=row[shift:]+row[:shift]
        if moved!=row:return False
    return True
def random_matrix(r):
    rows,cols=r.randint(1,8),r.randint(1,8);return [[[r.randint(0,9) for _ in range(cols)] for _ in range(rows)],r.randint(1,20)]
def peaks_oracle(a):return [i for i in range(1,len(a[0])-1) if a[0][i-1]<a[0][i]>a[0][i+1]]
def random_peaks(r):return [[r.randint(1,100) for _ in range(r.randint(3,30))]]
def intersection_oracle(a):
    one,two=a;return [sum(any(x==y for y in two) for x in one),sum(any(y==x for x in one) for y in two)]
def random_intersection(r):return [[r.randint(1,20) for _ in range(r.randint(1,30))],[r.randint(1,20) for _ in range(r.randint(1,30))]]
def tested_oracle(a):
    values=a[0][:];answer=0
    for i in range(len(values)):
        if values[i]>0:
            answer+=1
            for j in range(i+1,len(values)):values[j]=max(0,values[j]-1)
    return answer
def random_tested(r):return [[r.randint(0,20) for _ in range(r.randint(1,40))]]
def increasing(values):return all(x<y for x,y in zip(values,values[1:]))
def removable_oracle(a):
    nums=a[0];return sum(increasing(nums[:left]+nums[right+1:]) for left in range(len(nums)) for right in range(left,len(nums)))
def random_removable(r):return [[r.randint(1,30) for _ in range(r.randint(1,12))]]

MATRIX='''\
def matrix_unchanged_after_row_shifts(mat,k):
    width=len(mat[0]);shift=k%width
    return all(all(row[j]==row[(j+shift)%width] for j in range(width)) for row in mat)
'''
PEAKS='''\
def strict_peak_indices(mountain):
    return [i for i in range(1,len(mountain)-1) if mountain[i]>mountain[i-1] and mountain[i]>mountain[i+1]]
'''
INTERSECTION='''\
def cross_array_membership_counts(nums1,nums2):
    first=set(nums1);second=set(nums2)
    return [sum(value in second for value in nums1),sum(value in first for value in nums2)]
'''
TESTED='''\
def count_testable_devices(batteryPercentages):
    tested=0
    for charge in batteryPercentages:
        if charge-tested>0:tested+=1
    return tested
'''
REMOVABLE='''\
def count_incremovable_subarrays(nums):
    answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            remaining=nums[:left]+nums[right+1:]
            if all(a<b for a,b in zip(remaining,remaining[1:])):answer+=1
    return answer
'''

BATCH={
2946:entry('matrix_unchanged_after_row_shifts',[('mat','list[list[int]]'),('k','int')],'bool',['matrices','simulation','modular arithmetic'],['Shift every even-indexed row left by k positions and every odd-indexed row right by k positions.','Rows wrap around and all have the same width.','Return whether the matrix is identical to its original state after all shifts.'],[([[[1,2,3],[4,5,6],[7,8,9]],4],'A shift of four is one position modulo width three, and the rows change.'),([[[1,2,1,2],[5,5,5,5]],2],'Both period-two and constant rows are unchanged by two positions.')],[[m,k] for m,k in [([[1]],1),([[1,2]],2),([[1,2]],1),([[1,1]],1),([[1,2,1,2]],2),([[1,2,1,2]],1),([[1,2],[3,4]],2),([[1,2],[3,4]],1),([[1,2,3],[3,2,1]],3),([[0,0,0]],10),([[1,2,3,1,2,3]],3),([[1,2,3,1,2,3]],2),([[7,8,7,8],[9,9,9,9]],6),([[1,2,3],[4,5,6],[7,8,9]],4)]],MATRIX,[MATRIX.replace('(j+shift)%width','(j+1)%width'),MATRIX.replace('for row in mat','for row in mat[:-1]')],['Always tests a one-position shift instead of k modulo the width.','Ignores the final matrix row.'],matrix_oracle,random_matrix,['A row equals either its left or right k-shift exactly when it is periodic by k positions.','Reduce k modulo the row width.','For every row and column compare the value with the position shift steps away.','The equality condition checks every destination/source pair; direction is immaterial when testing invariance.'],'O(rows*columns)','O(1)',3),
2951:entry('strict_peak_indices',[('mountain','list[int]')],'list[int]',['arrays','local comparisons'],['A peak index is neither endpoint of the array.','Its value must be strictly greater than both immediate neighbors.','Return all peak indices in increasing order.'],[([[2,4,4]],'Index one ties its right neighbor, so there are no strict peaks.'),([[1,4,3,8,5]],'Indices one and three exceed both adjacent values.')],[[x] for x in [[1,2,3],[3,2,1],[1,3,1],[2,4,4],[4,4,2],[1,4,3,8,5],[5,1,5],[1,2,1,2,1],[1,1,1],[3,1,2],[1,3,2,4],[9,8,9,8,9],[2,1,3,1,2],[1,10,1]]],PEAKS,[PEAKS.replace('mountain[i]>mountain[i-1]','mountain[i]>=mountain[i-1]'),PEAKS.replace('range(1,len(mountain)-1)','range(0,len(mountain)-1)')],['Permits a tie with the left neighbor.','Incorrectly considers the first endpoint and wraps to the last value.'],peaks_oracle,random_peaks,['Only immediate neighbors matter for this definition.','Endpoints cannot qualify, so scan indices one through n-2.','Append an index only when both strict greater-than comparisons hold.','The scan examines every and only eligible index, applying the defining condition directly.'],'O(n)','O(output)',3),
2956:entry('cross_array_membership_counts',[('nums1','list[int]'),('nums2','list[int]')],'list[int]',['arrays','sets','counting'],['Count elements of nums1 whose value appears anywhere in nums2.','Separately count elements of nums2 whose value appears anywhere in nums1.','Repeated elements count separately in the array being counted.'],[([[2,3,2],[1,2]],'Two nums1 entries equal two, while one nums2 entry appears in nums1, giving [2,1].'),([[4,3,2,3,1],[2,2,5,2,3,6]],'Three entries qualify in the first array and four in the second.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,1],[1]),([1],[1,1]),([1,2],[2,3]),([2,3,2],[1,2]),([4,3,2,3,1],[2,2,5,2,3,6]),([1,2,3],[4,5,6]),([1,2,3],[3,2,1]),([0,0],[0,0,0]),([-1,2],[-1]),([5,5,6],[5,7,5]),([9,8,7],[7]),([1,3,5],[2,4,6])]],INTERSECTION,[INTERSECTION.replace('for value in nums1','for value in first'),INTERSECTION.replace('value in first for value in nums2','value in second for value in nums2')],['Counts distinct qualifying values rather than qualifying occurrences in nums1.','Tests nums2 values against nums2 itself, making the second count always its length.'],intersection_oracle,random_intersection,['Membership sets make repeated lookup constant time.','Build one set for each array.','Count original entries from each side whose value belongs to the opposite set.','Iterating the original arrays preserves multiplicity while sets answer only the required existence question.'],'O(n+m)','O(n+m)',3),
2960:entry('count_testable_devices',[('batteryPercentages','list[int]')],'int',['arrays','greedy','simulation'],['Process devices from left to right.','When the current effective battery is positive, test it and reduce every later positive battery by one.','Return the number of devices tested.'],[([[1,1,2,1,3]],'Devices zero, two, and four remain positive when reached, so three are tested.'),([[0,1,2]],'The first is skipped; the other two are tested, producing two.')],[[x] for x in [[0],[1],[0,0],[1,1],[0,1,2],[1,1,2,1,3],[5,5,5],[0,0,3],[2,1,0],[1,2,3,4],[4,3,2,1],[1,0,1,0,1],[10,0,10],[2,2,2,2]]],TESTED,[TESTED.replace('charge-tested>0','charge-tested>=0'),TESTED.replace('tested+=1','tested+=charge')],['Tests a device whose effective charge is exactly zero.','Adds the battery value instead of one tested device.'],tested_oracle,random_tested,['Every earlier successful test subtracts exactly one from the current device.','Thus effective charge equals its stored value minus the number already tested.','Increment the tested count exactly when that difference is positive.','This scalar count represents all prior decrements, making explicit mutation of every suffix unnecessary.'],'O(n)','O(1)',3),
2970:entry('count_incremovable_subarrays',[('nums','list[int]')],'int',['arrays','subarrays','enumeration'],['Remove one nonempty contiguous subarray.','The elements left behind must be strictly increasing; an empty or one-element remainder is increasing.','Return the number of removable subarrays satisfying that condition.'],[([[1,2,3,4]],'Every one of the ten nonempty subarrays can be removed while leaving an increasing sequence.'),([[6,5,7,8]],'Seven removal intervals leave a strictly increasing remainder.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[1,2,3],[3,2,1],[1,3,2],[6,5,7,8],[1,2,3,4],[1,1,1],[2,1,3],[3,1,2],[1,4,2,3],[5,4,3,2,1]]],REMOVABLE,[REMOVABLE.replace('a<b','a<=b'),REMOVABLE.replace('right+1','right')],['Accepts nondecreasing remainders containing equal adjacent values.','Keeps the right endpoint instead of removing the full chosen interval.'],removable_oracle,random_removable,['The source-I constraints allow enumerating every removal interval.','Construct the prefix before left followed by the suffix after right.','Check strict increase across every adjacent pair of that remainder.','Every nonempty contiguous removal has a unique left/right pair, so the count is exhaustive and duplicate-free.'],'O(n^3)','O(n)',3),
}
