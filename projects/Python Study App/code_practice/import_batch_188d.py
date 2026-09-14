"""Three-part cost, keypad pushes, key changes, triangle type, and boundary-return batch."""
from .import_batch_055 import entry

def cost_oracle(a):
    nums=a[0];return min(nums[0]+nums[i]+nums[j] for i in range(1,len(nums)) for j in range(i+1,len(nums)))
def random_cost(r):return [[r.randint(1,100) for _ in range(r.randint(3,30))]]
def pushes_oracle(a):return sum(index//8+1 for index in range(len(a[0])))
def random_pushes(r):
    chars=list('abcdefghijklmnopqrstuvwxyz');r.shuffle(chars);return [''.join(chars[:r.randint(1,26)])]
def changes_oracle(a):return sum(left.lower()!=right.lower() for left,right in zip(a[0],a[0][1:]))
def random_changes(r):return [''.join(r.choice('abcABC') for _ in range(r.randint(1,100)))]
def triangle_oracle(a):
    x,y,z=sorted(a[0])
    if x+y<=z:return 'none'
    kinds=len({x,y,z})
    return 'equilateral' if kinds==1 else 'isosceles' if kinds==2 else 'scalene'
def random_triangle(r):return [[r.randint(1,100) for _ in range(3)]]
def boundary_oracle(a):
    position=answer=0
    for move in a[0]:
        position+=move;answer+=position==0
    return answer
def random_boundary(r):return [[r.randint(-10,10) for _ in range(r.randint(1,100))]]

COST='''\
def minimum_three_subarray_cost(nums):
    first,second=sorted(nums[1:])[:2]
    return nums[0]+first+second
'''
PUSHES='''\
def minimum_keypad_pushes(word):
    return sum(index//8+1 for index in range(len(word)))
'''
CHANGES='''\
def case_insensitive_key_changes(s):
    return sum(a.lower()!=b.lower() for a,b in zip(s,s[1:]))
'''
TRIANGLE='''\
def classify_triangle(nums):
    a,b,c=sorted(nums)
    if a+b<=c:return 'none'
    distinct=len({a,b,c})
    if distinct==1:return 'equilateral'
    if distinct==2:return 'isosceles'
    return 'scalene'
'''
BOUNDARY='''\
def ant_boundary_returns(nums):
    position=answer=0
    for move in nums:
        position+=move
        if position==0:answer+=1
    return answer
'''

BATCH={
3010:entry('minimum_three_subarray_cost',[('nums','list[int]')],'int',['arrays','sorting','greedy'],['Partition nums into exactly three nonempty contiguous subarrays.','The cost is the sum of the first value of each subarray.','Return the minimum possible cost.'],[([[1,2,3,12]],'The first value is fixed at one; choosing starts two and three gives total six.'),([[5,4,3]],'All three single-element parts are forced, costing twelve.')],[[x] for x in [[1,2,3],[5,4,3],[1,2,3,12],[10,1,1],[3,9,2,8],[100,1,50,2],[4,4,4,4],[1,100,99,98],[8,7,6,5,4],[2,10,1,9,3],[9,3,7],[6,2,8,1],[5,10,20,1],[7,6,5,10,1]]],COST,[COST.replace('nums[1:]','nums'),COST.replace('[:2]','[-2:]')],['Allows the fixed first element to serve as another subarray start.','Chooses the two largest later starts instead of the smallest.'],cost_oracle,random_cost,['The first subarray must begin at index zero.','The second and third starts may be any two distinct later indices in increasing order.','Choose the two smallest values in nums[1:] and add nums[0].','Any pair of later indices defines a valid three-part partition, so minimizing their values independently is sufficient.'],'O(n log n)','O(n)',3),
3014:entry('minimum_keypad_pushes',[('word','str')],'int',['strings','greedy','counting'],['Assign the distinct letters of word to eight telephone keys.','The first letter assigned to a key costs one push, the second costs two, and so on.','Every character in this version appears once; return the minimum total pushes.'],[(['abcde'],'Five letters fit in first positions and require five pushes.'),(['xycdefghij'],'Eight letters cost one push and two additional letters cost two each, totaling twelve.')],[[s] for s in ['a','ab','abcdefgh','abcdefghi','abcdefghij','abcdefghijklmnop','abcdefghijklmnopq','abcdefghijklmnopqrstuvwxyz','xyz','qwerty','abcdefghijk','abcdefghijklmnopqrst','mnopqrstuv','code']],PUSHES,[PUSHES.replace('//8','//9'),PUSHES.replace('+1','+2')],['Places nine letters at each push depth despite having only eight keys.','Charges every letter one extra push.'],pushes_oracle,random_pushes,['Use all eight one-push positions before any two-push position.','Because letters occur once, their identities do not affect cost.','The zero-based assignment index has cost floor(index/8)+1.','Filling shallower positions first is optimal by exchange: moving any letter from a deeper open slot to a shallower one reduces cost.'],'O(n)','O(1)',3),
3019:entry('case_insensitive_key_changes',[('s','str')],'int',['strings','adjacent comparisons'],['Treat uppercase and lowercase forms of the same letter as the same keyboard key.','Count adjacent positions where the key changes.','Return the number of changes while reading the string left to right.'],[(['aAbBcC'],'Case changes alone do not count; transitions a-to-b and b-to-c give two.'),(['AaAaAaaA'],'Every character uses the same key, so the answer is zero.')],[[s] for s in ['a','aA','ab','aAbBcC','AaAaAaaA','abc','ABC','aBa','zzZZy','Code','cODE','xYz','mmNnn','aabbcc']],CHANGES,[CHANGES.replace('.lower()','',1),CHANGES.replace('!=','==')],['Treats a case-only transition as a key change.','Counts unchanged adjacent keys instead of changed ones.'],changes_oracle,random_changes,['Normalize character case before comparing keys.','Compare each character with its immediate predecessor.','Add one exactly when their lowercase forms differ.','Every key transition lies between one adjacent pair, and every differing adjacent pair is one transition.'],'O(n)','O(1)',3),
3024:entry('classify_triangle',[('nums','list[int]')],'str',['arrays','geometry','sorting'],['The three positive integers are proposed side lengths.','Return none if they cannot form a nondegenerate triangle.','Otherwise return equilateral, isosceles, or scalene according to how many side lengths are equal.'],[([[3,3,3]],'All sides are equal and satisfy the triangle inequality, so the type is equilateral.'),([[3,4,5]],'The valid triangle has three distinct sides, so it is scalene.')],[[x] for x in [[1,1,1],[1,1,2],[1,2,3],[2,2,3],[3,3,3],[3,4,5],[5,4,3],[2,3,4],[10,10,19],[10,10,20],[4,5,8],[7,8,9],[100,1,1],[6,6,10]]],TRIANGLE,[TRIANGLE.replace('a+b<=c','a+b<c'),TRIANGLE.replace("distinct==2","distinct<=2")],['Accepts degenerate sides whose two smaller lengths equal the largest.','Misclassifies equilateral triangles as isosceles after the first branch is altered below.'],triangle_oracle,random_triangle,['Sort so only the two smaller sides need be compared with the largest.','If their sum is no greater than the largest, no triangle exists.','For a valid triangle, classify by the number of distinct side lengths.','The triangle inequality and equality partition cover every possible triple exactly once.'],'O(1)','O(1)',3),
3028:entry('ant_boundary_returns',[('nums','list[int]')],'int',['arrays','prefix sums','simulation'],['An ant starts at boundary position zero.','Each value is its signed movement during one time step.','Count how many step endpoints place the ant back at position zero; the initial position does not count.'],[([[2,3,-5]],'The prefix positions are two, five, and zero, so the boundary is reached once.'),([[3,2,-3,-4]],'The prefix positions are three, five, two, and negative two, never zero.')],[[x] for x in [[1],[-1],[0],[2,3,-5],[3,2,-3,-4],[1,-1,1,-1],[5,-5,5],[-2,2,-2,2],[1,2,-1,-2],[10,-3,-7],[0,0],[4,-2,-2,1,-1],[3,-1,-2,6,-6],[2,-1,-1,2,-2]]],BOUNDARY,[BOUNDARY.replace('position==0','position<=0'),BOUNDARY.replace('position=answer=0','position=answer=1')],['Counts positions left of the boundary as if they were on it.','Starts away from zero and with a pre-counted return.'],boundary_oracle,random_boundary,['Maintain the ant’s current coordinate as a running prefix sum.','Add each movement in order.','Increment the answer whenever the new prefix sum equals zero.','The coordinate after each step is exactly its prefix sum, so zero prefixes correspond one-for-one with counted returns.'],'O(n)','O(1)',3),
}
BATCH[3024]['wrong'][1]=TRIANGLE.replace("return 'equilateral'","return 'isosceles'")
