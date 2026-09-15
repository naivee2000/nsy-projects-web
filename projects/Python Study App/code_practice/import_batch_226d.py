"""Pair deletions, active trades, convex-hull partitioning, range trades, and palindrome concatenation."""
from functools import lru_cache

from .import_batch_055 import entry


def score_oracle(args):
    @lru_cache(None)
    def solve(values):
        if len(values)<=2:return 0
        return max(values[0]+values[1]+solve(values[2:]),values[-2]+values[-1]+solve(values[:-2]),values[0]+values[-1]+solve(values[1:-1]))
    return solve(tuple(args[0]))


def random_score(rng):return [[rng.randint(-10,20) for _ in range(rng.randint(3,10))]]


def trade_best(text):
    best=text.count('1');augmented='1'+text+'1';n=len(augmented)
    for left in range(1,n-1):
        if augmented[left]!='1' or augmented[left-1]!='0':continue
        right=left
        while right+1<n and augmented[right+1]=='1':right+=1
        if right+1>=n or augmented[right+1]!='0':continue
        first=augmented[:left]+'0'*(right-left+1)+augmented[right+1:]
        for a in range(1,n-1):
            if first[a]!='0' or first[a-1]!='1':continue
            b=a
            while b+1<n and first[b+1]=='0':b+=1
            if b+1<n and first[b+1]=='1':best=max(best,(first[:a]+'1'*(b-a+1)+first[b+1:])[1:-1].count('1'))
    return best


def trade_oracle(args):return trade_best(args[0])
def random_trade(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,14)))]


def divide_oracle(args):
    nums,cost,k=args;n=len(nums);pnums=[0];pcost=[0]
    for value in nums:pnums.append(pnums[-1]+value)
    for value in cost:pcost.append(pcost[-1]+value)
    @lru_cache(None)
    def solve(start,order):
        if start==n:return 0
        return min((pnums[end]+k*order)*(pcost[end]-pcost[start])+solve(end,order+1) for end in range(start+1,n+1))
    return solve(0,1)


def random_divide(rng):
    n=rng.randint(1,9);return [[rng.randint(1,9) for _ in range(n)],[rng.randint(1,9) for _ in range(n)],rng.randint(1,8)]


def range_trade_oracle(args):
    text,queries=args;total=text.count('1');return [total-text[left:right+1].count('1')+trade_best(text[left:right+1]) for left,right in queries]


def random_range_trade(rng):
    n=rng.randint(1,14);text=''.join(rng.choice('01') for _ in range(n));queries=[]
    for _ in range(rng.randint(1,10)):
        left=rng.randrange(n);queries.append([left,rng.randint(left,n-1)])
    return [text,queries]


def palindrome_oracle(args):
    first,second=args;answer=0
    for left in range(len(first)+1):
        for right in range(left,len(first)+1):
            for a in range(len(second)+1):
                for b in range(a,len(second)+1):
                    candidate=first[left:right]+second[a:b]
                    if candidate==candidate[::-1]:answer=max(answer,len(candidate))
    return answer


def random_palindrome(rng):
    return [''.join(rng.choice('abc') for _ in range(rng.randint(1,8))),''.join(rng.choice('abc') for _ in range(rng.randint(1,8)))]


SCORE='''def maximum_pair_deletion_score(nums):
    total=sum(nums)
    if len(nums)%2:return total-min(nums)
    return total-min(nums[index]+nums[index+1] for index in range(len(nums)-1))
'''

TRADE='''def maximum_active_after_one_trade(s):
    active=s.count('1');previous=None;gain=0;index=0
    while index<len(s):
        end=index+1
        while end<len(s) and s[end]==s[index]:end+=1
        if s[index]=='0':
            length=end-index
            if previous is not None:gain=max(gain,previous+length)
            previous=length
        index=end
    return active+gain
'''

DIVIDE='''def minimum_division_cost(nums,cost,k):
    from collections import deque
    prefix_nums=[0];prefix_cost=[0]
    for value in nums:prefix_nums.append(prefix_nums[-1]+value)
    for value in cost:prefix_cost.append(prefix_cost[-1]+value)
    total_cost=prefix_cost[-1];lines=deque([(0,0)])
    def value(line,x):return line[0]*x+line[1]
    def add(line):
        while len(lines)>=2:
            first,second=lines[-2],lines[-1]
            if (second[1]-first[1])*(second[0]-line[0])<(line[1]-second[1])*(first[0]-second[0]):break
            lines.pop()
        lines.append(line)
    dp=0
    for index in range(1,len(nums)+1):
        x=prefix_nums[index]+k
        while len(lines)>=2 and value(lines[0],x)>=value(lines[1],x):lines.popleft()
        dp=prefix_nums[index]*prefix_cost[index]+k*total_cost+value(lines[0],x)
        add((-prefix_cost[index],dp))
    return dp
'''

RANGE_TRADE='''def maximum_active_for_substring_trades(s,queries):
    active=s.count('1');n=len(s);zero_runs=[];run_index=[-1]*n
    for index,char in enumerate(s):
        if char=='0':
            if index and s[index-1]=='0':zero_runs[-1][1]+=1
            else:zero_runs.append([index,1])
        run_index[index]=len(zero_runs)-1
    pair_values=[zero_runs[i][1]+zero_runs[i+1][1] for i in range(len(zero_runs)-1)]
    logs=(len(pair_values)).bit_length();table=[pair_values]
    for level in range(1,logs):
        width=1<<(level-1);previous=table[-1];table.append([max(previous[i],previous[i+width]) for i in range(len(previous)-width)])
    def maximum(left,right):
        if left>right:return 0
        level=(right-left+1).bit_length()-1;width=1<<level
        return max(table[level][left],table[level][right-width+1])
    answer=[]
    for left,right in queries:
        left_run,right_run=run_index[left],run_index[right]
        left_count=-1 if left_run<0 else zero_runs[left_run][1]-(left-zero_runs[left_run][0])
        right_count=-1 if right_run<0 else right-zero_runs[right_run][0]+1
        start=left_run+1;end=right_run-(s[right]=='0');best=active
        if start<end:best=max(best,active+maximum(start,end-1))
        if s[left]=='0' and s[right]=='0' and left_run+1==right_run:best=max(best,active+left_count+right_count)
        if s[left]=='0' and left_run+1<right_run+(s[right]=='1'):best=max(best,active+left_count+zero_runs[left_run+1][1])
        if s[right]=='0' and left_run<right_run-1:best=max(best,active+right_count+zero_runs[right_run-1][1])
        answer.append(best)
    return answer
'''

PALINDROME='''def longest_substring_concatenation_palindrome(s,t):
    def starts(text):
        result=[0]*len(text)
        for center in range(len(text)):
            for left,right in ((center,center),(center,center+1)):
                while left>=0 and right<len(text) and text[left]==text[right]:result[left]=max(result[left],right-left+1);left-=1;right+=1
        return result
    reversed_t=t[::-1];first=starts(s);second=starts(reversed_t);answer=max(first+second);matches=[[0]*(len(reversed_t)+1) for _ in range(len(s)+1)]
    for i,char in enumerate(s,1):
        for j,other in enumerate(reversed_t,1):
            if char==other:
                matches[i][j]=matches[i-1][j-1]+1;paired=2*matches[i][j]
                answer=max(answer,paired+(first[i] if i<len(s) else 0),paired+(second[j] if j<len(reversed_t) else 0))
    return answer
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


SCORE_CASES=[[[value for value in nums]] for nums in [[2,4,1],[1,2,3,4],[1,2,3],[5,5,5,5],[10,1,1,10],[-1,5,2],[9,8,7,6,5],[1,100,1,100,1,100],[0,0,0],[-5,-2,-3,-4],[3,1,4,1,5,9],[20,-10,2,-1,8],[7,6,5,4,3,2,1],[2,9,-3,8,-4,7]]]
TRADE_CASES=[[text] for text in ['01','1','0','111','000','010','101','00100','110011','01010','10001','0011100','10100101','0001000']]
DIVIDE_CASES=[[nums,cost,k] for nums,cost,k in [([3,1,4],[4,6,6],1),([4,8,5,1,14,2,2,12,1],[7,2,8,4,2,2,1,1,2],7),([1],[1],1),([5],[3],2),([1,2],[3,4],1),([2,1],[1,2],5),([1,1,1],[1,1,1],1),([9,1,9],[2,8,2],3),([3,5,2,6],[4,1,7,2],2),([10,2,3],[1,9,5],4),([2,7,1,8,2],[3,1,4,1,5],6),([5,4,3,2,1],[1,2,3,4,5],2),([6,1,6,1],[8,2,8,2],5),([1,3,3,7,2,4],[2,1,5,3,2,6],3)]]
RANGE_CASES=[[text,queries] for text,queries in [('01',[[0,1]]),('1',[[0,0]]),('0',[[0,0]]),('010',[[0,2],[1,1]]),('10101',[[0,4],[1,3]]),('001100',[[0,5],[1,4]]),('110011',[[0,5],[2,5]]),('0001000',[[0,6],[1,5],[3,3]]),('10100101',[[0,7],[2,6],[1,4]]),('111000111',[[0,8],[2,6]]),('0101010',[[0,6],[1,5],[2,4]]),('00101100',[[0,7],[1,6]]),('100001',[[0,5],[1,4]]),('0110100110',[[0,9],[2,8],[4,7]])]]
PALINDROME_CASES=[[s,t] for s,t in [('a','a'),('abc','def'),('ab','ba'),('aa','bb'),('abc','cba'),('race','car'),('a','b'),('aba','x'),('xyz','zyx'),('abcd','dc'),('banana','ana'),('abca','acba'),('aaaa','a'),('cab','bac')]]


BATCH={
3496:entry('maximum_pair_deletion_score',[('nums','list[int]')],'int',['arrays','greedy'],['nums has at least three integers.','While more than two remain, remove either the first two, last two, or first and last, adding their sum.','Maximize the total score; an odd-length array ends with one element and an even-length array ends with two.'],[([[2,4,1]],'Remove the first two values to score six, leaving one.'),([[1,2,3,4]],'The maximum score equals the total minus the minimum adjacent pair that can remain.')],SCORE_CASES,SCORE,[SCORE.replace('return total-min(nums)','return total-max(nums)'),SCORE.replace('nums[index]+nums[index+1]','nums[0]+nums[-1]')],['For odd length, leaves the maximum rather than minimum value unremoved.','For even length, assumes the two endpoints can remain instead of minimizing over adjacent pairs.'],score_oracle,random_score,lesson('Every operation scores removed values, so maximizing score is minimizing the sum left at termination.','For odd length any single value can remain; for even length the two survivors must be adjacent in the original order.','Subtract the minimum element for odd n, or the minimum adjacent-pair sum for even n, from the total.','Endpoint deletions can expose any chosen valid survivor set, while crossing survivors cannot become the final adjacent pair.'),'O(n)','O(1)',6),
3499:entry('maximum_active_after_one_trade',[('s','str')],'int',['strings','run length encoding','greedy'],['s is a nonempty binary string, conceptually surrounded by inactive-external sentinel ones.','A trade removes a one-run surrounded by zeros, then activates a zero-run surrounded by ones.','Return the maximum active count after at most one trade; sentinels never count.'],[(['01'],'No beneficial complete trade exists, so the single active section remains.'),(['00100'],'Trading the middle one joins and activates both zero runs, producing five active positions.')],TRADE_CASES,TRADE,[TRADE.replace('previous+length','length'),TRADE.replace("if s[index]=='0':","if s[index]=='1':")],['Uses only one adjacent zero run instead of both sides of the removed one-run.','Combines adjacent one runs rather than zero runs.'],trade_oracle,random_trade,lesson('Removing a one-run merges its adjacent zero-runs, and activating that merged run gains exactly their combined lengths.','Run-length encode the string and track consecutive zero-run lengths.','Count existing ones; for each zero run after another zero run, update the best sum of the pair separated by one-run.','Every legal trade corresponds to exactly two adjacent zero runs in the run sequence, and their intervening ones cancel from the net change.'),'O(n)','O(1)',6),
3500:entry('minimum_division_cost',[('nums','list[int]'),('cost','list[int]'),('k','int')],'int',['arrays','dynamic programming','convex hull optimization'],['nums and cost have equal length up to 1,000 and contain positive integers; k is positive.','For partition number q ending at r, cost is (prefix_nums[r]+k*q) times that segment’s cost sum.','Partition the full array into nonempty contiguous subarrays and minimize total cost.'],[([[3,1,4],[4,6,6],1],'Splitting after the second value yields costs fifty and sixty, totaling 110.'),([[1],[1],1],'The sole segment costs (one plus one) times one, giving two.')],DIVIDE_CASES,DIVIDE,[DIVIDE.replace('x=prefix_nums[index]+k','x=prefix_nums[index]'),DIVIDE.replace('add((-prefix_cost[index],dp))','pass')],['Omits the k shift from convex-hull query coordinates and misprices later partitions.','Never adds later boundary lines, effectively forcing the array to remain one segment.'],divide_oracle,random_divide,lesson('The order-dependent k term can be telescoped into a fixed k*total_cost charge per segment boundary.','Rewrite the DP transition as a line minimum with slope -prefix_cost at increasing x=prefix_nums+k.','Query the monotone hull, add prefix_nums*prefix_cost+k*total_cost, then insert the new decreasing-slope line.','Telescoping reproduces every partition index contribution, and monotone slopes/queries make deque convex-hull optimization exact.'),'O(n)','O(n)',8),
3501:entry('maximum_active_for_substring_trades',[('s','str'),('queries','list[list[int]]')],'list[int]',['strings','range queries','sparse tables'],['s is a nonempty binary string and each query is an inclusive substring range.','For each query, trade only within that substring as though it were surrounded by ones; positions outside remain unchanged.','Return the maximum total active count in the whole string after at most one query-local trade.'],[(['01',[[0,1]]],'The query cannot improve the string, so the answer is one.'),(['00100',[[0,4],[1,3]]],'The full range can activate all five positions, while the shorter range uses its clipped boundary zero runs.')],RANGE_CASES,RANGE_TRADE,[RANGE_TRADE.replace('best=active','best=0'),RANGE_TRADE.replace('left_count+right_count','zero_runs[left_run][1]+zero_runs[right_run][1]')],['Returns only the query-local gain and omits active positions outside the range.','Uses full zero-run lengths at query boundaries instead of clipping them to the queried substring.'],range_trade_oracle,random_range_trade,lesson('A query gain is the best sum of two zero runs separated by one-runs, with its first and last zero runs clipped at query boundaries.','Precompute zero runs, adjacent-run sums, and a sparse table for fully contained interior pairs.','For each range, combine the best interior pair with the few boundary pair configurations, then add the unchanged global active count.','Every eligible pair is either wholly interior or touches a clipped boundary, so the constant set of cases plus RMQ is complete.'),'O((n+q) log n)','O(n log n)',8),
3503:entry('longest_substring_concatenation_palindrome',[('s','str'),('t','str')],'int',['strings','dynamic programming','palindromes'],['s and t are nonempty lowercase strings.','Choose a contiguous substring from s and one from t; either may be empty; concatenate them in that order.','Return the maximum possible palindrome length.'],[(['a','a'],'Taking both single letters produces aa of length two.'),(['abc','def'],'No cross-string match exists, but a one-letter substring is palindromic.')],PALINDROME_CASES,PALINDROME,[PALINDROME.replace('reversed_t=t[::-1]','reversed_t=t'),PALINDROME.replace('answer=max(first+second)','answer=0')],['Matches s against t without reversing t and therefore pairs characters in the wrong order.','Ignores palindromes contained entirely within one input string.'],palindrome_oracle,random_palindrome,lesson('A cross-string palindrome has matching outer pieces from s and reversed t, plus an optional palindrome center from either string.','Precompute the longest palindrome starting at every position, then build common-suffix lengths between s and reversed t.','For each matching DP cell, double the paired length and append the best available center immediately afterward on either side.','Every concatenated palindrome decomposes into equal mirrored cross-string arms and at most one within-string center, all represented by these states.'),'O(len(s)*len(t)+len(s)^2+len(t)^2)','O(len(s)*len(t))',6),
}
