"""First slice of workbook batch 128."""

from itertools import product

from .import_batch_055 import entry


MOD = 1_000_000_007


def xor_oracle(args):
    (nums,) = args
    choices = [[value for value in range(number + 1) if value & ~number == 0] for number in nums]
    best = 0
    for values in product(*choices):
        result = 0
        for value in values: result ^= value
        best = max(best, result)
    return best


def random_xor(rng):
    return [[rng.randint(0, 31) for _ in range(rng.randint(1, 5))]]


def x_matrix_oracle(args):
    (grid,) = args; n = len(grid)
    for row in range(n):
        for column in range(n):
            diagonal = row == column or row + column == n - 1
            if diagonal != (grid[row][column] != 0): return False
    return True


def random_x_matrix(rng):
    n = rng.randint(1, 7)
    return [[[rng.randint(0, 3) for _ in range(n)] for _ in range(n)]]


def houses_oracle(args):
    (n,) = args
    valid = sum(all(not (bits[index] == bits[index + 1] == 1) for index in range(n - 1))
                for bits in product((0, 1), repeat=n))
    return valid * valid % MOD


def random_houses(rng):
    return [rng.randint(1, 14)]


def splice_oracle(args):
    first, second = args; best = max(sum(first), sum(second)); n = len(first)
    for left in range(n):
        for right in range(left + 1, n + 1):
            changed_first = first[:left] + second[left:right] + first[right:]
            changed_second = second[:left] + first[left:right] + second[right:]
            best = max(best, sum(changed_first), sum(changed_second))
    return best


def random_splice(rng):
    n = rng.randint(1, 10)
    return [[rng.randint(1, 30) for _ in range(n)], [rng.randint(1, 30) for _ in range(n)]]


def decode_oracle(args):
    key, message = args; mapping = {}; next_code = ord('a')
    for char in key:
        if char != ' ' and char not in mapping:
            mapping[char] = chr(next_code); next_code += 1
    return ''.join(' ' if char == ' ' else mapping[char] for char in message)


def random_decode(rng):
    letters = list('abcdefghijklmnopqrstuvwxyz'); rng.shuffle(letters)
    key = ''.join(letters)
    message = ''.join(rng.choice(letters + [' ', ' ']) for _ in range(rng.randint(1, 30)))
    return [key, message]


XOR = '''\
def maximum_xor_after_operations(nums):
    answer=0
    for number in nums:answer|=number
    return answer
'''

XMATRIX = '''\
def is_x_matrix(grid):
    n=len(grid)
    return all((grid[row][column]!=0) if row==column or row+column==n-1 else grid[row][column]==0 for row in range(n) for column in range(n))
'''

HOUSES = '''\
def count_house_placements(n):
    empty=1;occupied=0
    for _ in range(n):empty,occupied=(empty+occupied)%1000000007,empty
    return (empty+occupied)**2%1000000007
'''

SPLICE = '''\
def maximum_spliced_array_score(nums1,nums2):
    def gain(source,target):
        best=current=0
        for old,new in zip(source,target):current=max(0,current+new-old);best=max(best,current)
        return sum(source)+best
    return max(gain(nums1,nums2),gain(nums2,nums1))
'''

DECODE = '''\
def decode_substitution_message(key,message):
    mapping={};next_letter=ord('a')
    for char in key:
        if char!=' ' and char not in mapping:mapping[char]=chr(next_letter);next_letter+=1
    return ''.join(' ' if char==' ' else mapping[char] for char in message)
'''


BATCH = {
2317: entry('maximum_xor_after_operations',[('nums','list[int]')],'int',['arrays','bit manipulation'],['An operation may clear any chosen set bits of an array value but cannot create a bit absent from that value.','Apply any number of operations, then maximize the XOR of all values.','Array values are nonnegative integers.'],[([[3,2,4,6]],'The union of all set-bit positions is binary 111, so the maximum is seven.'),([[1,2,3,9,2]],'Across the values, bits for one, two, and eight are available, producing eleven.')],[[a] for a in [[0],[1],[1,1],[1,2],[7,7],[8,4,2,1],[0,0,5],[3,5],[16,1,2],[6,10,12],[31,0],[2,2,4],[9,6,3],[15,16]]],XOR,[XOR.replace('answer|=number','answer^=number'),XOR.replace('answer=0','answer=nums[0]')],['Computes the current XOR without using operations to clear conflicting bits.','Starts from the first value and then ORs it again, which is harmless here; this version is replaced below with a different initialization error.'],xor_oracle,random_xor,['Consider each bit independently.','If any input contains a bit, operations can retain it in exactly one value and clear it from the others.','OR all values to collect precisely the achievable set bits.','Every OR bit can be made odd in the final XOR, while no absent bit can be created, so OR is the maximum.'],'O(n)','O(1)',5),
2319: entry('is_x_matrix',[('grid','list[list[int]]')],'bool',['matrices','simulation'],['The grid is square.','Both main diagonals must contain only nonzero values.','Every cell outside those diagonals must equal zero.'],[([[[2,0,0,1],[0,3,1,0],[0,5,2,0],[4,0,0,2]]],'Every diagonal entry is nonzero and all other entries are zero.'),([[[5,7],[9,0]]],'In a two-by-two grid every cell is diagonal, but the bottom-right cell is zero.')],[[g] for g in [[[1]],[[0]],[[1,2],[3,4]],[[1,0],[0,1]],[[1,0,2],[0,3,0],[4,0,5]],[[1,1,1],[1,1,1],[1,1,1]],[[2,0,0,3],[0,4,5,0],[0,6,7,0],[8,0,0,9]],[[1,0,1],[0,0,0],[1,0,1]],[[9,0,0,9],[0,8,8,0],[0,7,7,0],[6,0,0,6]],[[1,0,0],[0,1,0],[0,0,1]],[[2,0,2],[0,4,0],[2,0,2]],[[3,0],[0,4]],[[3,4],[5,6]],[[1,0,0,1],[0,1,1,0],[0,1,1,0],[1,0,2,1]]]],XMATRIX,[XMATRIX.replace('row+column==n-1','row+column==n'),XMATRIX.replace('grid[row][column]==0','grid[row][column]!=0')],['Uses an off-by-one index for the secondary diagonal.','Requires off-diagonal cells to be nonzero as well.'],x_matrix_oracle,random_x_matrix,['A cell lies on the main diagonal when row equals column.','It lies on the other diagonal when row+column equals n-1.','Require nonzero on either diagonal and zero everywhere else.','These predicates partition all cells, so checking each cell proves both X-matrix conditions.'],'O(n^2)','O(1)',3),
2320: entry('count_house_placements',[('n','int')],'int',['dynamic programming','combinatorics'],['There are n plots on each of two independent street sides.','No two houses on the same side may occupy adjacent plots.','Return the total layouts modulo 1,000,000,007.'],[([1],'Each side may be empty or occupied, giving four paired layouts.'),([2],'One side has three valid patterns, so two sides have nine paired layouts.')],[[n] for n in [3,4,5,6,7,8,9,10,11,12,13,14,15,20]],HOUSES,[HOUSES.replace('**2','*2'),HOUSES.replace('empty=occupied=1','empty=1;occupied=0')],['Doubles the one-side count instead of choosing an independent layout for each side.','Initializes the empty zero-length layout incorrectly, shifting the recurrence.'],houses_oracle,random_houses,['First count valid layouts for one side.','Track counts ending with an empty plot and with an occupied plot.','The next empty plot follows either state; the next occupied plot follows only empty. Square the final one-side total.','The two street sides are independent, so the product of their identical counts includes every paired layout exactly once.'],'O(n)','O(1)',5),
2321: entry('maximum_spliced_array_score',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','dynamic programming','maximum subarray'],['The arrays have equal length.','Choose one contiguous interval and swap that interval between the arrays; choosing no beneficial swap is allowed.','Return the largest possible sum of either array after the swap.'],[([[60,60,60],[10,90,10]],'Swapping the middle element into the first array produces a sum of two hundred ten.'),([[20,40,20,70,30],[50,20,50,40,20]],'The best exchanged interval raises one array sum to two hundred twenty.')],[[a,b] for a,b in [([1],[2]),([5],[5]),([1,2],[3,4]),([10,1],[1,10]),([1,1,10],[5,5,1]),([9,8,7],[1,2,3]),([1,2,3],[9,8,7]),([4,4,4],[4,4,4]),([1,100,1,1],[50,1,50,50]),([5,1,5,1],[1,5,1,5]),([3,8,2],[7,1,9]),([10,20,30,40],[40,30,20,10]),([2,9,1,8,2],[7,1,7,1,7]),([100,1],[1,100])]],SPLICE,[SPLICE.replace('return max(gain(nums1,nums2),gain(nums2,nums1))','return gain(nums1,nums2)'),SPLICE.replace('current=max(0,current+new-old)','current=max(0,new-old)')],['Considers improving only the first array and misses swaps that best improve the second.','Keeps only a single-position gain instead of a contiguous interval gain.'],splice_oracle,random_splice,['View swapping an interval into nums1 as adding the interval sum of nums2[i]-nums1[i].','Use Kadane’s algorithm to find the maximum nonnegative interval gain.','Compute the gain in both directions and add it to the corresponding original sum.','Every legal swap corresponds to one difference-array interval, so the best of both directional maximum subarrays is exact.'],'O(n)','O(1)',8),
2325: entry('decode_substitution_message',[('key','str'),('message','str')],'str',['strings','hash maps'],['Ignoring spaces, the key contains every lowercase English letter at least once.','The first distinct key letter maps to a, the second to b, and so on.','Spaces in the message remain spaces.'],[(['the quick brown fox jumps over the lazy dog','vkbs bs t suepuv'],'Reading first key occurrences builds the substitution that decodes the message to this is a secret.'),(['eljuxhpwnyrdgtqkviszcfmabo','zwx hnfx lqantp mnoeius ycgk vcnjrdb'],'Applying the first-occurrence alphabet mapping decodes the pangram.')],[[k,m] for k,m in [('abcdefghijklmnopqrstuvwxyz','abc'),('zyxwvutsrqponmlkjihgfedcba','zyx'),('abcdefghijklmnopqrstuvwxyz','a b c'),('qwertyuiopasdfghjklzxcvbnm','qaz'),('thequickbrownfoxjumpsoverthelazydog','dog'),('bcdefghijklmnopqrstuvwxyza','abc'),('mnbvcxzlkjhgfdsapoiuytrewq','hello'),('abcdefghijklmnopqrstuvwxyz','z'),('zyxwvutsrqponmlkjihgfedcba','a'),('abcdefghijklmnopqrstuvwxyz','many words'),('phqgiumeaylnofdxjkrcvstzwb','this is text'),('qazwsxedcrfvtgbyhnujmikolp','code'),('abcdefghijklmnopqrstuvwxyzaaa','aaa'),('the quick brown fox jumps over the lazy dog','the dog')]],DECODE,[DECODE.replace("char not in mapping","char in mapping"),DECODE.replace("' ' if char==' ' else mapping[char]","mapping.get(char,char)")],['Never records a letter on its first occurrence, leaving the map empty.','Leaves encoded letters unchanged instead of translating them.'],decode_oracle,random_decode,['Scan the key from left to right while skipping spaces and repeats.','Assign successive unseen key letters to a, b, c, and so on.','Translate every message letter through that map and copy spaces.','First-occurrence order defines the unique substitution, so direct lookup decodes every character.'],'O(len(key)+len(message))','O(1)',3),
}

# A second ordinary wrong algorithm for 2317: it clears the least-significant
# available bit, incorrectly assuming every operation must change a number.
BATCH[2317]['wrong'][1] = '''\
def maximum_xor_after_operations(nums):
    answer=0
    for number in nums:answer|=number
    return answer & (answer-1)
'''
BATCH[2317]['wrong_reasons'][1] = 'Clears one achievable bit even though operations are optional.'
BATCH[2320]['wrong'][1] = '''\
def count_house_placements(n):
    empty=occupied=1
    for _ in range(n):empty,occupied=(empty+occupied)%1000000007,empty
    return (empty+occupied)**2%1000000007
'''
BATCH[2320]['wrong_reasons'][1] = 'Starts with an occupied zero-length street, shifting the recurrence by one plot.'
BATCH[2325]['wrong'] = ['''\
def decode_substitution_message(key,message):
    mapping={};next_letter=ord('a')
    for char in key:
        if char!=' ':mapping[char]=chr(next_letter);next_letter+=1
    return ''.join(' ' if char==' ' else mapping[char] for char in message)
''','''\
def decode_substitution_message(key,message):
    mapping={char:char for char in set(key) if char!=' '}
    return ''.join(' ' if char==' ' else mapping[char] for char in message)
''']
BATCH[2325]['wrong_reasons'] = ['Reassigns repeated key letters and advances the alphabet for duplicates.','Treats the encoded alphabet as the ordinary alphabet and leaves letters unchanged.']
