"""Bench occupancy, good elements, exact runs, digit reduction, and parity transformation."""
from collections import defaultdict
from .import_batch_055 import entry

def bench_oracle(a):
    benches=defaultdict(set)
    for student,bench in a[0]:benches[bench].add(student)
    return max(map(len,benches.values()),default=0)
def random_bench(r):return [[[r.randint(1,20),r.randint(1,8)] for _ in range(r.randint(0,60))]]
def good_oracle(a):
    nums,k=a;return sum(v for i,v in enumerate(nums) if (i<k or v>nums[i-k]) and (i+k>=len(nums) or v>nums[i+k]))
def random_good(r):
    n=r.randint(1,30);return [[r.randint(-20,30) for _ in range(n)],r.randint(1,n)]
def special_oracle(a):
    s,k=a;return any(j-i==k for i in range(len(s)) for j in range(i+1,len(s)+1) if (i==0 or s[i-1]!=s[i]) and (j==len(s) or s[j]!=s[i]) and len(set(s[i:j]))==1)
def random_special(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,40))),r.randint(1,10)]
def digits_oracle(a):
    values=list(map(int,a[0]))
    while len(values)>2:values=[(x+y)%10 for x,y in zip(values,values[1:])]
    return values[0]==values[1]
def random_digits(r):return [''.join(str(r.randrange(10)) for _ in range(r.randint(3,30)))]
def parity_oracle(a):return sorted(v%2 for v in a[0])
def random_parity(r):return [[r.randint(0,1000) for _ in range(r.randint(1,50))]]

BENCH='''def maximum_unique_students_on_bench(students):
    benches={}
    for student,bench in students:benches.setdefault(bench,set()).add(student)
    return max((len(group) for group in benches.values()),default=0)
'''
GOOD='''def sum_k_neighbor_good_numbers(nums,k):
    answer=0
    for i,value in enumerate(nums):
        if i>=k and value<=nums[i-k]:continue
        if i+k<len(nums) and value<=nums[i+k]:continue
        answer+=value
    return answer
'''
SPECIAL='''def has_exact_character_run(s,k):
    start=0
    while start<len(s):
        end=start+1
        while end<len(s) and s[end]==s[start]:end+=1
        if end-start==k:return True
        start=end
    return False
'''
DIGITS='''def final_two_digits_are_equal(s):
    values=[int(char) for char in s]
    while len(values)>2:values=[(a+b)%10 for a,b in zip(values,values[1:])]
    return values[0]==values[1]
'''
PARITY='''def transform_array_by_parity(nums):
    even=sum(value%2==0 for value in nums)
    return [0]*even+[1]*(len(nums)-even)
'''

BATCH={
3450:entry('maximum_unique_students_on_bench',[('students','list[list[int]]')],'int',['arrays','hash maps','sets'],['Each record is [student_id, bench_id].','Count a student only once per bench even if the same record repeats.','Return the largest unique-student count on one bench, or zero for no records.'],[([[[1,2],[2,2],[3,3],[1,3],[2,3]]],'Bench three has three distinct students, the maximum.'),([[]],'No bench has a student, so return zero.')],[[x] for x in [[[1,1]],[[1,1],[1,1]],[[1,1],[2,1]],[[1,1],[1,2]],[[1,1],[2,2]],[[1,2],[2,2],[3,2]],[[1,1],[2,1],[1,2]],[[3,3],[3,3],[4,3]],[[1,5],[2,5],[3,6]],[[9,1],[8,1],[7,1],[6,2]],[[1,2],[2,2],[1,2]],[[4,4],[5,4],[4,5]],[[10,2],[11,2],[12,3]],[[1,1],[2,1],[3,1],[4,1]]]],BENCH,[BENCH.replace('.add(student)','.add(bench)'),BENCH.replace('default=0','default=1')],['Counts the bench ID instead of distinct students.','Returns one rather than zero for empty input.'],bench_oracle,random_bench,['Map every bench to a set of student IDs.','Set insertion automatically removes repeated records on the same bench.','Take the largest set size.','An empty mapping uses the required default of zero.'],'O(records)','O(records)',3),
3452:entry('sum_k_neighbor_good_numbers',[('nums','list[int]'),('k','int')],'int',['arrays','local comparisons'],['A value is good when it is strictly greater than the value k positions before it, if that position exists.','It must also exceed the value k positions after it, when present.','Return the sum of all good values.'],[([[1,3,2,1,5,4],2],'The good values are three, five, and four, whose sum is twelve.'),([[5],1],'With no k-distance neighbors, the lone value is good.')],[[n,k] for n,k in [([1],1),([1,2],1),([2,1],1),([1,3,2,1,5,4],2),([1,1,1],1),([3,2,1],2),([1,2,3],2),([5,1,5],1),([-1,0,1],1),([10,1,2,9],2),([2,4,6,8],1),([8,6,4,2],1),([1,5,2,6,3],2),([7,0,7,0],2)]],GOOD,[GOOD.replace('value<=nums[i-k]','value<nums[i-k]'),GOOD.replace('i+k<len(nums)','i+k<=len(nums)-2')],['Allows equality with a preceding neighbor despite strictness.','Ignores a valid final k-distance comparison.'],good_oracle,random_good,['For every index, check the predecessor only if it exists.','Check the successor under the same rule.','Add the value only if every existing comparison is strictly greater.','Boundary positions naturally omit nonexistent neighbors.'],'O(n)','O(1)',3),
3456:entry('has_exact_character_run',[('s','str'),('k','int')],'bool',['strings','runs'],['Find a substring of exactly k copies of one character.','If a neighboring character exists before or after it, that neighbor must differ.','Equivalently, determine whether s has a maximal equal-character run of length k.'],[(['aaabaaa',3],'Both aaa runs are maximal and have exactly length three.'),(['aaaa',3],'The only maximal run has length four, so no length-three special substring exists.')],[[s,k] for s,k in [('a',1),('a',2),('aa',1),('aa',2),('ab',1),('aaa',3),('aaaa',3),('aaabaaa',3),('abbba',3),('aabbaa',2),('abc',2),('zzzy',3),('xyyyyx',4),('aabbccc',3)]],SPECIAL,[SPECIAL.replace('==k','>=k'),SPECIAL.replace('start=end','start+=1')],['Accepts a longer run as containing a special length-k substring.','Advances within a run and can treat a nonmaximal suffix as a run.'],special_oracle,random_special,['Partition s into maximal runs of equal characters.','A run already satisfies the different-neighbor boundary rule.','Return true if any run length equals k exactly.','Longer runs must not qualify because an adjacent same character would violate the boundary.'],'O(n)','O(1)',3),
3461:entry('final_two_digits_are_equal',[('s','str')],'bool',['strings','simulation'],['Repeatedly replace every adjacent digit pair by its sum modulo ten.','Each round shortens the sequence by one while preserving pair order.','When two digits remain, return whether they are equal.'],[(['3902'],'The rounds are 292 then 11, whose final digits match.'),(['34789'],'The final two digits differ.')],[[s] for s in ['000','111','123','909','3902','34789','9999','1010','55555','12345','98765','10001','24680','314159']],DIGITS,[DIGITS.replace('%10','%9'),DIGITS.replace('values[0]==values[1]','values[0]!=values[1]')],['Reduces sums modulo nine instead of ten.','Returns whether the final digits differ.'],digits_oracle,random_digits,['Convert the string into a digit list.','Build each next round from adjacent sums modulo ten.','Repeat until exactly two values remain.','The simulation matches every specified round and directly compares the final pair.'],'O(n^2)','O(n)',3),
3467:entry('transform_array_by_parity',[('nums','list[int]')],'list[int]',['arrays','sorting','counting'],['Replace each even number by zero and each odd number by one.','Sort the transformed values in nondecreasing order.','Return the resulting array.'],[([[4,3,2,1]],'Two even values become zeros followed by two ones from the odd values.'),([[2,4,6]],'Every value is even, producing three zeros.')],[[x] for x in [[0],[1],[2],[1,2],[4,3,2,1],[2,4,6],[1,3,5],[0,1,0,1],[10,11,12],[99,100],[7,8,9,10],[2,1,2,1,2],[1000,999],[5,4,3,2,1]]],PARITY,[PARITY.replace('value%2==0','value%2==1'),PARITY.replace('[0]*even+[1]*(len(nums)-even)','[1]*(len(nums)-even)+[0]*even')],['Counts odd values as zeros.','Returns the transformed values in descending rather than nondecreasing order.'],parity_oracle,random_parity,['Count how many input values are even.','Every even value contributes one zero and every remaining value contributes one one.','Sorted binary values place all zeros before all ones.','Constructing those two blocks avoids a comparison sort.'],'O(n)','O(n)',3),
}
