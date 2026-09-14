"""Unique-digit, matrix replacement, fixed-score operations, border pairs, and split feasibility."""
from collections import Counter
from .import_batch_055 import entry

def unique_digits(value):return len(set(str(value)))==len(str(value))
def unique_oracle(a):return sum(unique_digits(value) for value in range(a[0],a[1]+1))
def random_unique(r):
    low=r.randint(1,9000);return [low,r.randint(low,min(10000,low+500))]
def matrix_oracle(a):
    matrix=a[0];maximum=[max(row[j] for row in matrix) for j in range(len(matrix[0]))]
    return [[maximum[j] if value==-1 else value for j,value in enumerate(row)] for row in matrix]
def random_matrix(r):
    rows,cols=r.randint(1,8),r.randint(1,8);return [[[r.choice([-1]+list(range(10))) for _ in range(cols)] for _ in range(rows)]]
def operations_oracle(a):
    nums=a[0];score=nums[0]+nums[1];count=0
    for i in range(0,len(nums)-1,2):
        if nums[i]+nums[i+1]!=score:break
        count+=1
    return count
def random_operations(r):return [[r.randint(1,20) for _ in range(r.randint(2,30))]]
def borders_oracle(a):
    words=a[0];return sum(words[j].startswith(words[i]) and words[j].endswith(words[i]) for i in range(len(words)) for j in range(i+1,len(words)))
def random_borders(r):return [[''.join(r.choice('abc') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,20))]]
def split_oracle(a):
    counts=Counter(a[0]);return all(count<=2 for count in counts.values())
def random_split(r):return [[r.randint(1,15) for _ in range(2*r.randint(1,20))]]

UNIQUE='''\
def count_unique_digit_numbers(a,b):
    answer=0
    for value in range(a,b+1):
        digits=str(value)
        if len(set(digits))==len(digits):answer+=1
    return answer
'''
MATRIX='''\
def replace_negative_ones_by_column_maximum(matrix):
    answer=[row[:] for row in matrix]
    for column in range(len(matrix[0])):
        maximum=max(row[column] for row in matrix)
        for row in range(len(matrix)):
            if answer[row][column]==-1:answer[row][column]=maximum
    return answer
'''
OPERATIONS='''\
def maximum_fixed_score_front_operations(nums):
    score=nums[0]+nums[1];answer=0
    for i in range(0,len(nums)-1,2):
        if nums[i]+nums[i+1]!=score:break
        answer+=1
    return answer
'''
BORDERS='''\
def count_prefix_suffix_word_pairs(words):
    answer=0
    for i in range(len(words)):
        for j in range(i+1,len(words)):
            answer+=words[j].startswith(words[i]) and words[j].endswith(words[i])
    return answer
'''
SPLIT='''\
def can_split_into_unique_halves(nums):
    from collections import Counter
    return max(Counter(nums).values())<=2
'''

BATCH={
3032:entry('count_unique_digit_numbers',[('a','int'),('b','int')],'int',['math','digits','sets'],['Count integers in the inclusive range a through b.','A value qualifies only when every decimal digit occurs once.','Return the number of qualifying values.'],[([1,20],'Every value qualifies except eleven, giving nineteen.'),([9,19],'Nine, ten, twelve through nineteen qualify; eleven is excluded, giving ten.')],[[a,b] for a,b in [(1,1),(9,9),(10,10),(11,11),(98,102),(100,110),(120,130),(1,20),(9,19),(500,550),(987,1023),(1000,1010),(9000,9100),(1,10000)]],UNIQUE,[UNIQUE.replace('len(set(digits))==len(digits)','len(set(digits))<=len(digits)'),UNIQUE.replace('range(a,b+1)','range(a,b)')],['Accepts every number because a set can never exceed the string length.','Treats the inclusive upper bound as exclusive.'],unique_oracle,random_unique,['Inspect each value independently within the small range.','Convert a number to decimal text and compare its set size with its digit count.','Equal sizes mean no digit was repeated.','The inclusive loop visits every candidate once and the size equality is equivalent to digit uniqueness.'],'O((b-a+1)*digits)','O(digits)',3),
3033:entry('replace_negative_ones_by_column_maximum',[('matrix','list[list[int]]')],'list[list[int]]',['matrices','column scans'],['For every -1 cell, replace it with the greatest original value in the same column.','Nonnegative cells remain unchanged.','Return a modified copy of the rectangular matrix.'],[([[[1,2,-1],[4,-1,6],[7,8,9]]],'Column maxima are seven, eight, and nine, producing [[1,2,9],[4,8,6],[7,8,9]].'),([[3,-1],[-1,2]],'The replacements use column maxima three and two, producing [[3,2],[3,2]].')],[[x] for x in [[[1]], [[-1],[2]], [[1,-1]], [[3,-1],[-1,2]], [[-1,-1],[4,5]], [[1,2],[3,4]], [[-1],[0],[9]], [[1,-1,3],[4,5,-1]], [[-1,-1,-1],[1,2,3]], [[5,4],[3,-1],[2,9]], [[0,-1],[0,0]], [[9,-1,1],[-1,8,2]], [[2,3,4],[-1,-1,-1]], [[7,6],[5,4],[3,2]]]],MATRIX,[MATRIX.replace('row[column] for row in matrix','max(row) for row in matrix'),MATRIX.replace('== -1','<1')],['Uses each row maximum rather than the current column maximum.','Replaces zeros as well as -1 cells.'],matrix_oracle,random_matrix,['Compute replacements one column at a time from the original matrix.','Find the maximum value among all rows in that column.','Write that value only into copied cells equal to -1.','Column-local scanning gives every placeholder exactly its declared maximum while copying protects the caller’s input.'],'O(rows*columns)','O(rows*columns)',3),
3038:entry('maximum_fixed_score_front_operations',[('nums','list[int]')],'int',['arrays','simulation'],['Each operation removes the first two remaining elements.','The first removed pair establishes a score equal to its sum.','Continue while every later removed pair has the same score; return the maximum operation count.'],[([[3,2,1,4,5]],'The pairs 3+2 and 1+4 both score five; one value remains, so two operations succeed.'),([[3,2,6,1,4]],'The second pair scores seven rather than five, so only one operation succeeds.')],[[x] for x in [[1,1],[1,2],[3,2,1,4,5],[3,2,6,1,4],[1,2,1,2],[1,2,2,1],[5,5,5,5],[1,9,2,8,3,7],[1,1,2],[10,1,5,6,7],[2,3,4,1,9,0],[4,2,3,3,1,5],[7,8,15,0],[100,1,50,51]]],OPERATIONS,[OPERATIONS.replace('!=score','==score'),OPERATIONS.replace('len(nums)-1','len(nums)-2')],['Stops on matching pairs instead of the first mismatching pair.','Skips the final complete pair for even-length input.'],operations_oracle,random_operations,['After each front removal, the next operation always uses the next two original positions.','Store the sum of indices zero and one.','Scan disjoint consecutive pairs until one differs, counting matches.','The forced removal order leaves no alternative choices, so the first mismatch ends every valid continuation.'],'O(n)','O(1)',3),
3042:entry('count_prefix_suffix_word_pairs',[('words','list[str]')],'int',['strings','enumeration'],['For every index pair i<j, inspect words[i] and words[j].','The pair qualifies when words[i] is both a prefix and a suffix of words[j].','Return the number of qualifying index pairs, counting repeated words by position.'],[([['a','aba','ababa','aa']],'The pairs (a,aba), (a,ababa), (a,aa), and (aba,ababa) qualify.'),([['pa','papa','ma','mama']],'pa borders papa and ma borders mama, giving two pairs.')],[[x] for x in [[['a']], [['a','a']], [['a','b']], [['a','ab']], [['a','ba']], [['ab','abab']], [['ab','aba']], [['a','aba','ababa','aa']], [['pa','papa','ma','mama']], [['x','xx','xxx']], [['abc','abc']], [['ab','cab']], [['aa','aaa','aaaa']], [['z','az','za','aza']]]],BORDERS,[BORDERS.replace('and words[j].endswith(words[i])','or words[j].endswith(words[i])'),BORDERS.replace('range(i+1,len(words))','range(i,len(words))')],['Counts words having only one of the required border relations.','Allows i=j, so every word incorrectly pairs with itself.'],borders_oracle,random_borders,['The source-I limits permit checking every ordered index pair.','Use startswith and endswith for the two border conditions.','Count only when both hold and i is strictly before j.','Every allowable pair is visited once, and the two predicates directly implement the definition.'],'O(n^2*word length)','O(1)',3),
3046:entry('can_split_into_unique_halves',[('nums','list[int]')],'bool',['arrays','hash maps','counting'],['Split an even-length array into two arrays of equal length.','Each result must contain distinct values internally.','Return whether such a split exists; original order need not be preserved.'],[([[1,1,2,2,3,4]],'Place one copy of repeated values one and two in each half, then distribute three and four.'),([[1,1,1,1]],'Four copies of one cannot fit into two halves without repetition.')],[[x] for x in [[1,2],[1,1],[1,1,2,2,3,4],[1,1,1,1],[1,2,3,4],[1,1,2,3],[2,2,3,3],[1,2,2,2],[5,5,6,7,8,9],[1,1,2,2],[9,8,7,6],[3,3,4,4,5,5],[1,2,3,1,2,3],[10,10,20,30]]],SPLIT,[SPLIT.replace('<=2','<2'),SPLIT.replace('max(Counter(nums).values())','len(Counter(nums))')],['Rejects values appearing exactly twice even though one copy fits in each half.','Tests the number of distinct values against two rather than the maximum multiplicity.'],split_oracle,random_split,['A value can appear at most once in each of the two result arrays.','Therefore any frequency above two is impossible.','If all frequencies are at most two, put duplicate copies on opposite sides and balance singleton values.','The two equal-sized halves have total capacity n and duplicates consume one slot per side, so remaining singleton slots balance.'],'O(n)','O(distinct values)',3),
}
BATCH[3033]['examples'][1]=([[[3,-1],[-1,2]]],'The replacements use column maxima three and two, producing [[3,2],[3,2]].')
BATCH[3042]['boundaries']=[[x] for x in [['a'],['a','a'],['a','b'],['a','ab'],['a','ba'],['ab','abab'],['ab','aba'],['a','aba','ababa','aa'],['pa','papa','ma','mama'],['x','xx','xxx'],['abc','abc'],['ab','cab'],['aa','aaa','aaaa'],['z','az','za','aza']]]
BATCH[3033]['boundaries']=[args for args in BATCH[3033]['boundaries'] if args!=[[[3,-1],[-1,2]]]]
BATCH[3042]['boundaries']=[args for args in BATCH[3042]['boundaries'] if args not in [[['a','aba','ababa','aa']],[['pa','papa','ma','mama']]]]
BATCH[3033]['wrong'][1]=MATRIX.replace('==-1','<=0')
