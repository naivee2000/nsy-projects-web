"""Triplets, tree health, combinatorics, offline queries, and sequence DP."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

MOD=1_000_000_007

def triplet_oracle(args):
    prices,profits=args;best=-1
    for i,j,k in combinations(range(len(prices)),3):
        if prices[i]<prices[j]<prices[k]:best=max(best,profits[i]+profits[j]+profits[k])
    return best
def random_triplet(rng):
    n=rng.randint(3,12);return [[rng.randint(1,20) for _ in range(n)],[rng.randint(1,30) for _ in range(n)]]

def score_oracle(args):
    edges,values=args;n=len(values);graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;order=[0]
    for node in order:
        for child in graph[node]:
            if child!=parent[node]:parent[child]=node;order.append(child)
    leaves=[node for node in range(n) if node and len(graph[node])==1] or [0]
    best=0
    for removed in range(1<<n):
        if all(any(not (removed>>node&1) for node in path_to_root(leaf,parent)) for leaf in leaves):
            best=max(best,sum(value for node,value in enumerate(values) if removed>>node&1))
    return best
def path_to_root(node,parent):
    answer=[]
    while node!=-1:answer.append(node);node=parent[node]
    return answer
def random_score(rng):
    n=rng.randint(1,10);return [[[i,rng.randrange(i)] for i in range(1,n)],[rng.randint(1,15) for _ in range(n)]]

def candies_oracle(args):
    n,limit=args;return sum(1 for a in range(limit+1) for b in range(limit+1) if 0<=n-a-b<=limit)
def random_candies(rng):return [rng.randint(0,30),rng.randint(0,12)]

def spending_oracle(args):
    values=args[0];rows=len(values);cols=len(values[0])
    @lru_cache(None)
    def solve(state):
        bought=sum(state);day=bought+1
        if bought==rows*cols:return 0
        return max(values[row][cols-state[row]-1]*day+solve(state[:row]+(state[row]+1,)+state[row+1:])
                   for row in range(rows) if state[row]<cols)
    return solve((0,)*rows)
def random_spending(rng):
    rows=rng.randint(1,3);cols=rng.randint(1,4)
    return [[sorted([rng.randint(1,30) for _ in range(cols)],reverse=True) for _ in range(rows)]]

def building_oracle(args):
    heights,queries=args;answer=[]
    for first,second in queries:
        start=max(first,second);found=-1
        for index in range(start,len(heights)):
            first_ok=index==first or (index>first and heights[index]>heights[first])
            second_ok=index==second or (index>second and heights[index]>heights[second])
            if first_ok and second_ok:found=index;break
        answer.append(found)
    return answer
def random_building(rng):
    n=rng.randint(1,18);return [[rng.randint(1,30) for _ in range(n)],[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,20))]]

def complete_oracle(args):
    word,k=args;answer=0
    for left in range(len(word)):
        counts=Counter()
        for right in range(left,len(word)):
            if right>left and abs(ord(word[right])-ord(word[right-1]))>2:break
            counts[word[right]]+=1
            if all(count==k for count in counts.values()):answer+=1
    return answer
def random_complete(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,18))),rng.randint(1,4)]

def partitions_oracle(args):
    nums=args[0];answer=0
    for cuts in range(1<<(len(nums)-1)):
        group={};valid=True;part=0
        for index,value in enumerate(nums):
            if value in group and group[value]!=part:valid=False;break
            group[value]=part
            if index<len(nums)-1 and cuts>>index&1:part+=1
        answer+=valid
    return answer%MOD
def random_partitions(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,12))]]

def palindrome(value):return str(value)==str(value)[::-1]
def equalindromic_oracle(args):
    nums=args[0];upper=max(nums)+300
    return min(sum(abs(value-target) for value in nums) for target in range(1,upper+1) if palindrome(target))
def random_equalindromic(rng):return [[rng.randint(1,300) for _ in range(rng.randint(1,15))]]

def fruits_oracle(args):
    prices=args[0];n=len(prices)
    @lru_cache(None)
    def solve(index):
        if index>=n:return 0
        return prices[index]+min(solve(next_index) for next_index in range(index+1,2*index+3))
    return solve(0)
def random_fruits(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,18))]]

def incremovable_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            remaining=nums[:left]+nums[right+1:]
            answer+=all(a<b for a,b in zip(remaining,remaining[1:]))
    return answer
def random_incremovable(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,22))]]

TRIPLET='''def maximum_profitable_triplet(prices,profits):
    answer=-1
    for middle in range(len(prices)):
        left=max((profits[i] for i in range(middle) if prices[i]<prices[middle]),default=0)
        right=max((profits[i] for i in range(middle+1,len(prices)) if prices[middle]<prices[i]),default=0)
        if left and right:answer=max(answer,left+profits[middle]+right)
    return answer
'''
SCORE='''def maximum_healthy_tree_score(edges,values):
    graph=[[] for _ in values]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    def retained(node,parent):
        children=[child for child in graph[node] if child!=parent]
        if not children:return values[node]
        return min(values[node],sum(retained(child,node) for child in children))
    return sum(values)-retained(0,-1)
'''
CANDIES='''def bounded_candy_distributions(n,limit):
    from math import comb
    def choose_two(value):return comb(value,2) if value>=2 else 0
    return (choose_two(n+2)-3*choose_two(n-limit+1)+3*choose_two(n-2*limit)-choose_two(n-3*limit-1))
'''
SPENDING='''def maximum_item_spending(values):
    import heapq
    columns=len(values[0]);heap=[(row[-1],index,columns-1) for index,row in enumerate(values)];heapq.heapify(heap)
    answer=0;day=0
    while heap:
        value,row,column=heapq.heappop(heap);day+=1;answer+=day*value
        if column:heapq.heappush(heap,(values[row][column-1],row,column-1))
    return answer
'''
BUILDING='''def leftmost_meeting_buildings(heights,queries):
    n=len(heights);tree=[0]*(4*n)
    def build(node,left,right):
        if left==right:tree[node]=heights[left];return
        middle=(left+right)//2;build(node*2,left,middle);build(node*2+1,middle+1,right);tree[node]=max(tree[node*2],tree[node*2+1])
    def first_greater(node,left,right,start,threshold):
        if right<start or tree[node]<=threshold:return -1
        if left==right:return left
        middle=(left+right)//2;found=first_greater(node*2,left,middle,start,threshold)
        return found if found>=0 else first_greater(node*2+1,middle+1,right,start,threshold)
    build(1,0,n-1);answer=[]
    for first,second in queries:
        if first>second:first,second=second,first
        if first==second or heights[first]<heights[second]:answer.append(second)
        else:answer.append(first_greater(1,0,n-1,second+1,heights[first]))
    return answer
'''
COMPLETE='''def count_complete_substrings(word,k):
    from collections import Counter
    def segment_count(text):
        answer=0
        for kinds in range(1,27):
            width=k*kinds
            if width>len(text):break
            counts=Counter(text[:width]);answer+=len(counts)==kinds and all(value==k for value in counts.values())
            for right in range(width,len(text)):
                outgoing=text[right-width];counts[outgoing]-=1
                if counts[outgoing]==0:del counts[outgoing]
                counts[text[right]]+=1
                answer+=len(counts)==kinds and all(value==k for value in counts.values())
        return answer
    answer=0;start=0
    for index in range(1,len(word)+1):
        if index==len(word) or abs(ord(word[index])-ord(word[index-1]))>2:
            answer+=segment_count(word[start:index]);start=index
    return answer
'''
PARTITIONS='''def count_good_partitions(nums):
    last={value:index for index,value in enumerate(nums)};end=0;blocks=0
    for index,value in enumerate(nums):
        end=max(end,last[value])
        if index==end:blocks+=1
    return pow(2,blocks-1,1_000_000_007)
'''
EQUAL='''def minimum_equalindromic_cost(nums):
    from bisect import bisect_left
    palindromes=[]
    for half in range(1,100000):
        text=str(half);palindromes.append(int(text+text[-2::-1]));palindromes.append(int(text+text[::-1]))
    palindromes=sorted(set(palindromes));median=sorted(nums)[len(nums)//2];place=bisect_left(palindromes,median)
    return min(sum(abs(value-palindromes[i]) for value in nums) for i in range(max(0,place-1),min(len(palindromes),place+2)))
'''
FRUITS='''def minimum_fruit_coins(prices):
    n=len(prices);dp=[0]*(n+1)
    for index in range(n-1,-1,-1):dp[index]=prices[index]+min(dp[min(next_index,n)] for next_index in range(index+1,2*index+3))
    return dp[0]
'''
INCREMOVABLE='''def count_incremovable_subarrays(nums):
    n=len(nums);left=0
    while left+1<n and nums[left]<nums[left+1]:left+=1
    if left==n-1:return n*(n+1)//2
    answer=left+2;right=n-1
    while right:
        while left>=0 and nums[left]>=nums[right]:left-=1
        answer+=left+2
        if nums[right-1]>=nums[right]:break
        right-=1
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
CASES={
2907:[[p,v] for p,v in [([10,2,3,4],[100,2,7,10]),([1,2,3,4,5],[1,2,3,4,5]),([3,2,1],[5,6,7]),([1,3,2],[10,20,30]),([2,1,3],[5,100,6]),([1,2,1,3],[4,5,6,7]),([5,1,4,2,6],[9,8,7,6,5]),([1,1,2,3],[10,20,30,40]),([4,2,5,3,6],[1,10,2,20,3]),([1,4,2,5,3,6],[3,1,4,1,5,9]),([9,8,7,10,11],[5,5,5,5,5]),([2,4,6],[100,1,100]),([3,1,2,5,4],[8,7,6,5,4]),([1,5,2,6,3,7],[10,1,20,2,30,3])]],
2925:[[e,v] for e,v in [([[0,1],[0,2],[0,3],[2,4],[4,5]],[5,2,5,2,1,1]),([[0,1],[0,2],[0,3],[2,4],[2,5]],[5,2,5,2,1,1]),([],[5]),([[0,1]],[1,2]),([[0,1],[1,2]],[1,2,3]),([[0,1],[0,2]],[10,1,1]),([[0,1],[0,2]],[1,10,10]),([[0,1],[1,2],[2,3]],[4,3,2,1]),([[0,1],[0,2],[1,3],[1,4]],[3,1,4,1,5]),([[0,1],[0,2],[2,3]],[5,5,5,5]),([[0,1],[1,2],[1,3],[3,4]],[2,7,1,8,2]),([[0,1],[0,2],[0,3]],[1,2,3,4]),([[0,1],[1,2],[2,3],[3,4]],[1,1,1,1,1]),([[0,1],[0,2],[2,3],[2,4]],[9,2,6,5,3])]],
2927:[[n,l] for n,l in [(5,2),(3,3),(0,0),(1,1),(2,1),(3,1),(6,2),(7,2),(9,3),(4,10),(10,4),(15,5),(20,6),(2,0)]],
2931:[[x] for x in ([[8,5,2],[6,4,1],[9,7,3]],[[10,8,6,4,2],[9,7,5,3,2]],[[1]],[[2,1]],[[3],[2],[1]],[[5,4],[3,1]],[[10,1],[9,2]],[[7,6,5],[4,3,2]],[[9,8],[7,6],[5,4]],[[100,50,1]],[[6,3,2],[5,4,1]],[[8,7,2],[9,5,1]],[[4,3],[4,3]],[[20,10,5],[18,12,1]])],
2940:[[h,q] for h,q in [([6,4,8,5,2,7],[[0,1],[0,3],[2,4],[3,4],[2,2]]),([5,3,8,2,6,1,4,6],[[0,7],[3,5],[5,2],[3,0],[1,6]]),([1],[[0,0]]),([1,2],[[0,1]]),([2,1],[[0,1]]),([3,1,2],[[0,1],[1,2]]),([1,3,2,4],[[0,2],[1,2]]),([5,4,3,2,1],[[0,4],[2,3]]),([1,2,3,4,5],[[0,4],[3,1]]),([2,2,3],[[0,1],[0,2]]),([10,1,9,2,8],[[0,1],[1,3],[2,4]]),([4,1,5,2,6],[[0,1],[1,3]]),([7,3,5,8,2,9],[[1,2],[0,4]]),([3,6,1,7,2,8],[[0,2],[1,4]])]],
2953:[[w,k] for w,k in [('igigee',2),('aaabbbccc',3),('a',1),('a',2),('ab',1),('ac',1),('ad',1),('abcabc',1),('aabb',2),('zzzz',2),('abcdef',1),('abccba',1),('eeefff',3),('abcddcba',2)]],
2963:[[x] for x in ([1,2,3,4],[1,1,1,1],[1,2,1,3],[1],[1,2],[1,2,1],[1,2,3,1,2,3],[1,2,2,3,3],[3,1,2,3,4],[1,2,3,2,4],[5,4,3,2,1],[1,1,2,3,3,4],[1,2,1,2,3,4],[7,8,7,9,10])],
2967:[[x] for x in ([1,2,3,4,5],[10,12,13,14,15],[1],[9,10],[99,100,101],[5,5,5],[1,100],[120,130,140],[88,90,92],[200,250,300],[11,22,33],[7,17,27,37],[101,102,103],[50,60,70,80])],
2969:[[x] for x in ([3,1,2],[1,10,1,1],[1],[5,1],[5,4,3],[1,2,3,4],[10,1,10,1,10],[2,2,2,2],[9,8,7,6,5],[1,100,1,100,1],[4,3,2,1,5,6],[20,1,2,20,1,2],[7,3,9,2,8],[5,10,5,10,5,10])],
2972:[[x] for x in ([1,2,3,4],[6,5,7,8],[8,7,6,6],[1],[2,1],[1,2],[1,1],[1,3,2],[3,1,2],[1,2,1,3],[5,4,3,2,1],[1,5,2,3,4],[2,3,4,1,5],[1,2,5,3,4,6])],
}

BATCH={
2907:entry('maximum_profitable_triplet',[('prices','list[int]'),('profits','list[int]')],'int',['arrays','dynamic programming'],['Choose indices i<j<k with strictly increasing prices.','Return the maximum sum of their profits, or -1 when no such triplet exists.'],[([[10,2,3,4],[100,2,7,10]],'Prices two,three,four at indices one,two,three yield profit 2+7+10=19.'),([[1,2,3,4,5],[1,2,3,4,5]],'The last three increasing prices maximize the profit sum at twelve.')],CASES[2907][2:],TRIPLET,[TRIPLET.replace('prices[i]<prices[middle]','prices[i]<=prices[middle]'),TRIPLET.replace('middle+1','middle')],['Allows equal prices on the left despite strict increase.','Allows the middle index to be reused as the right member.'],triplet_oracle,random_triplet,lesson('Fixing the middle separates the choices into independent left and right maxima.','For each middle, find the best earlier lower-price profit and later higher-price profit.','Combine both maxima with the middle profit when each exists.','Every legal triplet has one middle and its best outer choices are independent once that middle is fixed.'),'O(n²)','O(1)',5),
2925:entry('maximum_healthy_tree_score',[('edges','list[list[int]]'),('values','list[int]')],'int',['trees','dynamic programming','depth-first search'],['Collecting a node adds its value to the score and sets that node value to zero.','After operations, every root-to-leaf path must retain at least one nonzero node; maximize score.'],[([[[0,1],[0,2],[0,3],[2,4],[4,5]],[5,2,5,2,1,1]],'The optimal healthy selection collects eleven total value.'),([[[0,1],[0,2],[0,3],[2,4],[2,5]],[5,2,5,2,1,1]],'Tree DP chooses the cheaper retained protection at each internal node.')],CASES[2925][2:],SCORE,[SCORE.replace('min(values[node],sum','max(values[node],sum'),SCORE.replace('return sum(values)-retained(0,-1)','return retained(0,-1)')],['Retains the more expensive of a node or all child protections.','Returns the minimum retained value rather than the collectible score.'],score_oracle,random_score,lesson('Maximizing collected score equals minimizing value that must remain to protect every root-leaf path.','At a leaf its value must remain; internally retain either this node or enough protection in every child subtree.','Return min(node value, sum child retained costs), then subtract root cost from total.','Those are the only two ways every descendant leaf path can retain a nonzero node.'),'O(n)','O(n)',5),
2927:entry('bounded_candy_distributions',[('n','int'),('limit','int')],'int',['combinatorics','inclusion exclusion'],['Distribute exactly n identical candies among three children.','Each child receives at most limit candies; return the number of ordered distributions.'],[([5,2],'Only permutations of 1,2,2 are valid, giving three distributions.'),([3,3],'All ten unrestricted distributions already respect the limit.')],CASES[2927][2:],CANDIES,[CANDIES.replace('-3*choose_two','-2*choose_two'),CANDIES.replace('+3*choose_two','+2*choose_two')],['Subtracts only two choices for which child exceeds the limit.','Adds back only two pairwise intersections instead of three.'],candies_oracle,random_candies,lesson('Start with all nonnegative solutions and exclude children exceeding the limit.','Apply inclusion-exclusion to three identical upper-bound violations.','Use C(total+2,2), subtract three shifted counts, add three double intersections, subtract the triple intersection.','Shifting an over-limit child by limit+1 bijects violations with an unrestricted smaller-sum distribution.'),'O(1)','O(1)',8),
2931:entry('maximum_item_spending',[('values','list[list[int]]')],'int',['heaps','greedy','sorting'],['Each shop row is nonincreasing; only its rightmost remaining item may be bought.','Exactly one item is bought per day and costs day times value; maximize total spending.'],[([[[8,5,2],[6,4,1],[9,7,3]]],'Buying currently cheapest available items first reserves large values for later multipliers, totaling 285.'),([[[10,8,6,4,2],[9,7,5,3,2]]],'A min-heap merges the accessible row suffixes in globally increasing order.')],CASES[2931][2:],SPENDING,[SPENDING.replace('heapq.heappop','heapq.heappop',1).replace('answer+=day*value','answer+=value'),SPENDING.replace('heapq.heapify(heap)','heap.sort(reverse=True)')],['Ignores the increasing day multiplier.','Sorts the initial heap descending, violating min-heap extraction order.'],spending_oracle,random_spending,lesson('Larger values should receive later, larger day multipliers whenever access constraints allow.','Put each row’s accessible rightmost item in a min-heap and reveal its left neighbor after purchase.','Pop the smallest available value each day and multiply by the day number.','An exchange argument moves any smaller accessible purchase earlier without decreasing later opportunities or total spending.'),'O(items log rows)','O(rows)',8),
2940:entry('leftmost_meeting_buildings',[('heights','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','segment tree','binary search'],['From building i a person may move only right to a strictly taller building.','For each pair, return the leftmost building both can reach, or -1.'],[([CASES[2940][0][0],CASES[2940][0][1]],'Direct reachability and later first-taller searches produce 2,5,-1,5,2.'),([CASES[2940][1][0],CASES[2940][1][1]],'Each query is resolved by the later start or the first later height above both starts.')],CASES[2940][2:],BUILDING,[BUILDING.replace('tree[node]<=threshold','tree[node]<threshold'),BUILDING.replace('second+1','second')],['Accepts equal-height buildings despite the strictly taller move rule.','Searches from the later starting building and can return it when direct reachability failed.'],building_oracle,random_building,lesson('After ordering starts a<=b, b is immediate only when a=b or height[a]<height[b].','Otherwise find the first index after b whose height exceeds height[a].','Build a range-maximum tree and descend left-first while pruning ranges whose maximum is too small.','The direct cases are necessary and sufficient at b; the pruned left-first search returns the earliest later common destination.'),'O((n+q) log n)','O(n)',8),
2953:entry('count_complete_substrings',[('word','str'),('k','int')],'int',['strings','sliding window','counting'],['A complete substring has every distinct character exactly k times.','Every adjacent character pair in it differs by at most two alphabet positions; count all complete substrings.'],[(['igigee',2],'Three substrings satisfy both exact frequencies and the adjacent-letter distance rule.'),(['aaabbbccc',3],'Each constant block and compatible combined blocks are checked by frequency windows.')],CASES[2953][2:],COMPLETE,[COMPLETE.replace('>2','>=2'),COMPLETE.replace('all(value==k','all(value>=k')],['Splits segments when adjacent letters differ exactly two, although that step is allowed.','Accepts character counts above k rather than exactly k.'],complete_oracle,random_complete,lesson('The adjacency rule partitions the word into independent maximal segments.','Within one segment, a complete substring with d distinct letters has fixed length d*k.','For every d from one to 26, slide that width and test exact counts; sum across segments.','Every valid substring lies wholly in one segment and appears in exactly the window size matching its distinct-character count.'),'O(26n)','O(alphabet)',8),
2963:entry('count_good_partitions',[('nums','list[int]')],'int',['arrays','hash maps','greedy'],['Partition nums into contiguous nonempty groups so every distinct value occurs in only one group.','Return the number of valid partitions modulo 1,000,000,007.'],[([[1,2,3,4]],'Every one of three gaps is independently cut or kept, giving eight partitions.'),([[1,1,1,1]],'All occurrences must remain together, so only one partition is valid.')],CASES[2963][2:],PARTITIONS,[PARTITIONS.replace('last={value:index','last={value:0'),PARTITIONS.replace('blocks-1','blocks')],['Records every last occurrence as zero and permits cuts through repeated-value spans.','Treats the final array boundary as an optional cut and doubles the count.'],partitions_oracle,random_partitions,lesson('A cut is legal only after every value seen in the current block has reached its last occurrence.','Track the farthest last occurrence while scanning.','Each index reaching that frontier closes one forced atomic block; choose cuts between adjacent blocks.','Values cannot cross atomic boundaries, while any subset of the block gaps is valid, giving 2^(blocks-1).'),'O(n)','O(n)',8),
2967:entry('minimum_equalindromic_cost',[('nums','list[int]')],'int',['arrays','medians','enumeration'],['Choose one positive palindromic integer target.','Return the minimum sum of absolute changes needed to make every nums value equal to that target.'],[([[1,2,3,4,5]],'Target three is palindromic and gives total cost six.'),([[10,12,13,14,15]],'The best palindromic target near the median minimizes total absolute distance.')],CASES[2967][2:],EQUAL,[EQUAL.replace('len(nums)//2','0'),EQUAL.replace('place-1','place+1')],['Searches near the smallest value instead of the median.','Skips palindromes immediately below the insertion point.'],equalindromic_oracle,random_equalindromic,lesson('Without the palindrome restriction, absolute distance is minimized at a median.','Generate palindromes and check the nearest candidates around the median.','Binary-search the median in the sorted palindrome list and evaluate neighboring targets.','The convex absolute-distance objective cannot improve after moving past the closest feasible target on either side.'),'O(P log P+n log n)','O(P+n)',5),
2969:entry('minimum_fruit_coins',[('prices','list[int]')],'int',['arrays','dynamic programming','monotonic queue'],['Buying fruit i (one-indexed) grants the next i fruits for free, though a free fruit may still be bought to extend benefits.','Return the minimum coins needed to acquire every fruit.'],[([[3,1,2]],'Buy the first fruit for three and the second for one to cover all fruits, totaling four.'),([[1,10,1,1]],'Strategic purchases of free fruits extend coverage at minimum total cost.')],CASES[2969][2:],FRUITS,[FRUITS.replace('2*index+3','2*index+2'),FRUITS.replace('prices[index]+','')],['Allows one fewer next purchase choice and can miss the cheapest extension.','Treats every paid fruit as free by omitting its price.'],fruits_oracle,random_fruits,lesson('After buying index i, the next paid fruit may be any position through 2i+2 in zero-based indexing.','Compute minimum remaining cost backward over those reachable next purchase positions.','dp[i]=price[i]+min(dp[j]) for j in i+1..2i+2, with out-of-range dp zero.','Choosing j also acquires all intervening fruits for free; every valid purchasing plan has exactly one such next paid position.'),'O(n²)','O(n)',8),
2972:entry('count_incremovable_subarrays',[('nums','list[int]')],'int',['arrays','two pointers'],['Remove one nonempty contiguous subarray.','Count removals leaving the remaining elements strictly increasing; an empty remainder is increasing.'],[([[1,2,3,4]],'Every one of ten nonempty subarrays can be removed while the remainder stays increasing.'),([[6,5,7,8]],'Only removals that eliminate the initial inversion and preserve the suffix qualify.')],CASES[2972][2:],INCREMOVABLE,[INCREMOVABLE.replace('nums[left]<nums[left+1]','nums[left]<=nums[left+1]'),INCREMOVABLE.replace('left+2','left+1')],['Treats equal adjacent values as strictly increasing.','Undercounts the possible removed-prefix boundary by one.'],incremovable_oracle,random_incremovable,lesson('The kept prefix and suffix must each be strictly increasing and their boundary values must join in order.','Find the maximal increasing prefix, then scan an increasing suffix while moving the prefix pointer left until it fits.','For each suffix start add prefix choices plus the empty prefix; stop when the suffix ceases increasing.','Both pointers move only left, and every valid removal is uniquely identified by its kept prefix end and suffix start.'),'O(n)','O(1)',8),
}

BATCH[2907]['wrong'][1]='''def maximum_profitable_triplet(prices,profits):
    answer=-1
    for i in range(len(prices)):
        for j in range(i+1,len(prices)):
            for k in range(j+1,len(prices)):
                if prices[i]<prices[j]<=prices[k]:answer=max(answer,profits[i]+profits[j]+profits[k])
    return answer
'''
BATCH[2907]['wrong_reasons'][1]='Allows the final price to equal the middle price even though all three prices must increase strictly.'
BATCH[2907]['wrong'][1]='''def maximum_profitable_triplet(prices,profits):
    answer=-1
    for i in range(len(prices)):
        for j in range(len(prices)):
            for k in range(len(prices)):
                if prices[i]<prices[j]<prices[k]:answer=max(answer,profits[i]+profits[j]+profits[k])
    return answer
'''
BATCH[2907]['wrong_reasons'][1]='Chooses strictly increasing prices but ignores the required increasing index order.'
BATCH[2940]['wrong']=[
    '''def leftmost_meeting_buildings(heights,queries):
    return [max(first,second) for first,second in queries]
''',
    '''def leftmost_meeting_buildings(heights,queries):
    answer=[]
    for first,second in queries:
        if first>second:first,second=second,first
        answer.append(second if first==second or heights[first]<heights[second] else -1)
    return answer
''',
]
BATCH[2940]['wrong_reasons']=[
    'Assumes the later starting building is always reachable by both people.',
    'Handles only direct meetings and never searches for a later building taller than both starts.',
]
BATCH[2953]['wrong'][1]='''def count_complete_substrings(word,k):
    from collections import Counter
    answer=0
    for left in range(len(word)):
        counts=Counter()
        for right in range(left,len(word)):
            counts[word[right]]+=1
            answer+=all(value==k for value in counts.values())
    return answer
'''
BATCH[2953]['wrong_reasons'][1]='Checks exact frequencies but ignores the adjacent-letter distance restriction.'
BATCH[2967]['reference']='''def minimum_equalindromic_cost(nums):
    ordered=sorted(nums);median=ordered[len(ordered)//2];text=str(median);half=(len(text)+1)//2;prefix=int(text[:half])
    candidates={10**(len(text)-1)-1,10**len(text)+1}
    for value in range(max(1,prefix-2),prefix+3):
        first=str(value);tail=first[:-1] if len(text)%2 else first
        candidates.add(int(first+tail[::-1]))
    return min(sum(abs(number-target) for number in nums) for target in candidates if target>0)
'''
BATCH[2972]['wrong'][0]='''def count_incremovable_subarrays(nums):
    return len(nums)*(len(nums)+1)//2
'''
BATCH[2972]['wrong_reasons'][0]='Assumes every removal works, which is true only when the original array is already strictly increasing.'
