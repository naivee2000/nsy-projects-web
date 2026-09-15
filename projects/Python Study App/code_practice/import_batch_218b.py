"""Ending AND states, recursive binary strings, anchored matrices, trie costs, and XOR parity."""
from itertools import product

from .import_batch_055 import entry


def and_oracle(args):
    nums,target=args;answer=0
    for left in range(len(nums)):
        value=nums[left]
        for right in range(left,len(nums)):
            if right>left:value&=nums[right]
            answer+=value==target
    return answer


def random_and(rng):return [[rng.randint(0,63) for _ in range(rng.randint(1,15))],rng.randint(0,63)]


def strings_oracle(args):
    n=args[0];return [''.join(bits) for bits in product('01',repeat=n) if '00' not in ''.join(bits)]


def random_strings(rng):return [rng.randint(1,10)]


def matrices_oracle(args):
    grid=args[0];answer=0
    for bottom in range(len(grid)):
        for right in range(len(grid[0])):
            cells=[grid[row][column] for row in range(bottom+1) for column in range(right+1)]
            answer+=cells.count('X')==cells.count('Y') and cells.count('X')>0
    return answer


def random_matrices(rng):
    rows=rng.randint(1,6);columns=rng.randint(1,6)
    return [[[rng.choice('XY.') for _ in range(columns)] for _ in range(rows)]]


def cost_oracle(args):
    target,words,costs=args;dp=[10**30]*(len(target)+1);dp[0]=0
    for index in range(len(target)):
        if dp[index]>=10**30:continue
        for word,cost in zip(words,costs):
            if target.startswith(word,index):dp[index+len(word)]=min(dp[index+len(word)],dp[index]+cost)
    return -1 if dp[-1]>=10**30 else dp[-1]


def random_cost(rng):
    target=''.join(rng.choice('abc') for _ in range(rng.randint(1,12)));words=[];costs=[]
    for _ in range(rng.randint(1,12)):
        words.append(''.join(rng.choice('abc') for _ in range(rng.randint(1,5))));costs.append(rng.randint(1,20))
    return [target,words,costs]


def triplets_oracle(args):
    first,second,third=args
    return sum(((a^b^c).bit_count()&1)==0 for a in first for b in second for c in third)


def random_triplets(rng):return [[rng.randint(0,255) for _ in range(rng.randint(1,8))] for _ in range(3)]


AND='''def count_subarrays_with_and(nums,k):
    previous={};answer=0
    for number in nums:
        current={number:1}
        for value,count in previous.items():current[value&number]=current.get(value&number,0)+count
        answer+=current.get(k,0);previous=current
    return answer
'''


STRINGS='''def binary_strings_without_adjacent_zeros(n):
    answer=[]
    def build(prefix):
        if len(prefix)==n:answer.append(prefix);return
        build(prefix+'1')
        if not prefix or prefix[-1]!='0':build(prefix+'0')
    build('');return answer
'''


MATRICES='''def count_balanced_origin_submatrices(grid):
    columns=len(grid[0]);x=[0]*columns;y=[0]*columns;answer=0
    for row in grid:
        total_x=total_y=0
        for column,value in enumerate(row):
            x[column]+=value=='X';y[column]+=value=='Y';total_x+=x[column];total_y+=y[column]
            if total_x>0 and total_x==total_y:answer+=1
    return answer
'''


COST='''def minimum_target_construction_cost(target,words,costs):
    root={}
    for word,cost in zip(words,costs):
        node=root
        for char in word:node=node.setdefault(char,{})
        node['$']=min(node.get('$',10**30),cost)
    dp=[10**30]*(len(target)+1);dp[0]=0
    for start in range(len(target)):
        if dp[start]>=10**30:continue
        node=root
        for end in range(start,len(target)):
            if target[end] not in node:break
            node=node[target[end]]
            if '$' in node:dp[end+1]=min(dp[end+1],dp[start]+node['$'])
    return -1 if dp[-1]>=10**30 else dp[-1]
'''


TRIPLETS='''def even_popcount_xor_triplets(a,b,c):
    def counts(values):
        odd=sum(value.bit_count()&1 for value in values);return len(values)-odd,odd
    ae,ao=counts(a);be,bo=counts(b);ce,co=counts(c)
    return ae*be*ce+ae*bo*co+ao*be*co+ao*bo*ce
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3209:entry('count_subarrays_with_and',[('nums','list[int]'),('k','int')],'int',['bit manipulation','dynamic programming','subarrays'],['nums is a nonempty nonnegative-integer array and k is nonnegative.','Count nonempty contiguous subarrays whose bitwise AND equals k.','Different index ranges count separately even when their values are identical.'],[([[1,1,1],1],'All six nonempty subarrays have AND one.'),([[7,3,3],3],'The two single threes and the three ranges ending after index zero have AND three, totaling five.')],[[n,k] for n,k in [([1,1,1],1),([7,3,3],3),([1],0),([0],0),([1,2],0),([7,7],7),([6,3,2],2),([15,7,3,1],1),([8,4,2],0),([5,5,1],5),([3,2,3],2),([0,1,0],0),([31,15,7],7),([10,14,6,2],2)]],AND,[AND.replace('value&number','value|number'),AND.replace('current={number:1}','current={}')],['Carries ending bitwise OR values rather than AND values.','Omits the one-element subarray beginning at each position.'],and_oracle,random_and,lesson('All subarrays ending at the current index arise from the singleton or by extending a previous ending subarray.','Map each distinct ending AND value to the number of ranges producing it; equal values merge.','current[number]+=1; current[old&number]+=count; add current[k].','The recurrence preserves every left endpoint and AND is idempotent, so combining equal states loses no counts or future behavior.'),'O(n*word_bits)','O(word_bits)',8),
3211:entry('binary_strings_without_adjacent_zeros',[('n','int')],'list[str]',['backtracking','recursion','strings'],['n is positive.','Generate every binary string of length n that does not contain 00 as a substring.','Return each valid string exactly once; output order does not matter.'],[([3],'The five valid strings are 010, 011, 101, 110, and 111.'),([1],'Both one-character strings 0 and 1 are valid.')],[[n] for n in [2,4,5,6,7,8,9,10,11,12,13,14,15,16]],STRINGS,[STRINGS.replace("if not prefix or prefix[-1]!='0'","if True"),STRINGS.replace("build(prefix+'1')","build(prefix+'0')",1)],['Generates strings containing adjacent zeros.','Explores the zero branch twice and never generates strings beginning with or extending by one.'],strings_oracle,random_strings,lesson('A zero may be appended only when the prefix is empty or ends in one; a one is always legal.','Backtrack over the next character while carrying the already-built prefix.','At length n record; recurse with 1; recurse with 0 only if previous is not 0.','Every valid string has one unique prefix path, and the local guard excludes exactly the forbidden substring.'),'O(number of outputs*n)','O(n) recursion plus output',5),
3212:entry('count_balanced_origin_submatrices',[('grid','list[list[str]]')],'int',['prefix sums','matrices'],['grid is a nonempty rectangle containing X, Y, or dot characters.','Count rectangles with top-left corner fixed at grid[0][0] and arbitrary bottom-right corner.','A counted rectangle contains at least one X and has equal X and Y counts.'],[([[['X','Y','.'],['Y','.','.']]],'The balanced origin-anchored rectangles ending at columns one or two of the first row and column zero of the second row total three.'),([[['.','X'],['Y','.']]],'Only the full 2x2 origin-anchored rectangle has one X and one Y.')],[[g] for g in [[['X']],[['.']],[['X','Y','.'],['Y','.','.']],[['.','X'],['Y','.']],[['X','Y']],[['Y','X']],[['X','.'],['.','Y']],[['X','X'],['Y','Y']],[['.','.'],['X','Y']],[['X','Y','X'],['Y','X','Y']],[['Y','.'],['.','X']],[['X','.','.'],['.','Y','.'],['.','.','X']],[['.','X','Y']],[['X','Y'],['.','.'],['Y','X']]]],MATRICES,[MATRICES.replace('total_x>0 and total_x==total_y','total_x==total_y'),MATRICES.replace("x[column]+=value=='X'","x[column]+=value!='Y'")],['Counts empty-of-X rectangles where both X and Y totals are zero.','Treats dot cells as X and inflates the X prefix count.'],matrices_oracle,random_matrices,lesson('Every eligible rectangle is a two-dimensional prefix ending at one bottom-right cell.','Accumulate per-column X/Y totals by row, then running totals across columns.','For each cell add column counts to row prefix; count when X>0 and X==Y.','The accumulated totals equal exactly the origin-to-current rectangle, so testing every bottom-right corner counts each eligible rectangle once.'),'O(rows*columns)','O(columns)',5),
3213:entry('minimum_target_construction_cost',[('target','str'),('words','list[str]'),('costs','list[int]')],'int',['tries','dynamic programming','strings'],['target is nonempty; words and positive costs have equal nonzero length, and words are nonempty.','Starting empty, append whole listed words to form target exactly; a word may be reused.','Return the minimum total cost or -1 when construction is impossible.'],[(['abcdef',['abdef','abc','d','def','ef'],[100,1,1,10,5]],'Append abc, d, and ef for total cost seven.'),(['aaaa',['a','aa'],[3,5]],'Two copies of aa cost ten, which is cheaper than four copies of a.')],[[t,w,c] for t,w,c in [('abcdef',['abdef','abc','d','def','ef'],[100,1,1,10,5]),('aaaa',['a','aa'],[3,5]),('a',['a'],[7]),('a',['b'],[1]),('abc',['a','bc'],[2,3]),('abc',['ab','c','abc'],[2,2,10]),('aaaa',['a','a'],[5,1]),('leetcode',['leet','code'],[4,5]),('abab',['ab','a','b'],[3,2,2]),('xyz',['x','yz','xy','z'],[1,10,5,2]),('banana',['ba','na','nana'],[2,1,8]),('miss',['mi','s'],[3,2]),('aaaaaa',['aaa','aa'],[4,3]),('target',['tar','get','target'],[5,5,20])]],COST,[COST.replace("min(node.get('$',10**30),cost)","max(node.get('$',0),cost)"),COST.replace('range(start,len(target))','range(start+1,len(target))')],['Keeps the most expensive duplicate spelling instead of the cheapest available cost.','Begins trie matching one character too late and misses every word starting at the current target position.'],cost_oracle,random_cost,lesson('Target construction is a shortest path over prefix positions; trie traversal lists all word edges beginning at one position.','Store the minimum cost for duplicate words, then relax reachable target prefixes through trie matches.','For each reachable start, walk target characters in trie; at each word end relax dp[end+1].','Every construction uniquely partitions target into trie words, and DP considers its edges in increasing prefix order, yielding the minimum path cost.'),'O(total word length+target length*maximum word length)','O(total word length+target length)',8),
3215:entry('even_popcount_xor_triplets',[('a','list[int]'),('b','list[int]'),('c','list[int]')],'int',['bit manipulation','counting'],['a, b, and c are nonempty arrays of nonnegative integers.','Choose one value from each array and count index triplets whose XOR has an even number of set bits.','Repeated equal values at different indices count as separate choices.'],[([[1],[2],[3]],'The XOR is zero, which has zero set bits and therefore counts.'),([[1,2],[3],[4,5]],'Classifying each number by set-bit parity counts the combinations whose three parities XOR to even.')],[[a,b,c] for a,b,c in [([1],[2],[3]),([0],[0],[0]),([1],[1],[1]),([1,2],[3],[4,5]),([1,1],[2,2],[3,3]),([0,1],[0,1],[0,1]),([7],[8],[15]),([3,5],[6,9],[10]),([2,4,8],[1],[3]),([15,16],[31],[0,1]),([5,10],[12,3],[6,9]),([255],[1,2],[3,4]),([0,0,1],[2,2],[3]),([6,7,8],[9,10],[11,12])]],TRIPLETS,[TRIPLETS.replace('ae*be*ce+',''),TRIPLETS.replace('value.bit_count()&1','value&1')],['Counts only parity patterns containing at least one odd-popcount value and omits even-even-even.','Classifies integers by numeric odd/even parity rather than set-bit-count parity.'],triplets_oracle,random_triplets,lesson('Popcount parity of an XOR equals the XOR of the operands’ popcount parities.','Count even- and odd-popcount values in each array, then multiply the four parity combinations totaling even.','Add EEE, EOO, OEO, and OOE products.','These four disjoint parity patterns are exactly the triples with parity XOR zero, and frequency products count their index choices.'),'O(len(a)+len(b)+len(c))','O(1)',5),
}
BATCH[3211]['comparator']='unordered'
