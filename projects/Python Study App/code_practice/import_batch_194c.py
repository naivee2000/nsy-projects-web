"""Coupon validation, digit divisibility, ride scheduling, trionic arrays, and submatrix flips."""
from .import_batch_055 import entry

LINES=['electronics','grocery','pharmacy','restaurant']
def coupon_oracle(a):
    code,line,active=a;valid=[]
    for c,b,on in zip(code,line,active):
        if on and b in LINES and c and all(ch.isalnum() or ch=='_' for ch in c):valid.append((LINES.index(b),c))
    return [c for _,c in sorted(valid)]
def random_coupon(r):
    n=r.randint(1,20);return [[''.join(r.choice('ab12_@') for _ in range(r.randint(0,6))) for _ in range(n)],[r.choice(LINES+['other']) for _ in range(n)],[r.choice([True,False]) for _ in range(n)]]
def digit_div_oracle(a):
    digits=list(map(int,str(a[0])));p=1
    for d in digits:p*=d
    return a[0]%(sum(digits)+p)==0
def random_digit_div(r):return [r.randint(1,1000000)]
def rides_oracle(a):
    ls,ld,ws,wd=a;best=10**18
    for a0,a1 in zip(ls,ld):
        for b0,b1 in zip(ws,wd):best=min(best,max(a0+a1,b0)+b1,max(b0+b1,a0)+a1)
    return best
def random_rides(r):
    n,m=r.randint(1,8),r.randint(1,8);return [[r.randint(0,30) for _ in range(n)],[r.randint(1,10) for _ in range(n)],[r.randint(0,30) for _ in range(m)],[r.randint(1,10) for _ in range(m)]]
def trionic_oracle(a):
    nums=a[0];n=len(nums)
    return any(all(nums[i]<nums[i+1] for i in range(p)) and all(nums[i]>nums[i+1] for i in range(p,q)) and all(nums[i]<nums[i+1] for i in range(q,n-1)) for p in range(1,n-2) for q in range(p+1,n-1))
def random_trionic(r):return [[r.randint(-20,20) for _ in range(r.randint(4,20))]]
def flip_oracle(a):
    grid,x,y,k=a;out=[row[:] for row in grid]
    for i in range(k//2):
        for j in range(k):out[x+i][y+j],out[x+k-1-i][y+j]=out[x+k-1-i][y+j],out[x+i][y+j]
    return out
def random_flip(r):
    rows,cols=r.randint(2,8),r.randint(2,8);k=r.randint(1,min(rows,cols));return [[[r.randint(0,50) for _ in range(cols)] for _ in range(rows)],r.randint(0,rows-k),r.randint(0,cols-k),k]

COUPON='''def valid_coupon_codes(code,businessLine,isActive):
    order=['electronics','grocery','pharmacy','restaurant'];valid=[]
    for value,line,active in zip(code,businessLine,isActive):
        if active and line in order and value and all(c.isalnum() or c=='_' for c in value):valid.append((order.index(line),value))
    return [value for _,value in sorted(valid)]
'''
DIGITDIV='''def is_divisible_by_digit_sum_and_product(n):
    digits=[int(c) for c in str(n)];product=1
    for digit in digits:product*=digit
    return n%(sum(digits)+product)==0
'''
RIDES='''def earliest_land_water_finish(landStartTime,landDuration,waterStartTime,waterDuration):
    answer=float('inf')
    for ls,ld in zip(landStartTime,landDuration):
        for ws,wd in zip(waterStartTime,waterDuration):answer=min(answer,max(ls+ld,ws)+wd,max(ws+wd,ls)+ld)
    return answer
'''
TRIONIC='''def is_trionic_array(nums):
    i=1
    while i<len(nums) and nums[i]>nums[i-1]:i+=1
    if i==1 or i==len(nums) or nums[i]>=nums[i-1]:return False
    while i<len(nums) and nums[i]<nums[i-1]:i+=1
    if i==len(nums) or nums[i]<=nums[i-1]:return False
    while i<len(nums) and nums[i]>nums[i-1]:i+=1
    return i==len(nums)
'''
FLIP='''def flip_square_submatrix_vertically(grid,x,y,k):
    answer=[row[:] for row in grid]
    for offset in range(k//2):
        top=x+offset;bottom=x+k-1-offset
        answer[top][y:y+k],answer[bottom][y:y+k]=answer[bottom][y:y+k],answer[top][y:y+k]
    return answer
'''

BATCH={
3606:entry('valid_coupon_codes',[('code','list[str]'),('businessLine','list[str]'),('isActive','list[bool]')],'list[str]',['arrays','strings','sorting'],['A valid coupon is active, has a nonempty code containing only letters, digits, or underscore, and belongs to an allowed business line.','Business-line order is electronics, grocery, pharmacy, restaurant.','Return valid codes sorted by that category order then lexicographically.'],[([['SAVE20','','PHARMA5','SAVE@20'],['restaurant','grocery','pharmacy','restaurant'],[True,True,True,True]],'The empty and @ codes are invalid; pharmacy precedes restaurant.'),([['A_1','B2'],['electronics','grocery'],[True,False]],'Only active electronics code A_1 remains.')],[[c,b,a] for c,b,a in [(['A'],['electronics'],[True]),(['A'],['electronics'],[False]),([''],['grocery'],[True]),(['@'],['grocery'],[True]),(['_'],['pharmacy'],[True]),(['B','A'],['grocery','grocery'],[True,True]),(['R','E'],['restaurant','electronics'],[True,True]),(['X'],['other'],[True]),(['1A'],['pharmacy'],[True]),(['A-B'],['electronics'],[True]),(['Z_9'],['restaurant'],[True]),(['G','P'],['grocery','pharmacy'],[True,True]),(['AA','A'],['electronics','electronics'],[True,True]),(['Q'],['restaurant'],[False])]],COUPON,[COUPON.replace("or c=='_'",''),COUPON.replace("order=['electronics','grocery','pharmacy','restaurant']","order=['restaurant','pharmacy','grocery','electronics']")],['Rejects underscore even though it is allowed.','Sorts business categories in reverse priority.'],coupon_oracle,random_coupon,['Validate aligned records independently.','Attach each accepted code to its business-line rank.','Sort tuples by rank then code.','Discard ranks from the ordered result.'],'O(n log n)','O(n)',3),
3622:entry('is_divisible_by_digit_sum_and_product',[('n','int')],'bool',['math','digits'],['Compute the sum and product of the decimal digits of positive n.','Add those two quantities.','Return whether n is divisible by that combined value.'],[([99],'Digit sum eighteen plus product eighty-one equals ninety-nine, which divides n.'),([23],'The combined value eleven does not divide twenty-three.')],[[n] for n in [1,2,9,10,11,12,23,99,101,111,123,222,1000,999]],DIGITDIV,[DIGITDIV.replace('sum(digits)+product','sum(digits)+product+1'),DIGITDIV.replace('==0','!=0')],['Adds one to the required divisor.','Returns nondivisibility.'],digit_div_oracle,random_digit_div,['Extract decimal digits.','Accumulate their sum and product.','Take n modulo the sum of those aggregates.','A zero remainder is exactly divisibility.'],'O(digits)','O(digits)',3),
3633:entry('earliest_land_water_finish',[('landStartTime','list[int]'),('landDuration','list[int]'),('waterStartTime','list[int]'),('waterDuration','list[int]')],'int',['arrays','enumeration','scheduling'],['Choose exactly one land ride and one water ride in either order.','A ride may start at its listed earliest time or later, and the second begins as soon as both it and the tourist are ready.','Return the earliest possible completion time.'],[([[2,8],[4,1],[6],[3]],'Taking the first land ride at two then water at six finishes at nine.'),([[0],[5],[1],[2]],'Water first finishes at three, then land finishes at eight.')],[[a,b,c,d] for a,b,c,d in [([0],[1],[0],[1]),([2,8],[4,1],[6],[3]),([0],[5],[1],[2]),([5],[1],[0],[10]),([1,10],[2,1],[4],[3]),([0],[10],[5],[1]),([5],[2],[1],[2]),([3,8],[5,2],[0,10],[4,1]),([1,2],[1,1],[1,2],[1,1]),([10],[5],[20],[2]),([20],[2],[10],[5]),([0,100],[50,1],[20],[5]),([4],[4],[4],[4]),([2,7],[3,2],[1,9],[2,1])]],RIDES,[RIDES.replace('max(ls+ld,ws)','ls+ld'),RIDES.replace('max(ws+wd,ls)','ws+wd')],['Starts water before its availability after land.','Starts land before its availability after water.'],rides_oracle,random_rides,['Enumerate one ride from each category.','For land first, water starts at max(land finish, water availability).','Compute the symmetric water-first completion.','The minimum across pairs and orders is globally earliest.'],'O(L*W)','O(1)',3),
3637:entry('is_trionic_array',[('nums','list[int]')],'bool',['arrays','two pointers'],['Split the complete array into three nonempty edge sequences: strictly increasing, then strictly decreasing, then strictly increasing.','The two turning indices must be internal.','Return whether such a split exists.'],[([[1,3,5,4,2,6]],'The array rises to five, falls to two, then rises to six.'),([[1,2,3,4]],'There is no nonempty decreasing middle segment.')],[[x] for x in [[1,3,5,4,2,6],[1,2,3,4],[4,3,2,1],[1,3,2,4],[1,2,1,0,1],[1,1,0,1],[3,2,3,2],[0,2,1,3,5],[-3,-1,-2,0],[1,4,3,2,5,6],[1,2,2,1,3],[5,6,4,2,3],[1,5,4,6],[2,4,1,3],[1,3,2,4,3]]],TRIONIC,[TRIONIC.replace('nums[i]>nums[i-1]','nums[i]>=nums[i-1]'),TRIONIC.replace('return i==len(nums)','return i>=len(nums)-1')],['Allows equality in increasing segments.','Accepts one trailing violation after the final rise.'],trionic_oracle,random_trionic,['Consume the maximal initial strict rise.','Require it to be nonempty and followed by a strict fall.','Consume that fall, require a final rise, then consume it.','Success requires reaching the array end after all three nonempty phases.'],'O(n)','O(1)',3),
3643:entry('flip_square_submatrix_vertically',[('grid','list[list[int]]'),('x','int'),('y','int'),('k','int')],'list[list[int]]',['matrices','simulation'],['Copy grid, then select the k by k square whose top-left corner is (x,y).','Reverse only the order of rows inside that square while preserving values within each selected row.','Return the modified grid.'],[([[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],1,0,3],'Rows of the selected lower-left 3x3 square are reversed.'),([[[1,2],[3,4]],0,0,2],'The two complete rows swap vertically.')],[[g,x,y,k] for g,x,y,k in [([[1]],0,0,1),([[1,2],[3,4]],0,0,2),([[1,2,3],[4,5,6],[7,8,9]],0,0,3),([[1,2,3],[4,5,6],[7,8,9]],1,1,2),([[1,2,3,4],[5,6,7,8]],0,1,2),([[1,2],[3,4],[5,6]],1,0,2),([[1,2,3],[4,5,6]],0,0,2),([[9,8],[7,6]],0,0,1),([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],1,0,3),([[0,1,2],[3,4,5],[6,7,8]],0,1,2),([[1,1],[2,2]],0,0,2),([[5,4,3],[2,1,0],[9,8,7]],0,0,2),([[1,2,3],[4,5,6],[7,8,9]],0,0,2),([[1,2,3,4],[5,6,7,8],[9,10,11,12]],0,2,2)]],FLIP,[FLIP.replace('bottom=x+k-1-offset','bottom=x+k-2-offset'),FLIP.replace('y:y+k','0:k')],['Pairs each top row with the row above its correct mirror.','Always flips columns starting at zero.'],flip_oracle,random_flip,['Copy the matrix so input remains unchanged.','Pair the top and bottom rows of the selected square.','Swap only their slices from y through y+k.','Half the row pairs suffice; a middle row remains fixed when k is odd.'],'O(rows*columns)','O(rows*columns)',3),
}
