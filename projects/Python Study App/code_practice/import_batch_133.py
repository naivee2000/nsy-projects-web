"""First slice of workbook batch 133."""

from collections import deque

from .import_batch_055 import entry


def palindrome_merge_oracle(args):
    start=tuple(args[0]);queue=deque([(start,0)]);seen={start}
    while queue:
        values,steps=queue.popleft()
        if values==values[::-1]:return steps
        for index in range(len(values)-1):
            candidate=values[:index]+(values[index]+values[index+1],)+values[index+2:]
            if candidate not in seen:seen.add(candidate);queue.append((candidate,steps+1))


def random_palindrome_merge(rng):return [[rng.randint(1,9) for _ in range(rng.randint(1,8))]]


def pairing_xor_oracle(args):
    nums1,nums2=args;answer=0
    for left in nums1:
        for right in nums2:answer^=left^right
    return answer


def random_pairing_xor(rng):return [[rng.randint(0,63) for _ in range(rng.randint(1,9))],[rng.randint(0,63) for _ in range(rng.randint(1,9))]]


def hourglass_oracle(args):
    grid=args[0];best=-10**18
    for row in range(len(grid)-2):
        for column in range(len(grid[0])-2):
            cells=[grid[row][column],grid[row][column+1],grid[row][column+2],grid[row+1][column+1],grid[row+2][column],grid[row+2][column+1],grid[row+2][column+2]]
            best=max(best,sum(cells))
    return best


def random_hourglass(rng):
    rows,columns=rng.randint(3,7),rng.randint(3,7)
    return [[[rng.randint(-20,30) for _ in range(columns)] for _ in range(rows)]]


def minimize_xor_oracle(args):
    num1,num2=args;needed=num2.bit_count();limit=1<<(max(num1.bit_length(),needed)+1)
    return min((candidate^num1,candidate) for candidate in range(limit) if candidate.bit_count()==needed)[1]


def random_minimize_xor(rng):return [rng.randint(1,255),rng.randint(1,255)]


def prefix_xor_oracle(args):
    pref=args[0];result=[];running=0
    for target in pref:
        candidate=next(value for value in range(1<<max(1,target.bit_length(),running.bit_length())) if running^value==target)
        result.append(candidate);running=target
    return result


def random_prefix_xor(rng):
    nums=[rng.randint(0,31) for _ in range(rng.randint(1,12))];running=0;pref=[]
    for value in nums:running^=value;pref.append(running)
    return [pref]


PALINDROME='''\
def minimum_merges_to_palindrome(nums):
    left=0;right=len(nums)-1;left_sum=nums[left];right_sum=nums[right];operations=0
    while left<right:
        if left_sum==right_sum:left+=1;right-=1
        elif left_sum<right_sum:left+=1;left_sum+=nums[left];operations+=1;continue
        else:right-=1;right_sum+=nums[right];operations+=1;continue
        if left<right:left_sum=nums[left];right_sum=nums[right]
    return operations
'''

PAIRING='''\
def xor_of_all_pairings(nums1,nums2):
    answer=0
    if len(nums2)%2:
        for value in nums1:answer^=value
    if len(nums1)%2:
        for value in nums2:answer^=value
    return answer
'''

HOURGLASS='''\
def maximum_hourglass_sum(grid):
    best=-10**30
    for row in range(len(grid)-2):
        for column in range(len(grid[0])-2):
            total=sum(grid[row][column:column+3])+grid[row+1][column+1]+sum(grid[row+2][column:column+3]);best=max(best,total)
    return best
'''

MINXOR='''\
def minimize_xor_with_bit_count(num1,num2):
    needed=num2.bit_count();answer=0
    for bit in range(31,-1,-1):
        if needed and num1>>bit&1:answer|=1<<bit;needed-=1
    for bit in range(32):
        if needed and not answer>>bit&1:answer|=1<<bit;needed-=1
    return answer
'''

PREFIX='''\
def recover_array_from_prefix_xor(pref):
    result=[pref[0]]
    for previous,current in zip(pref,pref[1:]):result.append(previous^current)
    return result
'''


BATCH={
2422:entry('minimum_merges_to_palindrome',[('nums','list[int]')],'int',['arrays','two pointers','greedy'],['One operation replaces two adjacent elements by their sum.','Return the minimum operations needed to make the resulting array a palindrome.','All input values are positive.'],[([[4,3,2,1,2,3,1]],'Merging the leading four with three and later balancing the opposite side yields a palindrome in two operations.'),([[1,2,3,4]],'Three merges are required because no smaller sequence of adjacent sums can balance both ends.')],[[a] for a in [[1],[1,1],[1,2],[1,2,1],[1,2,2],[2,1,3],[1,3,2,2],[5,1,1,5],[1,1,1,3],[3,1,1,1],[2,4,1,5],[10,1,2,3,6],[1,4,5,1],[2,2,3,1]]],PALINDROME,[PALINDROME.replace('left_sum<right_sum','left_sum>right_sum'),PALINDROME.replace('operations+=1;continue','continue',1)],['Merges the larger side instead of the smaller side, moving its sum farther from equality.','Fails to count merges performed on the left side.'],palindrome_merge_oracle,random_palindrome_merge,['Compare accumulated values from the two ends.','Equal end sums can be fixed as matching palindrome entries and both pointers advance inward.','When unequal, merge the smaller side with its next inner value and count one operation.','Positive values mean only growing the smaller side can reach equality without wasting a necessary merge, so the greedy choices are forced.'],'O(n)','O(1)',5),
2425:entry('xor_of_all_pairings',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','bit manipulation'],['Form nums1[i] XOR nums2[j] for every cross-array index pair.','Return the XOR of all those pair values.','Repeated values and occurrences retain their index multiplicity.'],[([[2,1,3],[10,2,5,0]],'Each nums1 value appears four times and cancels; each nums2 value appears three times and contributes, yielding thirteen.'),([[1,2],[3,4]],'Every source value appears an even number of times across pairings, so the result is zero.')],[[a,b] for a,b in [([1],[2]),([1,2],[3]),([1],[2,3]),([0],[0]),([1,1],[2,2]),([5,6,7],[8,9]),([5,6],[7,8,9]),([0,1,2],[3,4,5]),([15],[1,2,3,4]),([2,2,3],[4]),([10,20,30],[1,1,1]),([7,8],[9,10]),([1,2,4,8],[16]),([31,0],[1,2,3])]],PAIRING,[PAIRING.replace('len(nums2)%2','len(nums1)%2',1),PAIRING.replace('answer^=value','answer|=value')],['Uses the first array’s parity to decide whether first-array values survive.','Combines contributions with OR instead of XOR, losing cancellation.'],pairing_xor_oracle,random_pairing_xor,['Each nums1 value occurs once for every nums2 position, and vice versa.','A value repeated an even number of times cancels under XOR; an odd count leaves one copy.','XOR nums1 only when len(nums2) is odd, and XOR nums2 only when len(nums1) is odd.','Expanding every pair XOR and regrouping identical source occurrences proves exactly those parity contributions.'],'O(n+m)','O(1)',5),
2428:entry('maximum_hourglass_sum',[('grid','list[list[int]]')],'int',['matrices','sliding windows'],['An hourglass uses three cells in a top row, the centered cell below, and three cells in the following row.','The grid has at least three rows and columns.','Return the maximum sum over all hourglass placements.'],[([[[6,2,1,3],[4,2,1,5],[9,2,8,7],[4,1,2,9]]],'The best seven-cell hourglass has sum thirty.'),([[[1,2,3],[4,5,6],[7,8,9]]],'The only hourglass sums the top and bottom rows plus center five, giving thirty-five.')],[[g] for g in [[[0,0,0],[0,0,0],[0,0,0]],[[-1,-2,-3],[-4,-5,-6],[-7,-8,-9]],[[9,1,1],[1,1,1],[1,1,9]],[[1,2,3,4],[5,6,7,8],[9,10,11,12]],[[1,2,3],[4,100,6],[7,8,9]],[[5,5,5,5],[5,5,5,5],[5,5,5,5],[5,5,5,5]],[[1,0,1],[0,9,0],[1,0,1]],[[10,1,1,10],[1,1,1,1],[10,1,1,10]],[[1,2,3,4,5],[5,4,3,2,1],[1,9,1,9,1]],[[3,1,4],[1,5,9],[2,6,5]],[[20,0,0],[0,0,0],[0,0,20]],[[1,1,1,1],[1,9,1,1],[1,1,1,1],[1,1,9,1]],[[2,4,6],[8,10,12],[14,16,18]],[[7,0,7,0],[0,7,0,7],[7,0,7,0]]]],HOURGLASS,[HOURGLASS.replace('+grid[row+1][column+1]','+sum(grid[row+1][column:column+3])'),HOURGLASS.replace('range(len(grid)-2)','range(len(grid)-3)')],['Includes all three middle-row cells instead of only the center.','Omits the last valid starting row.'],hourglass_oracle,random_hourglass,['Enumerate each top-left position with room for a three-by-three box.','Add the three top cells, the middle center, and the three bottom cells.','Track the maximum across every placement, initializing below possible negative sums.','Every hourglass has one such top-left coordinate and those seven terms, so enumeration is exact.'],'O(rows*columns)','O(1)',5),
2429:entry('minimize_xor_with_bit_count',[('num1','int'),('num2','int')],'int',['greedy','bit manipulation'],['Return an integer x with exactly as many set bits as num2.','Minimize x XOR num1; the answer is unique.','Inputs are positive 32-bit integers.'],[([3,5],'Both inputs have two set bits, so choosing x=3 makes the XOR zero.'),([1,12],'Two bits are required; retaining bit zero and adding bit one gives x=3 and minimum XOR two.')],[[a,b] for a,b in [(1,1),(1,2),(2,1),(7,1),(7,8),(8,7),(15,3),(10,5),(5,10),(31,16),(16,31),(6,9),(9,6),(100,7)]],MINXOR,[MINXOR.replace('range(31,-1,-1)','range(32)'),MINXOR.replace('range(32)','range(31,-1,-1)',1)],['Keeps low num1 bits before high bits, causing a larger XOR penalty at a missed high bit.','Adds required new bits from high to low instead of using the cheapest low zero bits.'],minimize_xor_oracle,random_minimize_xor,['Matching a set bit of num1 avoids a XOR difference, with higher bits more valuable to match.','First take set bits of num1 from most significant to least until the required count is met.','If more bits are needed, add them at zero positions from least significant upward.','The greedy ordering minimizes the lexicographically dominant XOR bit: avoid high differences first, then introduce only the lowest unavoidable differences.'],'O(1)','O(1)',5),
2433:entry('recover_array_from_prefix_xor',[('pref','list[int]')],'list[int]',['arrays','bit manipulation','prefix sums'],['pref[i] is nums[0] XOR ... XOR nums[i].','Recover and return the unique original nums array.','The input list is nonempty.'],[([[5,2,0,3,1]],'The first value is five and adjacent prefix XORs yield seven, two, three, and two.'),([[13]],'A one-element prefix array is identical to its original array.')],[[p] for p in [[0],[1,0],[1,1],[0,0,0],[1,2,3],[7,4,0],[5,5,5],[10,3,12,8],[1,3,7,15],[31,0,31],[2,6,4,12],[100,50,25],[9,8,7,6],[0,1,3,7,15]]],PREFIX,[PREFIX.replace('previous^current','pref[0]^current'),PREFIX.replace('result=[pref[0]]','result=[0]')],['XORs every later prefix with the first prefix instead of its immediate predecessor.','Assumes the first original value is zero rather than pref[0].'],prefix_xor_oracle,random_prefix_xor,['The first original value equals the first prefix XOR.','For i>0, pref[i-1] XOR pref[i] cancels all earlier original values and leaves nums[i].','Append pref[0], then XOR each adjacent prefix pair.','XOR self-cancellation proves each recovered value, and the defining prefix relation makes the reconstruction unique.'],'O(n)','O(n)',5),
}
