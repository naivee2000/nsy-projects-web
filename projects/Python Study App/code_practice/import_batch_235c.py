"""One replacement, fast majority counts, equal triples, budget paths, and expanded text."""
from itertools import combinations
from .import_batch_055 import entry


def nondescending_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            for changed in range(left-1,right+1):
                valid=True
                for index in range(left+1,right+1):
                    if index in (changed,changed+1):continue
                    if nums[index-1]>nums[index]:valid=False;break
                if not valid:continue
                before=nums[changed-1] if changed>left else None;after=nums[changed+1] if left<=changed<right else None
                if changed<left or before is None or after is None or before<=after:
                    answer=max(answer,right-left+1);break
    return answer

def random_nondescending(rng):return [[rng.randint(-10,10) for _ in range(rng.randint(1,14))]]

def majority_oracle(args):
    nums,target=args;answer=0
    for left in range(len(nums)):
        count=0
        for right in range(left,len(nums)):
            count+=nums[right]==target;answer+=count*2>right-left+1
    return answer

def random_majority(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,16))],rng.randint(1,7)]

def triple_oracle(args):
    nums=args[0];answer=None
    for i,j,k in combinations(range(len(nums)),3):
        if nums[i]==nums[j]==nums[k]:
            distance=abs(i-j)+abs(j-k)+abs(k-i);answer=distance if answer is None else min(answer,distance)
    return -1 if answer is None else answer

def random_triple(rng):return [[rng.randint(1,8) for _ in range(rng.randint(1,18))]]

def grid_oracle(args):
    grid,k=args;rows=len(grid);cols=len(grid[0]);answer=-1
    def visit(row,col,cost,score):
        nonlocal answer
        if cost>k:return
        if row==rows-1 and col==cols-1:answer=max(answer,score);return
        if row+1<rows:
            value=grid[row+1][col];visit(row+1,col,cost+(value>0),score+value)
        if col+1<cols:
            value=grid[row][col+1];visit(row,col+1,cost+(value>0),score+value)
    visit(0,0,0,0);return answer

def random_grid(rng):
    rows=rng.randint(1,5);cols=rng.randint(1,5);grid=[[rng.randint(0,2) for _ in range(cols)] for _ in range(rows)];grid[0][0]=0
    return [grid,rng.randint(0,rows+cols)]

def expanded_oracle(args):
    s,k=args;expanded=' '.join(''.join(character*(index+1) for index,character in enumerate(word)) for word in s.split(' '))
    return expanded[k]

def random_expanded(rng):
    words=[''.join(rng.choice('abcde') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,5))];s=' '.join(words)
    length=sum(len(word)*(len(word)+1)//2 for word in words)+len(words)-1
    return [s,rng.randrange(length)]


NONDECREASING='''def longest_nondecreasing_after_replacement(nums):
    n=len(nums);left=[1]*n;right=[1]*n
    for index in range(1,n):
        if nums[index]>=nums[index-1]:left[index]=left[index-1]+1
    for index in range(n-2,-1,-1):
        if nums[index]<=nums[index+1]:right[index]=right[index+1]+1
    answer=max(left)
    for index in range(n):
        before=left[index-1] if index else 0;after=right[index+1] if index+1<n else 0
        if 0<index<n-1 and nums[index-1]>nums[index+1]:answer=max(answer,before+1,after+1)
        else:answer=max(answer,before+1+after)
    return answer
'''

MAJORITY='''def count_target_majority_subarrays_fast(nums,target):
    n=len(nums);tree=[0]*(2*n+3)
    def add(index):
        while index<len(tree):tree[index]+=1;index+=index&-index
    def query(index):
        answer=0
        while index:answer+=tree[index];index-=index&-index
        return answer
    prefix=n+1;add(prefix);answer=0
    for value in nums:
        prefix+=1 if value==target else -1;answer+=query(prefix-1);add(prefix)
    return answer
'''

TRIPLE='''def minimum_equal_triple_distance(nums):
    positions={}
    for index,value in enumerate(nums):positions.setdefault(value,[]).append(index)
    answer=None
    for indices in positions.values():
        for start in range(len(indices)-2):
            distance=2*(indices[start+2]-indices[start]);answer=distance if answer is None else min(answer,distance)
    return -1 if answer is None else answer
'''

GRID='''def maximum_grid_path_score(grid,k):
    rows=len(grid);cols=len(grid[0]);previous=[None]*cols
    for row in range(rows):
        current=[None]*cols
        for col in range(cols):
            if row==0 and col==0:current[col]={0:0};continue
            value=grid[row][col];cost=int(value>0);states={}
            for source in ((previous[col] if row else None),(current[col-1] if col else None)):
                if source:
                    for used,score in source.items():
                        if used+cost<=k:states[used+cost]=max(states.get(used+cost,-1),score+value)
            current[col]=states
        previous=current
    return max(previous[-1].values(),default=-1)
'''

EXPANDED='''def kth_expanded_character(s,k):
    words=s.split(' ')
    for word_index,word in enumerate(words):
        length=len(word)*(len(word)+1)//2
        if k<length:
            used=0
            for index,character in enumerate(word):
                used+=index+1
                if k<used:return character
        k-=length
        if word_index+1<len(words):
            if k==0:return ' '
            k-=1
'''

def lesson(a,b,c,d):return [a,b,c,d]

N_CASES=[[[*values]] for values in ([1],[2,1],[1,2,3],[3,2,1],[2,2,2,2,3],[1,2,3,1,3],[5,1,2,3,4],[1,4,2,3,5],[3,3,1,2,2],[1,5,3,4,2,6],[10,9,8,7,6],[1,2,10,3,4,5,0])]
M_CASES=[[a,t] for a,t in (([1],1),([1],2),([1,1],1),([1,2],1),([1,2,2,4],2),([1,1,1,2],1),([1,2,3],4),([2,2,1,2,3],2),([5,4,5,5,6],5),([3,3,2,3,2,3],3),([7,8,7,9,7,7],7),([1,2,1,2,1,3,1],1))]
T_CASES=[[[*values]] for values in ([1],[1,1],[1,1,1],[1,2,1,1,4],[1,1,2,3,2,1,3],[2,2,2,2],[1,2,3,4],[3,1,3,2,3,3],[4,4,1,4,2,4,4],[1,2,1,2,1,2,1],[5,6,5,7,5,8,5],[2,3,2,2,3,2,3,3,3])]
G_CASES=[[g,k] for g,k in (([[0]],0),([[0,1]],0),([[0,2]],1),([[0,1],[1,0]],1),([[0,2],[2,0]],1),([[0,1],[1,2]],2),([[0,0,2],[1,2,0]],2),([[0,2,1],[1,0,2],[0,2,0]],2),([[0,1,2],[2,1,0],[0,2,1]],3),([[0,0,0],[2,2,2],[0,0,0]],1),([[0,2],[2,2]],0),([[0,1,0,2],[2,0,1,0],[0,2,0,1]],3))]
E_CASES=[[s,k] for s,k in (('a',0),('ab',1),('ab',2),('hello world',14),('hello world',16),('a bc',1),('a bc',2),('abc d',5),('xy z',2),('one two three',4),('aa bb',3),('coding practice',20))]

BATCH={
3738:entry('longest_nondecreasing_after_replacement',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums contains one to 100,000 signed integers.','Replace at most one element by any integer.','Return the maximum length of a contiguous nondecreasing subarray.'],[([[1,2,3,1,2]],'Replacing the fourth value by three creates a nondecreasing prefix of length four.'),([[2,2,2,2,2]],'The entire array is already nondecreasing, so its length five is optimal.')],N_CASES,NONDECREASING,[NONDECREASING.replace('nums[index-1]>nums[index+1]','nums[index-1]>=nums[index+1]'),NONDECREASING.replace('before+1+after','before+after')],['Refuses to bridge equal neighbors around the replaced value.','Forgets to count the replacement position when joining both sides.'],nondescending_oracle,random_nondescending,lesson('Precompute the nondecreasing run ending at every index and starting at every index.','Replacing position i can join its left and right runs exactly when the neighboring values leave some value between them.','Otherwise attach the replacement only to the better side; also retain the best unchanged run.','These are all possibilities for a subarray using zero or one replacement, and the two run arrays give their exact lengths.'),'O(n)','O(n)',6),
3739:entry('count_target_majority_subarrays_fast',[('nums','list[int]'),('target','int')],'int',['arrays','fenwick trees','prefix sums'],['nums contains up to 100,000 positive integers.','A subarray qualifies when target occurs strictly more than half its length.','Return the total qualifying subarray count.'],[([[1,2,2,3],2],'Five subarrays have target two as a strict majority.'),([[1,1,1,1],1],'All ten subarrays have target one as a strict majority.')],M_CASES,MAJORITY,[MAJORITY.replace('query(prefix-1)','query(prefix)'),MAJORITY.replace('1 if value==target else -1','-1 if value==target else 1')],['Counts equal prefix balances and therefore includes tied subarrays.','Reverses the target and non-target prefix contributions.'],majority_oracle,random_majority,lesson('Map target to +1 and every other value to -1; a subarray has target majority exactly when its transformed sum is positive.','For each prefix sum, count earlier prefix sums that are strictly smaller.','Offset sums into positive Fenwick indices, query prefix-1, then insert the current sum.','Every qualifying subarray corresponds uniquely to an ordered prefix pair with later sum greater than earlier sum.'),'O(n log n)','O(n)',8),
3741:entry('minimum_equal_triple_distance',[('nums','list[int]')],'int',['arrays','hash maps'],['nums contains up to 100,000 values between one and n.','Choose three distinct indices holding the same value.','Minimize the sum of their three pairwise index distances, or return negative one if impossible.'],[([[1,2,1,1,3]],'Indices 0,2,3 have total pairwise distance six.'),([[1,1,2,3,2,1,2]],'Indices 2,4,6 holding two have distance eight.')],T_CASES,TRIPLE,[TRIPLE.replace('indices[start+2]-indices[start]','indices[start+2]-indices[start+1]'),TRIPLE.replace('range(len(indices)-2)','range(max(0,len(indices)-3))')],['Uses only the final gap instead of the full first-to-third span.','Skips the last consecutive triple of occurrences.'],triple_oracle,random_triple,lesson('For sorted indices i<j<k, the three-distance sum simplifies to 2(k-i).','Group occurrence indices by value and inspect every consecutive triple in each group.','Minimize twice the gap between the first and third occurrence.','Any nonconsecutive triple can move an endpoint inward to a skipped equal occurrence without increasing its span, so a consecutive optimum exists.'),'O(n)','O(n)',5),
3742:entry('maximum_grid_path_score',[('grid','list[list[int]]'),('k','int')],'int',['matrices','dynamic programming'],['grid has up to 200 rows and columns and values zero, one, or two; its first cell is zero.','Move only right or down; nonzero cells cost one budget unit and contribute their value to score.','Return the maximum score using cost at most k, or negative one when no path fits.'],[([[[0,1],[2,0]],1],'The down-right path costs one and scores two.'),([[[0,1],[1,2]],1],'Every path uses two nonzero cells, so none fits budget one.')],G_CASES,GRID,[GRID.replace('cost=int(value>0)','cost=value'),GRID.replace('score+value','score+1')],['Charges score value as budget cost instead of one per nonzero cell.','Awards one point for every visited cell instead of its stored value.'],grid_oracle,random_grid,lesson('A path state needs its cell, used budget, and best score; worse scores at the same state are dominated.','Sweep the grid and merge states from the top and left, adding the current cell’s cost and score.','Keep the maximum score for each reachable cost no greater than k.','Every monotone path reaches a cell from exactly one predecessor, so the transitions enumerate all feasible paths and retain their optimum.'),'O(mn(m+n))','O(n(m+n))',6),
3744:entry('kth_expanded_character',[('s','str'),('k','int')],'str',['strings','math'],['s contains lowercase words separated by single spaces and has no leading or trailing space.','Within each word, character i is repeated i+1 times; original spaces remain single.','k is a valid zero-based index in the expanded string.'],[(['hello world',0],'The first expanded character is h.'),(['hello world',15],'The first expanded word has length fifteen, so index fifteen is the separating space.')],E_CASES,EXPANDED,[EXPANDED.replace('index+1','index'),EXPANDED.replace('k-=length','k-=length+1')],['Repeats the first letter zero times and shifts every character block.','Subtracts the separator twice when moving to the next word.'],expanded_oracle,random_expanded,lesson('A word of length m expands to triangular length m(m+1)/2.','Skip whole expanded words and their single separators until k lies inside one word.','Within that word, accumulate block sizes one, two, and so on until the block containing k is reached.','The skipped lengths exactly partition the expanded string, so the first containing block identifies the requested character without constructing t.'),'O(|s|)','O(number of words)',5),
}
