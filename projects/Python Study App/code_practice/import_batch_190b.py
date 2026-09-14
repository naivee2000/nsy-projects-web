"""Duplicate XOR, divisible pairs, chair occupancy, adjacent OR, and digit clearing."""
from collections import Counter
from .import_batch_055 import entry

def duplicate_oracle(a):
    counts=Counter(a[0]);answer=0
    for value,count in counts.items():
        if count==2:answer^=value
    return answer
def random_duplicate(r):
    values=[]
    for x in range(1,r.randint(2,20)):
        values.extend([x]*r.randint(1,2))
    r.shuffle(values);return [values]
def pairs_oracle(a):return sum(x%(y*a[2])==0 for x in a[0] for y in a[1])
def random_pairs(r):return [[r.randint(1,100) for _ in range(r.randint(1,20))],[r.randint(1,30) for _ in range(r.randint(1,20))],r.randint(1,10)]
def chairs_oracle(a):
    current=best=0
    for event in a[0]:current+=1 if event=='E' else -1;best=max(best,current)
    return best
def random_chairs(r):
    s=[];inside=0
    for _ in range(r.randint(1,50)):
        if inside==0 or r.random()<.6:s.append('E');inside+=1
        else:s.append('L');inside-=1
    return [''.join(s)]
def adjacent_oracle(a):return [x|y for x,y in zip(a[0],a[0][1:])]
def random_adjacent(r):return [[r.randint(0,1000) for _ in range(r.randint(2,50))]]
def clear_oracle(a):
    out=[]
    for char in a[0]:
        if char.isdigit():out.pop()
        else:out.append(char)
    return ''.join(out)
def random_clear(r):
    out=[];letters=0
    for _ in range(r.randint(1,50)):
        if letters and r.random()<.35:out.append(str(r.randint(0,9)));letters-=1
        else:out.append(r.choice('abcde'));letters+=1
    return [''.join(out)]

DUPLICATE='''\
def xor_values_appearing_twice(nums):
    seen=set();answer=0
    for value in nums:
        if value in seen:answer^=value
        else:seen.add(value)
    return answer
'''
PAIRS='''\
def count_scaled_divisible_pairs(nums1,nums2,k):
    return sum(a%(b*k)==0 for a in nums1 for b in nums2)
'''
CHAIRS='''\
def minimum_waiting_room_chairs(s):
    occupied=answer=0
    for event in s:
        occupied+=1 if event=='E' else -1
        answer=max(answer,occupied)
    return answer
'''
ADJACENT='''\
def adjacent_bitwise_or(nums):
    return [a|b for a,b in zip(nums,nums[1:])]
'''
CLEAR='''\
def clear_digits_and_left_letters(s):
    stack=[]
    for char in s:
        if char.isdigit():stack.pop()
        else:stack.append(char)
    return ''.join(stack)
'''

BATCH={
3158:entry('xor_values_appearing_twice',[('nums','list[int]')],'int',['arrays','sets','bit manipulation'],['Every value appears either once or twice.','Take the bitwise XOR of the values that appear exactly twice.','Return zero when no value is duplicated.'],[([[1,2,1,3]],'Only one appears twice, so the XOR is one.'),([[1,2,3]],'No value appears twice, so return zero.')],[[x] for x in [[1],[1,1],[1,2,1,3],[1,2,3],[1,1,2,2],[5,4,5,4],[7,8,9,7],[10,10,20],[1,2,3,2],[4,5,6,4,6],[9,9],[2,3,2,4,3],[100,1,100],[8,7,6,5]]],DUPLICATE,[DUPLICATE.replace('answer^=value','answer+=value'),DUPLICATE.replace('if value in seen','if value not in seen')],['Adds duplicate values instead of XOR-ing them.','XORs first occurrences rather than second occurrences.'],duplicate_oracle,random_duplicate,['A set distinguishes first from second occurrence under the at-most-twice promise.','Store unseen values without changing the answer.','On the second occurrence, XOR that value into the answer.','Each exactly-twice value contributes once and every singleton contributes zero times.'],'O(n)','O(n)',3),
3162:entry('count_scaled_divisible_pairs',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'int',['arrays','enumeration','divisibility'],['An index pair i,j is good when nums1[i] is divisible by nums2[j]*k.','Count pairs by index, so repeated values create separate pairs.','Return the number of good pairs.'],[([[1,3,4],[1,3,4],1],'Five index pairs satisfy the divisibility condition.'),([[1,2,4,12],[2,4],3],'Only twelve is divisible by six and twelve, giving two pairs.')],[[a,b,k] for a,b,k in [([1],[1],1),([1],[2],1),([2],[1],2),([1,3,4],[1,3,4],1),([1,2,4,12],[2,4],3),([4,4],[2],1),([10,20],[5,10],2),([6,12],[2,3],1),([7,14],[7],2),([100],[10],10),([9,18,27],[3],3),([8,16],[2,4],2),([5,10,15],[5],1),([2,3,5],[1],4)]],PAIRS,[PAIRS.replace('b*k','b+k'),PAIRS.replace('==0','!=0')],['Divides by b+k instead of the product b*k.','Counts nondivisible pairs instead of divisible ones.'],pairs_oracle,random_pairs,['The source-I constraints permit checking each Cartesian-product pair.','For a,b test whether the remainder modulo b*k is zero.','Add the Boolean result for every index combination.','The nested iteration visits each index pair once, preserving multiplicity exactly.'],'O(nm)','O(1)',3),
3168:entry('minimum_waiting_room_chairs',[('s','str')],'int',['strings','prefix sums','simulation'],['E means one person enters and needs a chair; L means one person leaves.','No one leaves an empty room.','Return the minimum chairs needed so every entrant can sit.'],[(['EEEEEEE'],'Seven simultaneous occupants require seven chairs.'),(['ELELEEL'],'The maximum simultaneous occupancy is two.')],[[s] for s in ['E','EL','EE','EEL','EEEEEEE','ELELEEL','EEELLL','ELEL','EELL','EEELELL','ELLEE','EEEE', 'EELLEL','EELEELLL']],CHAIRS,[CHAIRS.replace("1 if event=='E' else -1","1"),CHAIRS.replace('max(answer,occupied)','occupied')],['Treats leaving as another entrance.','Returns final occupancy instead of the maximum prefix occupancy.'],chairs_oracle,random_chairs,['Current occupancy is the prefix sum of entrances as +1 and leaves as -1.','Track that value while scanning events.','The answer is the maximum occupancy reached.','A chair can be reused after a leave, while at each time at least current occupancy chairs are necessary, making the maximum both sufficient and minimal.'],'O(n)','O(1)',3),
3173:entry('adjacent_bitwise_or',[('nums','list[int]')],'list[int]',['arrays','bit manipulation'],['For every adjacent pair nums[i],nums[i+1], compute their bitwise OR.','Return these n-1 results in index order.','The input contains at least two values.'],[([[1,3,7,15]],'The adjacent OR values are three, seven, and fifteen.'),([[8,4]],'Eight OR four sets both bits and equals twelve.')],[[x] for x in [[0,0],[1,1],[1,2],[8,4],[1,3,7,15],[2,4,8],[7,0,1],[5,10,5],[15,16],[3,6,12],[100,50,25],[1,2,1,2],[0,1,0],[9,8,7,6]]],ADJACENT,[ADJACENT.replace('a|b','a&b'),ADJACENT.replace('nums[1:]','nums[2:]')],['Uses bitwise AND instead of OR.','Pairs values two positions apart and returns too few elements.'],adjacent_oracle,random_adjacent,['Zip nums with its one-position suffix to enumerate adjacent pairs.','Apply bitwise OR to each pair.','Collect results in the same order.','The zip creates exactly pairs (0,1) through (n-2,n-1), so no adjacency is missing or duplicated.'],'O(n)','O(n)',3),
3174:entry('clear_digits_and_left_letters',[('s','str')],'str',['strings','stacks','simulation'],['Process s from left to right.','Each digit removes itself and the closest remaining nondigit character to its left.','The input guarantees a nondigit is available for every digit; return the final string.'],[(['abc'],'No digit appears, so the string remains abc.'),(['cb34'],'Three removes b and four then removes c, leaving the empty string.')],[[s] for s in ['a','abc','a1','ab1','ab12','cb34','a1b2','abc3d','xy1z2','code4','a0b0c0','abcd12','q1wert2','stack5x']],CLEAR,[CLEAR.replace('stack.pop()','stack.pop(0)'),CLEAR.replace('if char.isdigit()','if not char.isdigit()')],['Removes the farthest-left remaining character instead of the closest-left one.','Treats letters as removal commands and digits as retained text.'],clear_oracle,random_clear,['Remaining nondigits to the left are naturally stored in encounter order.','A digit must remove the most recent such character, which is the top of a stack.','Push nondigits and pop once for digits, then join the stack.','The stack top is always the closest character not already removed, matching each operation.'],'O(n)','O(n)',3),
}
BATCH[3174]['wrong'][1]=CLEAR.replace('stack.pop()','stack.append(char)')
