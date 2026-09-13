"""Reviewed memoization, counting, bit, matrix-shape, and partition imports."""
from collections import Counter, deque

from .import_batch_055 import entry


def stickers_oracle(args):
    stickers,target=args
    counts=[Counter(word) for word in stickers]
    start=''.join(sorted(target));queue=deque([(start,0)]);seen={start}
    while queue:
        remaining,steps=queue.popleft()
        if not remaining:return steps
        need=Counter(remaining)
        for sticker in counts:
            if not sticker[remaining[0]]:continue
            following=''.join(sorted((need-sticker).elements()))
            if following not in seen:seen.add(following);queue.append((following,steps+1))
    return -1


def top_words_oracle(args):
    words,k=args;counts=Counter(words)
    return sorted(counts,key=lambda word:(-counts[word],word))[:k]


def alternating_oracle(args):
    bits=bin(args[0])[2:]
    return all(left!=right for left,right in zip(bits,bits[1:]))


def islands_oracle(args):
    grid=args[0];rows,columns=len(grid),len(grid[0]);seen=set();shapes=set()
    for row in range(rows):
        for column in range(columns):
            if not grid[row][column] or (row,column) in seen:continue
            stack=[(row,column)];seen.add((row,column));cells=[]
            while stack:
                r,c=stack.pop();cells.append((r-row,c-column))
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            shapes.add(tuple(sorted(cells)))
    return len(shapes)


def binary_substrings_oracle(args):
    text=args[0];total=0
    for left in range(len(text)):
        for right in range(left+2,len(text)+1):
            fragment=text[left:right]
            split=next((i for i in range(1,len(fragment)) if fragment[i]!=fragment[0]),len(fragment))
            if split<len(fragment) and all(char==fragment[split] for char in fragment[split:]) and split==len(fragment)-split:total+=1
    return total


def degree_oracle(args):
    nums=args[0];counts=Counter(nums);degree=max(counts.values())
    return min(max(i for i,v in enumerate(nums) if v==value)-min(i for i,v in enumerate(nums) if v==value)+1 for value,count in counts.items() if count==degree)


def partition_oracle(args):
    nums,k=args;total=sum(nums)
    if total%k:return False
    target=total//k;bins=[0]*k
    def search(index):
        if index==len(nums):return all(value==target for value in bins)
        value=sorted(nums,reverse=True)[index]
        tried=set()
        for bucket in range(k):
            if bins[bucket] in tried or bins[bucket]+value>target:continue
            tried.add(bins[bucket]);bins[bucket]+=value
            if search(index+1):return True
            bins[bucket]-=value
        return False
    return search(0)


def random_stickers(rng):
    stickers=[''.join(rng.choice('abcde') for _ in range(rng.randint(1,6))) for _ in range(rng.randint(1,5))]
    target=''.join(rng.choice('abcde') for _ in range(rng.randint(1,7)))
    return [stickers,target]
def random_words(rng):
    vocab=[''.join(rng.choice('abcde') for _ in range(rng.randint(1,4))) for _ in range(rng.randint(1,8))]
    words=[rng.choice(vocab) for _ in range(rng.randint(1,20))];return [words,rng.randint(1,len(set(words)))]
def random_alternating(rng):return [rng.randint(1,2**20)]
def random_grid(rng):
    rows,columns=rng.randint(1,6),rng.randint(1,6);return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]
def random_binary(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,20)))]
def random_degree(rng):return [[rng.randint(0,6) for _ in range(rng.randint(1,20))]]
def random_partition(rng):
    nums=[rng.randint(1,10) for _ in range(rng.randint(1,9))]
    return [nums,rng.randint(1,min(4,len(nums)))]


STICKERS='''\
def minimum_stickers(stickers, target):
    from collections import Counter
    from functools import lru_cache
    available=[Counter(sticker) for sticker in stickers]
    @lru_cache(None)
    def solve(remaining):
        if not remaining:return 0
        need=Counter(remaining);best=float('inf')
        for sticker in available:
            if not sticker[remaining[0]]:continue
            following=''.join(sorted((need-sticker).elements()))
            result=solve(following)
            if result>=0:best=min(best,1+result)
        return -1 if best==float('inf') else best
    return solve(''.join(sorted(target)))
'''
TOP='''\
def top_frequent_words(words, k):
    from collections import Counter
    counts=Counter(words)
    return sorted(counts,key=lambda word:(-counts[word],word))[:k]
'''
ALTERNATING='''\
def has_alternating_bits(n):
    changed=n^(n>>1)
    return changed&(changed+1)==0
'''
ISLANDS='''\
def distinct_island_shapes(grid):
    rows,columns=len(grid),len(grid[0]);seen=set();shapes=set()
    for row in range(rows):
        for column in range(columns):
            if not grid[row][column] or (row,column) in seen:continue
            stack=[(row,column)];seen.add((row,column));shape=[]
            while stack:
                r,c=stack.pop();shape.append((r-row,c-column))
                for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            shapes.add(tuple(sorted(shape)))
    return len(shapes)
'''
BINARY='''\
def count_balanced_binary_substrings(s):
    previous=0;current=1;answer=0
    for index in range(1,len(s)):
        if s[index]==s[index-1]:current+=1
        else:
            answer+=min(previous,current);previous,current=current,1
    return answer+min(previous,current)
'''
DEGREE='''\
def shortest_degree_subarray(nums):
    first={};counts={};degree=0;answer=len(nums)
    for index,value in enumerate(nums):
        first.setdefault(value,index);counts[value]=counts.get(value,0)+1
        if counts[value]>degree:degree=counts[value];answer=index-first[value]+1
        elif counts[value]==degree:answer=min(answer,index-first[value]+1)
    return answer
'''
PARTITION='''\
def can_partition_k_subsets(nums, k):
    total=sum(nums)
    if total%k:return False
    target=total//k;nums=sorted(nums,reverse=True);bins=[0]*k
    def search(index):
        if index==len(nums):return True
        value=nums[index]
        for bucket in range(k):
            if bins[bucket]+value>target:continue
            bins[bucket]+=value
            if search(index+1):return True
            bins[bucket]-=value
            if bins[bucket]==0:break
        return False
    return nums[0]<=target and search(0)
'''


STICKERS_SET=STICKERS.replace('Counter(sticker)','Counter(set(sticker))')
STICKERS_GREEDY="def minimum_stickers(stickers,target):\n    remaining=list(target);used=0\n    while remaining:\n        best=max(stickers,key=lambda s:sum(c in remaining for c in s))\n        old=len(remaining)\n        for c in best:\n            if c in remaining:remaining.remove(c)\n        if len(remaining)==old:return -1\n        used+=1\n    return used\n"
TOP_INPUT="def top_frequent_words(words,k):\n    from collections import Counter\n    counts=Counter(words)\n    return sorted(counts,key=lambda word:-counts[word])[:k]\n"
TOP_ALPHA="def top_frequent_words(words,k):\n    return sorted(set(words))[:k]\n"
ALT_EVEN="def has_alternating_bits(n):\n    return bin(n).count('1')*2 in (n.bit_length(),n.bit_length()+1)\n"
ALT_LAST="def has_alternating_bits(n):\n    return n&1 != (n>>1)&1\n"
ISLAND_COUNT=ISLANDS.replace('return len(shapes)','return sum(1 for shape in shapes) if False else len(seen)')
ISLAND_AREA="def distinct_island_shapes(grid):\n    return len({sum(row) for row in grid})\n"
BINARY_RUNS="def count_balanced_binary_substrings(s):\n    return 1+sum(a!=b for a,b in zip(s,s[1:]))\n"
BINARY_PAIRS="def count_balanced_binary_substrings(s):\n    return sum(a!=b for a,b in zip(s,s[1:]))\n"
DEGREE_VALUE=DEGREE.replace('return answer','return degree')
DEGREE_FIRST="def shortest_degree_subarray(nums):\n    from collections import Counter\n    value=Counter(nums).most_common(1)[0][0]\n    return len(nums)-nums[::-1].index(value)-nums.index(value)\n"
PARTITION_DIVISIBLE="def can_partition_k_subsets(nums,k):\n    return sum(nums)%k==0\n"
PARTITION_GREEDY="def can_partition_k_subsets(nums,k):\n    if sum(nums)%k:return False\n    target=sum(nums)//k;bins=[0]*k\n    for value in sorted(nums,reverse=True):\n        for bucket in range(k):\n            if bins[bucket]+value<=target:\n                bins[bucket]+=value\n                break\n        else:return False\n    return all(value==target for value in bins)\n"


def lesson(a,b,c,d):return [a,b,c,d],d
BATCH={
691:entry('minimum_stickers',[('stickers','list[str]'),('target','str')],'int',['dynamic-programming','backtracking'],['1 <= len(stickers) <= 50; target has at most 15 lowercase letters.','Stickers may be reused; return the minimum count needed to form target or -1.'],[([['with','example','science'],'thehat'],'Three stickers suffice to supply every required letter.'),([['notice','possible'],'basicbasic'],'No sticker contains a b, so the target is impossible.')],[[s,t] for s,t in ((['a'],'a'),(['a'],'aa'),(['ab'],'ba'),(['ab'],'abc'),(['abc','def'],'fed'),(['ab','bc'],'abbc'),(['aaaa','b'],'aaaab'),(['aab','abb'],'aaabb'),(['xyz','xy'],'zyx'),(['these','guess','about','garden','him'],'atomher'),(['a','b','c'],'abcabc'),(['abc','bcd','cde'],'edcba'))],STICKERS,[STICKERS_SET,STICKERS_GREEDY],['Treats repeated letters on one sticker as a set.','Greedily chooses current overlap and can miss a globally smaller combination.'],stickers_oracle,random_stickers,*lesson('Only the multiset of still-needed letters matters.','Memoize a canonical sorted remainder and subtract each useful sticker.','Try stickers containing the first remaining letter; recurse on need-sticker and add one.','Canonical remainders merge different application orders, and requiring the first letter prunes equivalent unhelpful choices.'),'O(stickers * exponential target states)','O(exponential target states)',8),
692:entry('top_frequent_words',[('words','list[str]'),('k','int')],'list[str]',['hash-maps','sorting'],['1 <= k <= number of distinct words.','Rank higher frequency first and lexicographically smaller words first on ties.'],[([['i','love','leetcode','i','love','coding'],2],'i and love each appear twice and are ordered lexicographically.'),([['the','day','is','sunny','the','the','the','sunny','is','is'],4],'Frequency determines the order the, is, sunny, day.')],[[w,k] for w,k in ((['a'],1),(['b','a'],2),(['b','a'],1),(['a','b','a'],2),(['x','y','z','y','x'],3),(['c','b','a','c','b','a'],2),(['aa','a','aa','a'],1),(['z','z','a'],2),(['one','two','two','three','three','three'],2),(['b','c','a','b','c','a'],3),(['x','x','y','z','z'],2),(['dog','cat','dog','ant','cat'],2))],TOP,[TOP_INPUT,TOP_ALPHA],['Keeps first-seen order for equal frequencies instead of lexical order.','Ignores frequency and returns alphabetically smallest words.'],top_words_oracle,random_words,*lesson('The ranking has two explicit keys.','Count each word, then sort distinct words by negative count and the word itself.','Return sorted(counts,key=(-frequency,word))[:k].','Python tuple ordering implements the required primary descending and secondary ascending order exactly.'),'O(n log n)','O(n)',5),
693:entry('has_alternating_bits',[('n','int')],'bool',['bit-manipulation'],['1 <= n <= 2^31-1.','Adjacent bits in the binary representation must always differ.'],[([5],'Binary 101 alternates.'),([7],'Binary 111 contains equal adjacent bits.')],[[n] for n in (1,2,3,4,6,8,10,11,21,42,85,170)],ALTERNATING,[ALT_EVEN,ALT_LAST],['Checks only the total number of one bits, not their positions.','Checks only the final adjacent bit pair.'],alternating_oracle,random_alternating,*lesson('XOR with a one-bit shift turns every alternating adjacency into one.','Compute changed=n^(n>>1) and test whether it is all binary ones.','An all-ones value x satisfies x&(x+1)==0.','Every original adjacent pair contributes one XOR bit; the leading bit also contributes one, so all ones is equivalent to full alternation.'),'O(1)','O(1)',3),
694:entry('distinct_island_shapes',[('grid','list[list[int]]')],'int',['matrices','depth-first-search'],['Grid cells are zero or one; islands connect orthogonally.','Two islands are equal only by translation, not rotation or reflection.'],[([[[1,1,0,0,0],[1,1,0,0,0],[0,0,0,1,1],[0,0,0,1,1]]],'The two translated 2x2 islands have one distinct shape.'),([[[1,1,0],[0,1,0],[1,0,0]]],'The bent island and isolated cell produce two shapes.')],[[g] for g in ([[0]],[[1]],[[1,0,1]],[[1,1],[1,1]],[[1,0],[0,1]],[[1,1,0],[0,0,1]],[[1,0,0],[1,1,0],[0,0,1]],[[1,1,0,1],[1,0,0,1]],[[1,0,1],[1,0,1]],[[1,1,0],[1,0,1],[0,0,1]],[[0,1,0],[1,1,0],[0,0,1]],[[1,0,0,1],[1,1,0,1]])],ISLANDS,[ISLAND_COUNT,ISLAND_AREA],['Counts land cells rather than distinct island shapes.','Compares row totals instead of connected relative coordinates.'],islands_oracle,random_grid,*lesson('Translation invariance is achieved by coordinates relative to each island’s origin.','Flood-fill each unseen island and store its sorted relative cell offsets.','Subtract the start row/column from every visited cell; add the tuple to a set.','Translated copies produce identical offset sets, while any different orthogonal shape differs at some relative cell.'),'O(rows*columns)','O(rows*columns)',5),
696:entry('count_balanced_binary_substrings',[('s','str')],'int',['strings','two-pointers'],['1 <= len(s) <= 50,000; s contains only 0 and 1.','Count substrings with equal consecutive runs of zeros and ones.'],[(['00110011'],'Six substrings have two equal adjacent runs.'),(['10101'],'Each adjacent differing pair forms one valid length-two substring, giving four.')],[[s] for s in ('0','1','01','10','00','0011','000111','00110','1110001','010101','0000','11001100')],BINARY,[BINARY_RUNS,BINARY_PAIRS],['Returns the number of runs instead of the number of valid substrings.','Counts only length-two transitions and misses longer balanced runs.'],binary_substrings_oracle,random_binary,*lesson('Only the lengths of two adjacent character runs determine how many substrings cross their boundary.','For every run boundary, add the smaller of the previous and current run lengths.','Track two run lengths while scanning; add min(previous,current) when a run ends and once at the end.','For each length from one through the smaller run, exactly one balanced substring is centered on that boundary.'),'O(n)','O(1)',3),
697:entry('shortest_degree_subarray',[('nums','list[int]')],'int',['arrays','hash-maps'],['1 <= len(nums) <= 50,000.','Return the shortest contiguous subarray with the same maximum frequency (degree) as the full array.'],[([[1,2,2,3,1]],'The array degree is two, and [2,2] is the shortest matching subarray.'),([[1,2,2,3,1,4,2]],'Two appears three times, spanning indices one through six for length six.')],[[x] for x in ([1],[1,1],[1,2],[1,2,1],[1,2,2,1],[3,1,2,3,2],[0,0,1,1],[1,2,3,4],[5,1,5,2,5],[1,1,2,2,2,1],[9,8,9,8,8],[2,1,2,1,2,1])],DEGREE,[DEGREE_VALUE,DEGREE_FIRST],['Returns the degree value rather than a subarray length.','Uses only the first most-frequent value and misses a shorter tied span.'],degree_oracle,random_degree,*lesson('For a chosen value, the shortest subarray containing all its occurrences spans its first through last occurrence.','Track first index, running count, current degree, and best span online.','On a new degree replace the answer; on an equal degree minimize with index-first[value]+1.','Any subarray retaining the full degree must include every occurrence of at least one degree-achieving value.'),'O(n)','O(n)',3),
698:entry('can_partition_k_subsets',[('nums','list[int]'),('k','int')],'bool',['backtracking','dynamic-programming'],['1 <= k <= len(nums) <= 16; values are positive.','Use every value exactly once to form k nonempty subsets with equal sums.'],[([[4,3,2,3,5,2,1],4],'The values can form four groups each summing five.'),([[1,2,3,4],3],'The total ten is not divisible by three.')],[[n,k] for n,k in (([1],1),([1,1],2),([1,2],2),([2,2,2,2],2),([2,1,4,5,6],3),([1,1,1,1,2,2,2,2],4),([5,5,5,5],4),([4,8,6,3,10,3],2),([1,2,3,4,5,6],3),([2,2,2,2,3,4,5],4),([3,3,3,3,4,4,4,4],4),([8,7,6,5,4,3,2,1],4))],PARTITION,[PARTITION_DIVISIBLE,PARTITION_GREEDY],['Checks only total divisibility without constructing subsets.','Uses first-fit placement without backtracking and can miss a valid assignment.'],partition_oracle,random_partition,*lesson('Once the target sum is fixed, the task is a symmetric bucket assignment.','Place large values first and backtrack while skipping equivalent bucket sums.','Try each value in a fitting bucket; after an empty-bucket failure, stop trying other empty buckets.','Sorting exposes impossibility early, and equal-load buckets are interchangeable, making symmetry pruning sound.'),'O(k^n)','O(k+n)',7),
}
