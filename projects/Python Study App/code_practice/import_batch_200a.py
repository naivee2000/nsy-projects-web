"""Build scheduling, rank counts, substrings, similar arrays, and parity swaps."""
from functools import lru_cache
from itertools import permutations
from .import_batch_055 import entry

def build_oracle(a):
    blocks,split=a
    @lru_cache(None)
    def solve(state):
        if len(state)==1:return state[0]
        answer=float('inf');n=len(state)
        for mask in range(1,1<<(n-1)):
            left=tuple(state[i] for i in range(n) if mask>>i&1)
            right=tuple(state[i] for i in range(n) if not mask>>i&1)
            if left and right:answer=min(answer,split+max(solve(tuple(sorted(left))),solve(tuple(sorted(right)))))
        return answer
    return solve(tuple(sorted(blocks)))
def random_build(r):return [[r.randint(1,30) for _ in range(r.randint(1,4))],r.randint(1,8)]
def smaller_oracle(a):return [sum(y<x for j,y in enumerate(a[0]) if j!=i) for i,x in enumerate(a[0])]
def random_smaller(r):return [[r.randint(0,100) for _ in range(r.randint(2,40))]]
def distinct_oracle(a):
    root={};answer=0
    for start in range(len(a[0])):
        node=root
        for char in a[0][start:]:
            if char not in node:node[char]={};answer+=1
            node=node[char]
    return answer
def random_distinct(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,16)))]
def similar_oracle(a):
    nums,target=a;answer=float('inf')
    for order in permutations(target):
        if all((x-y)%2==0 for x,y in zip(nums,order)):
            answer=min(answer,sum(max(0,x-y)//2 for x,y in zip(nums,order)))
    return answer
def random_similar(r):
    nums=[2*r.randint(1,12)+r.randint(0,1) for _ in range(r.randint(2,6))];target=nums[:]
    for _ in range(r.randint(0,5)):
        same=[(i,j) for i in range(len(nums)) for j in range(len(nums)) if i!=j and target[j]>2 and (target[i]-target[j])%2==0]
        if same:
            i,j=r.choice(same);target[i]+=2;target[j]-=2
    r.shuffle(target);return [nums,target]
def parity_oracle(a):
    s1,s2=a;seen={s1};todo=[s1]
    while todo:
        value=todo.pop()
        if value==s2:return True
        for i in range(len(value)):
            for j in range(i+2,len(value),2):
                chars=list(value);chars[i],chars[j]=chars[j],chars[i];nxt=''.join(chars)
                if nxt not in seen:seen.add(nxt);todo.append(nxt)
    return False
def random_parity(r):
    n=r.randint(1,8);return [''.join(r.choice('abcd') for _ in range(n)),''.join(r.choice('abcd') for _ in range(n))]

BUILD='''def minimum_block_build_time(blocks,split):
    from heapq import heapify,heappop,heappush
    work=list(blocks);heapify(work)
    while len(work)>1:
        heappop(work);heappush(work,heappop(work)+split)
    return work[0]
'''
SMALLER='''def count_smaller_numbers(nums):
    from bisect import bisect_left
    ordered=sorted(nums)
    return [bisect_left(ordered,x) for x in nums]
'''
DISTINCT='''def count_distinct_substrings(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1)})
'''
SIMILAR='''def minimum_operations_to_make_similar(nums,target):
    left=sorted(nums,key=lambda x:(x&1,x));right=sorted(target,key=lambda x:(x&1,x))
    return sum(abs(x-y) for x,y in zip(left,right))//4
'''
PARITY='''def can_make_strings_equal(s1,s2):
    from collections import Counter
    return Counter(s1[::2])==Counter(s2[::2]) and Counter(s1[1::2])==Counter(s2[1::2])
'''

BATCH={
1199:entry('minimum_block_build_time',[('blocks','list[int]'),('split','int')],'int',['heaps','greedy'],['1 <= len(blocks) <= 1,000; build and split times are positive.','One worker may either build one block or spend split time becoming two workers; parallel actions finish when the slower branch finishes.','Return the least elapsed time to finish every block.'],[([[1],1],'One worker builds the only block in one unit.'),([[1,2],5],'Splitting takes five units, then parallel builds take two more, totaling seven.')],[[b,s] for b,s in [([1],2),([1,2],5),([1,2,3],1),([5,5],2),([1,1,1,1],1),([10,4,5],2),([7,2,9],3),([2,3,7,8],4),([20,1,1],2),([3,6,9,12],1),([8,8,8],8),([1,4,16,20],3),([2,2,3,3,9],2),([100,20],10)]],BUILD,[BUILD.replace('heappop(work);heappush','heappush'),BUILD.replace('+split','+2*split')],['Keeps both smallest jobs after combining and overcounts workers.','Charges twice the split duration at every merge.'],build_oracle,random_build,['A split creates the two branches of a parallel schedule.','Combine the two quickest remaining jobs because delaying either cannot improve the maximum finish time.','Min-heap jobs; remove the smallest, add split to the next smallest, and reinsert it.','This is the reverse construction of an optimal binary worker tree; the final heap value is its makespan.'],'O(n log n)','O(n)',8),
1365:entry('count_smaller_numbers',[('nums','list[int]')],'list[int]',['arrays','sorting','binary search'],['2 <= len(nums) <= 500; 0 <= nums[i] <= 100.','For each position, count other elements whose value is strictly smaller.','Return counts in original order; equal values do not count one another.'],[([[8,1,2,2,3]],'The values have respectively 4, 0, 1, 1, and 3 smaller elements.'),([[6,5,4,8]],'The sorted ranks produce counts 2, 1, 0, and 3.')],[[x] for x in [[0,1],[1,0],[1,1],[8,1,2,2,3],[6,5,4,8],[7,7,7],[0,100,50],[3,1,2],[2,2,1],[5,4,3,2,1],[1,2,3,4,5],[0,0,1,1],[10,9,10,8],[2,0,2,1]]],SMALLER,[SMALLER.replace('bisect_left','bisect_right'),SMALLER.replace('ordered=sorted(nums)','ordered=list(nums)')],['Counts equal values as smaller.','Binary-searches an unsorted sequence.'],smaller_oracle,random_smaller,['A value’s count is its first position in sorted order.','Sort a copy and use a lower-bound search for every original value.','For x, append bisect_left(sorted_nums,x).','All earlier sorted positions are strictly smaller, and lower bound excludes ties.'],'O(n log n)','O(n)',3),
1698:entry('count_distinct_substrings',[('s','str')],'int',['strings','sets'],['1 <= len(s) <= 500; s contains lowercase English letters.','A substring is a nonempty contiguous slice obtained by trimming a prefix and suffix.','Return the number of different substring values, counting duplicate occurrences once.'],[(['aabbaba'],'Enumerating contiguous slices and deduplicating them leaves 21 values.'),(['aaa'],'The only distinct substrings are a, aa, and aaa.')],[[s] for s in ['a','aa','ab','aaa','abc','aba','abab','abcd','aabbaba','banana','mississippi','aaaaa','abca','abcabc']],DISTINCT,[DISTINCT.replace('range(i+1,len(s)+1)','range(i+1,len(s))'),DISTINCT.replace('s[i:j]','s[i+1:j]')],['Omits every substring ending at the final character.','Drops the first character from every candidate slice.'],distinct_oracle,random_distinct,['Distinctness concerns substring values, not positions.','Insert every nonempty contiguous slice into a set.','Loop start i and exclusive end j>i; return the set size.','Every substring has one such pair of endpoints, and set membership removes repeated occurrences.'],'O(n^3)','O(n^3)',5),
2449:entry('minimum_operations_to_make_similar',[('nums','list[int]'),('target','list[int]')],'int',['arrays','greedy','sorting'],['nums and target have equal length and positive values; a solution is guaranteed.','One operation adds two to one nums element and subtracts two from another.','Reordering is allowed for the final multiset; return the minimum operations.'],[([[8,12,6],[2,14,10]],'Match values by parity; the total transferable distance needs two operations.'),([[1,2,5],[4,1,3]],'After parity-aware matching, one transfer of two makes the multisets equal.')],[[a,b] for a,b in [([1],[1]),([2,4],[4,2]),([8,12,6],[2,14,10]),([1,2,5],[4,1,3]),([4,6],[2,8]),([3,5,7],[1,5,9]),([2,2,6],[4,4,2]),([1,3,2,4],[3,1,4,2]),([10,2,6],[4,8,6]),([7,1,9],[3,7,7]),([2,8,4,6],[6,4,8,2]),([5,5,1],[3,5,3]),([20,10],[14,16]),([1,2,3,4,5],[5,4,3,2,1])]],SIMILAR,[SIMILAR.replace('//4','//2'),SIMILAR.replace('key=lambda x:(x&1,x)','')],['Counts both the increases and decreases as separate operations.','Matches values without preserving parity classes.'],similar_oracle,random_similar,['Adding or subtracting two preserves parity.','Sort odd and even values together by parity, then by magnitude, in both arrays.','Sum absolute matched differences and divide by four.','Each operation contributes two units on a donor and two on a receiver, so the total absolute distance drops by four.'],'O(n log n)','O(n)',8),
2840:entry('can_make_strings_equal',[('s1','str'),('s2','str')],'bool',['strings','hash-maps'],['s1 and s2 have equal length and lowercase letters.','A swap may exchange positions whose index difference is even.','Return whether any sequence of allowed swaps transforms s1 into s2.'],[(['abcdba','cabdab'],'Even positions and odd positions have matching character multisets, so transformation is possible.'),(['abe','bea'],'The parity-position character multisets differ, so no allowed swaps can succeed.')],[[a,b] for a,b in [('a','a'),('ab','ab'),('ab','ba'),('ab','ac'),('abcdba','cabdab'),('abe','bea'),('abcd','cbad'),('abcd','adcb'),('aaaa','aaaa'),('aabb','bbaa'),('abcabc','cbacba'),('xyzy','zyxy'),('abcde','edcba'),('ababab','bababa'),('aaabbb','baaabb')]],PARITY,[PARITY.replace('and Counter(s1[1::2])==Counter(s2[1::2])',''),PARITY.replace('s2[::2]','s2[1::2]')],['Checks only even-index positions.','Compares the even positions of one string with odd positions of the other.'],parity_oracle,random_parity,['An even index difference means both indices have the same parity.','Characters may permute freely within even positions and within odd positions, but cannot cross groups.','Compare the two multisets for each parity.','Equal multisets are necessary and sufficient because arbitrary permutations are generated by swaps within each group.'],'O(n)','O(alphabet)',5),
}
