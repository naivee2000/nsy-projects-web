"""Replacement candidates for two twice-failed validations in batch 200."""
from .import_batch_055 import entry

def ascii_oracle(a):
    bits=[]
    for char in a[0]:
        value=ord(char)
        bits.extend('1' if value&(1<<shift) else '0' for shift in range(7,-1,-1))
    return bits==bits[::-1]
def random_ascii(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,100)))]
def blocks_oracle(a):
    nums=a[0];answer=0
    for value in set(nums):
        positions=[i for i,x in enumerate(nums) if x==value]
        answer+=positions[-1]-positions[0]+1==len(positions)
    return answer
def random_blocks(r):return [[r.randint(1,10) for _ in range(r.randint(1,100))]]

ASCII='''def is_ascii_bit_palindrome(s):
    bits=''.join(format(ord(char),'08b') for char in s)
    return bits==bits[::-1]
'''
BLOCKS='''def count_single_block_integers(nums):
    from collections import Counter
    runs=Counter(value for i,value in enumerate(nums) if i==0 or value!=nums[i-1])
    return sum(count==1 for count in runs.values())
'''

BATCH={
4030:entry('is_ascii_bit_palindrome',[('s','str')],'bool',['strings','bit manipulation'],['1 <= len(s) <= 100; s contains lowercase English letters.','Replace each character with exactly eight ASCII bits, including its leading zero, and concatenate in order.','Return whether the resulting bit string reads the same forward and backward.'],[(['ff'],'Each f is 01100110; their concatenation is palindromic.'),(['leet'],'The concatenated eight-bit character encodings do not read the same backward.')],[[s] for s in ['a','f','ff','leet','aa','aba','z','zz','az','abc','noon','level','abcdef','ffff']],ASCII,[ASCII.replace("'08b'","'b'"),ASCII.replace('bits[::-1]','s[::-1]')],['Drops the required leading zero from each eight-bit encoding.','Checks whether the original letters form a palindrome instead of the constructed bits.'],ascii_oracle,random_ascii,['The palindrome is defined over bits, so character symmetry alone is insufficient.','Encode every ASCII value to exactly eight binary digits before concatenating.','Build bits, then compare it with its reverse.','Fixed-width encoding preserves every leading zero required by the constructed sequence.'],'O(n)','O(n)',3),
4038:entry('count_single_block_integers',[('nums','list[int]')],'int',['arrays','hash-maps'],['1 <= len(nums) <= 100; values are positive integers.','A value is special when all its occurrences form one uninterrupted contiguous block.','Return the number of distinct special values.'],[([[1,2,2,1]],'One occurs in two separated blocks, while two occurs in one block, so return one.'),([[3,3,1,2,2,1]],'Three and two each form one block; one forms two blocks, so return two.')],[[x] for x in [[1],[1,1],[1,2],[1,2,2,1],[3,3,1,2,2,1],[1,2,3],[1,2,1],[2,2,3,3],[1,1,2,1],[4,3,3,4,4],[1,2,1,2],[5,5,5,6],[7,8,8,9,7],[1,1,2,2,3,3]]],BLOCKS,[BLOCKS.replace('count==1','count>=1'),BLOCKS.replace("i==0 or value!=nums[i-1]","i==0")],['Counts every distinct value even when it appears in several runs.','Records only the first array value and misses every later run.'],blocks_oracle,random_blocks,['Compress the array conceptually into maximal runs.','Count how many runs belong to each value.','Increment a value only at index zero or when it differs from the previous value; count frequencies equal to one.','A value’s occurrences are contiguous exactly when it creates one maximal run.'],'O(n)','O(distinct values)',3),
}
