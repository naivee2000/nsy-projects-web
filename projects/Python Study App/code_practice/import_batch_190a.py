"""Array offset, word validation, grid conditions, permutation distance, and parity alternation."""
from .import_batch_055 import entry

def offset_oracle(a):return min(a[1])-min(a[0])
def random_offset(r):
    one=[r.randint(-100,100) for _ in range(r.randint(1,30))];delta=r.randint(-50,50);two=[x+delta for x in one];r.shuffle(two);return [one,two]
def valid_oracle(a):
    word=a[0]
    return len(word)>=3 and word.isalnum() and any(c.lower() in 'aeiou' for c in word) and any(c.isalpha() and c.lower() not in 'aeiou' for c in word)
def random_valid(r):return [''.join(r.choice('abcdeiouXYZ0123$#') for _ in range(r.randint(1,15)))]
def grid_oracle(a):
    grid=a[0];rows=len(grid);cols=len(grid[0])
    return all(grid[i][j]==grid[i+1][j] for i in range(rows-1) for j in range(cols)) and all(grid[i][j]!=grid[i][j+1] for i in range(rows) for j in range(cols-1))
def random_grid(r):
    rows,cols=r.randint(1,8),r.randint(1,8);return [[[r.randint(0,4) for _ in range(cols)] for _ in range(rows)]]
def permutation_oracle(a):
    s,t=a;return sum(abs(i-t.index(char)) for i,char in enumerate(s))
def random_permutation(r):
    chars=list('abcdefghijklmnopqrstuvwxyz');r.shuffle(chars);s=''.join(chars[:r.randint(1,20)]);t=list(s);r.shuffle(t);return [s,''.join(t)]
def special_oracle(a):return all((x+y)%2==1 for x,y in zip(a[0],a[0][1:]))
def random_special(r):return [[r.randint(1,100) for _ in range(r.randint(1,40))]]

OFFSET='''\
def added_integer_between_arrays(nums1,nums2):
    return min(nums2)-min(nums1)
'''
VALID='''\
def is_valid_alphanumeric_word(word):
    if len(word)<3 or not word.isalnum():return False
    vowel=any(char.lower() in 'aeiou' for char in word)
    consonant=any(char.isalpha() and char.lower() not in 'aeiou' for char in word)
    return vowel and consonant
'''
GRID='''\
def grid_meets_column_row_conditions(grid):
    rows=len(grid);columns=len(grid[0])
    for row in range(rows):
        for column in range(columns):
            if row+1<rows and grid[row][column]!=grid[row+1][column]:return False
            if column+1<columns and grid[row][column]==grid[row][column+1]:return False
    return True
'''
PERMUTATION='''\
def permutation_position_difference(s,t):
    positions={char:i for i,char in enumerate(t)}
    return sum(abs(i-positions[char]) for i,char in enumerate(s))
'''
SPECIAL='''\
def is_alternating_parity_array(nums):
    return all((a-b)%2 for a,b in zip(nums,nums[1:]))
'''

BATCH={
3131:entry('added_integer_between_arrays',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','math'],['nums2 is a permutation of nums1 after the same integer x is added to every nums1 value.','The arrays are nonempty and have equal length.','Return x.'],[([[2,6,4],[9,7,5]],'Adding three gives [5,9,7], a permutation of nums2.'),([[10],[5]],'The single value was changed by negative five.')],[[a,b] for a,b in [([1],[1]),([10],[5]),([2,6,4],[9,7,5]),([1,2],[3,4]),([-3,0],[2,5]),([5,5],[8,8]),([9,1,4],[0,-8,-5]),([100,0],[150,50]),([-10,-20],[-7,-17]),([1,3,2],[1,3,2]),([7,8,9],[6,5,4]),([0,0,1],[10,10,11]),([4,2,6,8],[9,7,11,13]),([50,-50],[0,-100])]],OFFSET,[OFFSET.replace('min(nums2)-min(nums1)','max(nums2)-min(nums1)'),OFFSET.replace('-min(nums1)','+min(nums1)')],['Uses the maximum of nums2 rather than corresponding extrema.','Adds the minima instead of subtracting them.'],offset_oracle,random_offset,['Adding a constant preserves relative order and shifts every order statistic equally.','In particular, min(nums2)=min(nums1)+x.','Subtract the two minima to recover x.','The promised common shift makes this necessary equation sufficient for the unique answer.'],'O(n)','O(1)',3),
3136:entry('is_valid_alphanumeric_word',[('word','str')],'bool',['strings','character classes'],['A valid word has at least three characters and contains only letters or digits.','It must contain at least one vowel letter and at least one consonant letter, ignoring case.','Digits satisfy neither the vowel nor consonant requirement.'],[(['234Adas'],'The word is alphanumeric and contains vowel A and consonants d,s.'),(['b3'],'It has a consonant but is shorter than three and has no vowel.')],[[s] for s in ['abc','aei','bcd','123','a1b','ab$','234Adas','b3','A0z','___','e2e','Z9a','a-b','IOUq','xy1']],VALID,[VALID.replace('len(word)<3','len(word)<2'),VALID.replace("char.isalpha() and char.lower() not in 'aeiou'","char.lower() not in 'aeiou'")],['Accepts two-character words.','Treats digits as consonants.'],valid_oracle,random_valid,['Reject invalid length or nonalphanumeric characters first.','Scan characters for a vowel and separately for an alphabetic nonvowel.','Return true only when both flags exist.','The checks correspond exactly to the independent validity requirements.'],'O(n)','O(1)',3),
3142:entry('grid_meets_column_row_conditions',[('grid','list[list[int]]')],'bool',['matrices','local comparisons'],['Every vertically adjacent pair in a column must be equal.','Every horizontally adjacent pair in a row must be different.','Return whether the entire rectangular grid satisfies both rules.'],[([[[1,0,2],[1,0,2]]],'Columns are constant and every horizontal neighbor differs.'),([[[1,1,1],[0,0,0]]],'Horizontal neighbors match and columns differ, violating both rules.')],[[g] for g in [[[1]],[[1,2]],[[1],[1]],[[1],[2]],[[1,0,2],[1,0,2]],[[1,1,1],[0,0,0]],[[1,2],[1,2]],[[1,2],[1,3]],[[0,1,0]],[[5],[5],[5]],[[2,3,4],[2,3,4],[2,3,4]],[[1,2,1],[1,2,1]],[[0,0]],[[7,8],[7,8],[7,9]]]],GRID,[GRID.replace('!=grid[row+1][column]','==grid[row+1][column]'),GRID.replace('==grid[row][column+1]','!=grid[row][column+1]')],['Rejects equal vertical neighbors instead of requiring them.','Rejects different horizontal neighbors instead of requiring them.'],grid_oracle,random_grid,['Each rule concerns only immediate neighbors.','Scan every cell and compare downward and rightward when those neighbors exist.','Return false on the first violated equality or inequality.','Every adjacency is checked once, so passing all checks is equivalent to satisfying the grid conditions.'],'O(rows*columns)','O(1)',3),
3146:entry('permutation_position_difference',[('s','str'),('t','str')],'int',['strings','hash maps'],['s and t are permutations of the same distinct lowercase characters.','For each character, take the absolute difference between its index in s and its index in t.','Return the sum of those differences.'],[(['abc','bac'],'a and b each move one position while c stays, totaling two.'),(['abcde','edbac'],'The five absolute position changes sum to twelve.')],[[a,b] for a,b in [('a','a'),('ab','ab'),('ab','ba'),('abc','bac'),('abc','cba'),('abcd','badc'),('abcde','edbac'),('xyz','zxy'),('qwer','rewq'),('mnop','ponm'),('abcdef','fabcde'),('ace','cea'),('code','deco'),('rstuv','trvus')]],PERMUTATION,[PERMUTATION.replace('abs(i-positions[char])','i-positions[char]'),PERMUTATION.replace('enumerate(t)','enumerate(s)')],['Uses signed changes that can cancel.','Builds positions from s, making every contribution zero.'],permutation_oracle,random_permutation,['Map every t character to its index for constant-time lookup.','Enumerate s and find the same character’s mapped position.','Add their absolute index difference.','Distinct characters guarantee one mapped position each, and the sum directly follows the definition.'],'O(n)','O(n)',3),
3151:entry('is_alternating_parity_array',[('nums','list[int]')],'bool',['arrays','parity'],['An array is special when every adjacent pair contains one even and one odd value.','A one-element array is special because it has no adjacent violation.','Return whether nums is special.'],[([[1]],'There are no adjacent pairs, so the result is true.'),([[2,1,4]],'Even, odd, even alternates throughout.')],[[x] for x in [[1],[2],[1,2],[2,1],[1,3],[2,4],[2,1,4],[1,2,3,4],[4,3,2,1],[1,1,2],[2,3,5],[10,9,8,7],[7,4,3],[6,1,2,5,8]]],SPECIAL,[SPECIAL.replace('(a-b)%2','(a-b)%2==0'),SPECIAL.replace('all(','any(')],['Requires equal parity instead of alternating parity.','Accepts when only one adjacent pair alternates.'],special_oracle,random_special,['Two integers have opposite parity exactly when their difference is odd.','Inspect every adjacent pair.','Require the difference modulo two to be nonzero for all pairs.','Universal adjacency checking implements the definition, with the empty set of pairs correctly passing.'],'O(n)','O(1)',3),
}
BATCH[3136]['boundaries'].append(['ab'])
