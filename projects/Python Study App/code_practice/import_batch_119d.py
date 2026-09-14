"""Final reviewed group of workbook batch 119."""
from collections import Counter
from itertools import permutations
from .import_batch_055 import entry

def title_o(a):return ' '.join(word.lower() if len(word)<=2 else word[0].upper()+word[1:].lower() for word in a[0].split(' '))
def twin_o(a):
 values=a[0];return max(values[i]+values[-1-i] for i in range(len(values)//2))
def palindrome_o(a):
 words=a[0];best=0
 for size in range(1,len(words)+1):
  for chosen in permutations(range(len(words)),size):
   if len(set(chosen))<size:continue
   text=''.join(words[i] for i in chosen)
   if text==text[::-1]:best=max(best,len(text))
 return best
def stamp_o(a):
 grid,height,width=a;rows=len(grid);cols=len(grid[0]);covered=set()
 for r in range(rows-height+1):
  for c in range(cols-width+1):
   cells={(x,y) for x in range(r,r+height) for y in range(c,c+width)}
   if all(grid[x][y]==0 for x,y in cells):covered|=cells
 return all(grid[r][c] or (r,c) in covered for r in range(rows) for c in range(cols))
def valid_o(a):
 matrix=a[0];need=set(range(1,len(matrix)+1));return all(set(row)==need for row in matrix) and all({row[c] for row in matrix}==need for c in range(len(matrix)))
def rtitle(r):return [' '.join(''.join(r.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,8)))]
def rtwin(r):return [[r.randint(0,30) for _ in range(2*r.randint(1,10))]]
def rpalindrome(r):return [[''.join((r.choice('abc'),r.choice('abc'))) for _ in range(r.randint(1,7))]]
def rstamp(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)],r.randint(1,rows),r.randint(1,cols)]
def rvalid(r):
 n=r.randint(1,6);return [[[r.randint(1,n) for _ in range(n)] for _ in range(n)]]

TITLE='''\
def capitalize_title_words(title):
    answer=[]
    for word in title.split(' '):
        lowered=word.lower();answer.append(lowered if len(word)<=2 else lowered.capitalize())
    return ' '.join(answer)
'''
TWIN='''\
def maximum_linked_twin_sum(head):
    values=[];node=head
    while node:values.append(node.val);node=node.next
    return max(values[i]+values[-1-i] for i in range(len(values)//2))
'''
PALINDROME='''\
def longest_two_letter_palindrome(words):
    from collections import Counter
    counts=Counter(words);length=0;center=False
    for word,count in list(counts.items()):
        reverse=word[::-1]
        if word==reverse:
            length+=(count//2)*4
            if count%2:center=True
        elif word<reverse:
            length+=min(count,counts[reverse])*4
    return length+(2 if center else 0)
'''
STAMP='''\
def can_stamp_grid(grid,stamp_height,stamp_width):
    rows,cols=len(grid),len(grid[0]);prefix=[[0]*(cols+1) for _ in range(rows+1)]
    for r in range(rows):
        for c in range(cols):prefix[r+1][c+1]=grid[r][c]+prefix[r][c+1]+prefix[r+1][c]-prefix[r][c]
    change=[[0]*(cols+1) for _ in range(rows+1)]
    for r in range(rows-stamp_height+1):
        for c in range(cols-stamp_width+1):
            bottom,right=r+stamp_height,c+stamp_width
            if prefix[bottom][right]-prefix[r][right]-prefix[bottom][c]+prefix[r][c]==0:
                change[r][c]+=1;change[bottom][c]-=1;change[r][right]-=1;change[bottom][right]+=1
    for r in range(rows):
        for c in range(cols):
            if r:change[r][c]+=change[r-1][c]
            if c:change[r][c]+=change[r][c-1]
            if r and c:change[r][c]-=change[r-1][c-1]
            if grid[r][c]==0 and change[r][c]==0:return False
    return True
'''
VALID='''\
def valid_latin_matrix(matrix):
    required=set(range(1,len(matrix)+1))
    return all(set(row)==required for row in matrix) and all({row[col] for row in matrix}==required for col in range(len(matrix)))
'''
def L(*x):return list(x)
BATCH={
2129:entry('capitalize_title_words',[('title','str')],'str',['strings','normalization'],['title has words separated by single spaces.','Words of length one or two become lowercase; longer words get an uppercase first letter and lowercase remainder.','Preserve word order and single separators.'],[(['capiTalIze tHe titLe'],'The three longer words become Capitalize The Title.'),(['First leTTeR of EACH Word'],'The result is First Letter of Each Word; of remains lowercase.')],[[s] for s in ['a','I','AN','the','hELLo','a b c','TO be OR not','PYTHON code','x Yz ABC','one TWO three','mIxEd CaSe','go TO Home','AA aaa','this IS fine']],TITLE,[TITLE.replace('len(word)<=2','len(word)<2'),TITLE.replace('lowered.capitalize()','lowered.upper()')],['Capitalizes two-letter words instead of lowercasing them.','Uppercases every letter in long words instead of only the first.'],title_o,rtitle,L('Normalize case before applying the length-based first-letter rule.','Split on spaces; lowercase each word; capitalize only when its length exceeds two.','Append lowered if len<=2 else lowered.capitalize(), then join with spaces.','Each word is transformed independently according to exactly one rule, while split/join preserves order and separators.'),'O(length)','O(length)',3),
2130:entry('maximum_linked_twin_sum',[('head','ListNode')],'int',['linked lists','two pointers'],['The linked list has positive even length.','Node i is paired with node n-1-i; calculate each pair once.','Return the maximum twin sum without changing node values.'],[([[5,4,2,1]],'Twin pairs sum to six and six, so the maximum is six.'),([[4,2,2,3]],'The outer nodes sum to seven, exceeding the inner sum four.')],[[x] for x in [[1,1],[1,2],[1,2,3,4],[9,1,2,8],[5,5,5,5],[1,9,8,2,3,7],[10,0],[0,0,1,1],[4,3,2,1,5,6],[7,1,4,2,8,3,9,5],[2,8,6,4],[100,1,1,100],[3,6,9,12,15,18],[1,2,3,4,5,6,7,8]]],TWIN,[TWIN.replace('values[-1-i]','values[-i]'),TWIN.replace('range(len(values)//2)','range(len(values)//2-1)')],['Pairs the first node with itself because of a negative-index off-by-one.','Skips the final twin pair and may miss the maximum.'],twin_o,rtwin,L('Twin positions are symmetric around the list endpoints.','Collect values once, then compare values[i]+values[n-1-i] over the first half.','Return max(values[i]+values[-1-i] for i in range(n//2)).','Every node belongs to exactly one symmetric pair, and first-half indices enumerate all pairs without duplication.'),'O(n)','O(n)',5),
2131:entry('longest_two_letter_palindrome',[('words','list[str]')],'int',['strings','hash maps','greedy'],['Every word contains exactly two lowercase letters and each occurrence may be used once.','Arrange selected words in any order so the concatenation is a palindrome.','Return the maximum possible character length.'],[([['lc','cl','gg']],'lc and cl form mirrored ends while gg occupies the center, totaling six.'),([['ab','ty','yt','lc','cl','ab']],'The reverse pairs ty/yt and lc/cl contribute eight characters; unmatched ab words cannot be used.')],[[w] for w in [['aa'],['ab'],['ab','ba'],['aa','aa'],['aa','aa','aa'],['ab','ba','cc'],['ab','ab','ba'],['ab','ba','ab','ba'],['aa','bb','cc'],['lc','cl','gg'],['xy','yx','zz','zz','zz'],['ab','cd','ef'],['aa','ab','ba','aa'],['az','za','by','yb','cc']]],PALINDROME,[PALINDROME.replace('word<reverse','word<=reverse'),PALINDROME.replace('if count%2:center=True','if count%2:center=False')],['Double-counts symmetric words by processing both orientations.','Never reserves an unmatched symmetric word for the center.'],palindrome_o,rpalindrome,L('Nonsymmetric words must pair with their reverse; symmetric words pair among themselves with at most one leftover center.','Count words, process one lexical orientation of each reverse pair, and track whether any symmetric odd count exists.','Add 4 per reverse pair or symmetric pair, then add 2 once for a center if available.','Mirrored blocks are necessary outside the center, and these independent maximum pairings can always be concatenated into a palindrome.'),'O(words)','O(distinct words)',5),
2132:entry('can_stamp_grid',[('grid','list[list[int]]'),('stamp_height','int'),('stamp_width','int')],'bool',['matrices','prefix sums','difference arrays'],['grid is a nonempty binary matrix; stamps cannot rotate or cover occupied cells.','Stamps may overlap and must stay within the grid.','Return whether every zero cell can be covered by at least one valid stamp.'],[([[[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],4,3],'Two overlapping 4-by-3 stamps cover every zero without touching the occupied first column.'),([[[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],4,4],'Every 4-by-4 placement touches an occupied cell, so the zeros cannot all be covered.')],[[g,h,w] for g,h,w in [([[0]],1,1),([[1]],1,1),([[0,0]],1,2),([[0,0]],1,1),([[0],[0]],2,1),([[0,1]],1,1),([[0,1]],1,2),([[0,0],[0,0]],2,2),([[0,0],[0,1]],2,2),([[0,0,0],[0,1,0],[0,0,0]],1,2),([[0,0,0],[0,0,0]],2,2),([[1,0,1],[0,0,0]],2,1),([[0,0,0],[0,0,0],[0,0,0]],2,2),([[1,0,0],[1,0,0],[1,0,0]],2,2)]],STAMP,[STAMP.replace('==0:', '>0:'),STAMP.replace('change[r][c]==0','change[r][c]<=1')],['Places stamps only where occupied cells exist.','Requires every zero to be covered at least twice instead of once.'],stamp_o,rstamp,L('Use a rectangle-sum table to identify valid empty placements, then a 2D difference array to combine their coverage.','For every top-left position, query whether its stamp rectangle sum is zero and range-add that rectangle.','Prefix the difference grid; reject any original zero whose resulting coverage is zero.','Every added rectangle is legal, overlaps are allowed, and the final coverage test is exactly the requirement for each empty cell.'),'O(rows*cols)','O(rows*cols)',8),
2133:entry('valid_latin_matrix',[('matrix','list[list[int]]')],'bool',['matrices','sets'],['matrix is n by n with values intended from one through n.','Every row and every column must contain each number from one through n exactly once.','Return whether the matrix is valid.'],[([[[1,2,3],[3,1,2],[2,3,1]]],'Every row and column contains one, two, and three exactly once.'),([[[1,1,1],[1,2,3],[1,2,3]]],'The first row repeats one and the columns are also incomplete.')],[[m] for m in [[[1]],[[1,2],[2,1]],[[1,2],[1,2]],[[1,1],[2,2]],[[2,1],[1,2]],[[1,2,3],[2,3,1],[3,1,2]],[[1,2,3],[3,2,1],[2,1,3]],[[1,2,4],[2,3,1],[3,1,2]],[[1,2],[2,2]],[[2]],[[1,2,3,4],[2,3,4,1],[3,4,1,2],[4,1,2,3]],[[1,2,3],[2,1,3],[3,3,1]],[[3,1,2],[2,3,1],[1,2,3]],[[1,2,3],[3,1,2],[2,1,3]]]],VALID,[VALID.replace('and all({row[col]','or all({row[col]'),VALID.replace('range(1,len(matrix)+1)','range(len(matrix))')],['Accepts a matrix when either rows or columns alone are valid.','Requires zero through n-1 instead of one through n.'],valid_o,rvalid,L('Every valid row and column has exactly the required set {1,...,n}.','Build the required set and compare it against each row set and each column set.','Return all(set(row)==required) and all({matrix[r][c]}==required).','With n positions and permitted values, set equality enforces both presence and uniqueness in every line.'),'O(n^2)','O(n)',3)
}
BATCH[2130]['params'][0]=('head','ListNode','listnode')
BATCH[2131]['wrong'][0]=PALINDROME.replace('elif word<reverse:','elif word!=reverse:')
BATCH[2131]['wrong_reasons'][0]='Processes both orientations of every reverse pair and double-counts the same word occurrences.'
