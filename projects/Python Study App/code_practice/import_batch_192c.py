"""Stone game, positive-window, set-bit, equalization, and circular-transform exercises."""
from .import_batch_055 import entry

def stone_oracle(a):
    n=a[0];take=10;alice=True
    while take>0 and n>=take:n-=take;take-=1;alice=not alice
    return not alice
def random_stone(r):return [r.randint(1,50)]
def positive_oracle(a):
    nums,l,r=a;values=[sum(nums[i:i+k]) for k in range(l,r+1) for i in range(len(nums)-k+1) if sum(nums[i:i+k])>0]
    return min(values,default=-1)
def random_positive(r):
    n=r.randint(1,20);l=r.randint(1,n);return [[r.randint(-10,10) for _ in range(n)],l,r.randint(l,n)]
def bits_oracle(a):
    x=a[0]
    while x&(x+1):x+=1
    return x
def random_bits(r):return [r.randint(1,1000)]
def equal_oracle(a):
    nums,k=a
    if any(v<k for v in nums):return -1
    return len({v for v in nums if v>k})
def random_equal(r):return [[r.randint(1,20) for _ in range(r.randint(1,30))],r.randint(1,20)]
def transform_oracle(a):
    nums=a[0];n=len(nums);return [nums[(i+nums[i])%n] for i in range(n)]
def random_transform(r):return [[r.randint(-30,30) for _ in range(r.randint(1,30))]]

STONE='''def does_alice_win_stone_removal(n):
    take=10
    alice=True
    while take>0 and n>=take:
        n-=take
        take-=1
        alice=not alice
    return not alice
'''
POSITIVE='''def minimum_positive_bounded_subarray_sum(nums,l,r):
    answer=None
    for length in range(l,r+1):
        total=sum(nums[:length])
        if total>0:answer=total if answer is None else min(answer,total)
        for right in range(length,len(nums)):
            total+=nums[right]-nums[right-length]
            if total>0:answer=total if answer is None else min(answer,total)
    return -1 if answer is None else answer
'''
BITS='''def smallest_all_set_bits_number(n):
    return (1<<n.bit_length())-1
'''
EQUAL='''def minimum_operations_to_equal_k(nums,k):
    if min(nums)<k:return -1
    return len({value for value in nums if value>k})
'''
TRANSFORM='''def circular_transformed_array(nums):
    n=len(nums)
    return [nums[(i+move)%n] for i,move in enumerate(nums)]
'''

BATCH={
3360:entry('does_alice_win_stone_removal',[('n','int')],'bool',['math','simulation','games'],['Alice and Bob alternate, with Alice first.','The required removal begins at ten stones and decreases by one after every successful turn.','A player unable to remove the required amount loses; return whether Alice wins.'],[([12],'Alice removes ten, leaving two; Bob cannot remove nine, so Alice wins.'),([1],'Alice cannot make the first ten-stone move and loses.')],[[n] for n in [2,9,10,11,18,19,20,27,28,35,36,40,45,49]],STONE,[STONE.replace('return not alice','return alice'),STONE.replace('take-=1','take+=1')],['Returns whether it is Alice’s losing turn instead of whether Alice won.','Increases the required removal after each turn.'],stone_oracle,random_stone,['Simulate the forced sequence 10,9,8,... .','Track whose turn follows every successful removal.','Stop when the current player lacks enough stones or the required amount reaches zero.','The player who made the last successful move is the winner.'],'O(1)','O(1)',3),
3364:entry('minimum_positive_bounded_subarray_sum',[('nums','list[int]'),('l','int'),('r','int')],'int',['arrays','sliding windows','prefix sums'],['Consider every contiguous subarray whose length is between l and r inclusive.','Among those with strictly positive sum, return the smallest sum.','Return -1 when no eligible subarray has positive sum.'],[([[3,-2,1,4],2,3],'The length-two subarray [3,-2] has positive sum one, the minimum possible.'),([[-2,2,-3,1],2,2],'Every length-two sum is nonpositive, so return -1.')],[[n,l,r] for n,l,r in [([1],1,1),([-1],1,1),([1,2],1,2),([-1,2],1,2),([3,-2,1,4],2,3),([-2,2,-3,1],2,2),([5,-4,2],2,3),([0,1,0],1,2),([-5,-1,-2],1,3),([2,-1,2,-1],3,4),([10,-9,-9,10],2,3),([4,-3,-2,5],1,4),([1,1,1],2,2),([-1,0,1],1,3)]],POSITIVE,[POSITIVE.replace('total>0','total>=0'),POSITIVE.replace('range(l,r+1)','range(l,r)')],['Treats zero sums as positive.','Omits subarrays of the maximum allowed length r.'],positive_oracle,random_positive,['Evaluate each allowed window length.','Maintain its sum while sliding one position at a time.','Update the answer only for strictly positive totals.','All eligible subarrays are visited once; -1 represents the absence of a positive candidate.'],'O(n*(r-l+1))','O(1)',3),
3370:entry('smallest_all_set_bits_number',[('n','int')],'int',['bit manipulation','math'],['Find the smallest integer at least n whose binary representation contains only one bits.','The answer must have no zero between its most significant and least significant bits.','Return that integer.'],[([5],'Five is binary 101; the next all-one-bit value is binary 111, or seven.'),([7],'Seven is already binary 111, so it is returned unchanged.')],[[n] for n in [1,2,3,4,6,8,9,15,16,17,31,32,100,999]],BITS,[BITS.replace('n.bit_length()','n.bit_length()+1'),BITS.replace('-1','-2')],['Always chooses an unnecessarily wider all-one-bit value.','Returns a number missing one from the required mask.'],bits_oracle,random_bits,['An all-one-bit number with b bits equals 2^b-1.','Use n’s bit length to select the smallest possible width.','The mask (1<<b)-1 is at least n and has all b bits set.','Any shorter all-one mask is below n, proving minimality.'],'O(1)','O(1)',3),
3375:entry('minimum_operations_to_equal_k',[('nums','list[int]'),('k','int')],'int',['arrays','sets','greedy'],['An operation chooses a valid threshold and replaces every array value above it by that threshold.','A threshold is valid when every value strictly above it is equal.','Return the minimum operations to make all values k, or -1 if impossible.'],[([[5,2,5,4,5],2],'The distinct levels above two are five and four, requiring two operations.'),([[2,1,2],2],'A value below k can never be increased, so the target is impossible.')],[[n,k] for n,k in [([1],1),([2],1),([1],2),([5,2,5,4,5],2),([2,1,2],2),([3,3,3],3),([4,4,2,2],2),([10,9,8],7),([7,7,7],5),([5,1,5],1),([6,5,4,3],4),([2,2,1],1),([100,50,100],50),([3,2,1],1)]],EQUAL,[EQUAL.replace('min(nums)<k','min(nums)<=k'),EQUAL.replace('if value>k','if value>=k')],['Incorrectly rejects arrays that already contain the target k.','Counts k itself as an operation level.'],equal_oracle,random_equal,['Values can only decrease, so any value below k makes the goal impossible.','Otherwise each distinct value above k must be removed as a level.','One valid operation eliminates exactly the current greatest remaining level.','Thus the number of distinct levels above k is both achievable and necessary.'],'O(n)','O(n)',3),
3379:entry('circular_transformed_array',[('nums','list[int]')],'list[int]',['arrays','modular arithmetic','simulation'],['For each index i, move nums[i] steps around the circular array: right for positive and left for negative.','Set result[i] to the value at the reached index.','All destinations are calculated from the unchanged input array.'],[([[3,-2,1,1]],'The circular destinations yield values [1,1,1,3].'),([[-1,4,-1]],'The destinations wrap to indices two, two, and one, producing [-1,-1,4].')],[[x] for x in [[0],[1,0],[-1,0],[1,1],[2,0,0],[3,-2,1,1],[-1,4,-1],[5,1,2],[0,0,0],[10,-10,3,4],[1,2,3,4],[-4,-3,-2,-1],[7],[2,-1,0,1,2]]],TRANSFORM,[TRANSFORM.replace('(i+move)%n','move%n'),TRANSFORM.replace('i+move','i-move')],['Uses each movement as an absolute index rather than an offset from i.','Reverses left and right movement.'],transform_oracle,random_transform,['For position i, its destination is i+nums[i].','Modulo n handles repeated laps and negative movement.','Read every result value from the original nums.','Independent destination calculation preserves the simultaneous transformation contract.'],'O(n)','O(n)',3),
}
