"""Wildcard movement, digit-ended subarrays, interval filtering, replacement, and resources."""
from itertools import product
from string import ascii_lowercase
from .import_batch_055 import entry

def distance_oracle(a):
    moves=a[0];best=0
    for replacements in product('UDLR',repeat=moves.count('_')):
        it=iter(replacements);x=y=0
        for c in moves:
            c=next(it) if c=='_' else c;x+=(c=='D')-(c=='U');y+=(c=='R')-(c=='L')
        best=max(best,abs(x)+abs(y))
    return best
def random_distance(r):return [''.join(r.choice('UDLR_') for _ in range(r.randint(1,7)))]
def digit_subarrays_oracle(a):
    nums,x=a;return sum(str(sum(nums[i:j])).startswith(str(x)) and str(sum(nums[i:j])).endswith(str(x)) for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def random_digit_subarrays(r):return [[r.randint(1,50) for _ in range(r.randint(1,12))],r.randint(0,9)]
def interval_oracle(a):
    intervals,lo,hi=a;points={x for l,r in intervals for x in range(l,r+1) if not lo<=x<=hi};out=[]
    for x in sorted(points):
        if out and x==out[-1][1]+1:out[-1][1]=x
        else:out.append([x,x])
    return out
def random_intervals(r):
    values=[]
    for _ in range(r.randint(1,8)):
        x=r.randint(0,20);values.append([x,r.randint(x,25)])
    x=r.randint(0,20);return [values,x,r.randint(x,25)]
def subsequence(x,t):
    it=iter(t);return all(any(c==wanted for c in it) for wanted in x)
def replace_oracle(a):
    s,t=a
    if subsequence(s,t):return True
    return any(subsequence(s[:i]+c+s[i+1:],t) for i in range(len(s)) for c in ascii_lowercase)
def random_replace(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,7))),''.join(r.choice('abc') for _ in range(r.randint(1,10)))]
def resources_oracle(a):
    nums,k=a;current=k;buys=0
    for need in nums:
        while current<need:current+=k;buys+=1
        current-=need
    return buys*(buys+1)//2%(10**9+7)
def random_resources(r):return [[r.randint(1,20) for _ in range(r.randint(1,15))],r.randint(1,10)]

DISTANCE='''def maximum_manhattan_after_wildcards(moves):
    vertical=moves.count('D')-moves.count('U');horizontal=moves.count('R')-moves.count('L')
    return abs(vertical)+abs(horizontal)+moves.count('_')
'''
DIGIT_SUBARRAYS='''def count_digit_ended_subarrays(nums,x):
    answer=0
    for left in range(len(nums)):
        total=0
        for right in range(left,len(nums)):
            total+=nums[right];text=str(total)
            if text[0]==str(x) and text[-1]==str(x):answer+=1
    return answer
'''
INTERVAL='''def filter_occupied_intervals(intervals,free_start,free_end):
    intervals=sorted(intervals);merged=[]
    for left,right in intervals:
        if merged and left<=merged[-1][1]+1:merged[-1][1]=max(merged[-1][1],right)
        else:merged.append([left,right])
    answer=[]
    for left,right in merged:
        if left<free_start:answer.append([left,min(right,free_start-1)])
        if right>free_end:answer.append([max(left,free_end+1),right])
    return answer
'''
INTERVAL_NAMED=INTERVAL.replace('filter_occupied_intervals(intervals,free_start,free_end)','filter_occupied_intervals(occupiedIntervals,freeStart,freeEnd)').replace('intervals=sorted(intervals)','occupiedIntervals=sorted(occupiedIntervals)').replace('in intervals:','in occupiedIntervals:').replace('free_start','freeStart').replace('free_end','freeEnd')
REPLACE='''def subsequence_after_one_replacement(s,t):
    unchanged=changed=0
    for char in t:
        next_changed=changed+(changed<len(s) and s[changed]==char)
        if unchanged<len(s):next_changed=max(next_changed,unchanged+1)
        unchanged+=unchanged<len(s) and s[unchanged]==char
        changed=next_changed
    return changed>=len(s)
'''
RESOURCES='''def minimum_processing_resource_cost(nums,k):
    current=k;operations=0
    for need in nums:
        if current<need:
            added=(need-current+k-1)//k;current+=added*k;operations+=added
        current-=need
    return operations*(operations+1)//2%(10**9+7)
'''

BATCH={
3968:entry('maximum_manhattan_after_wildcards',[('moves','str')],'int',['strings','greedy','geometry'],['Execute U, D, L, and R moves from the origin.','Each underscore may independently become any one move.','Return the greatest possible final Manhattan distance.'],[(['L_D_'],'Choose both wildcards to extend away from the origin, reaching distance four.'),(['UD_'],'The fixed moves cancel and the wildcard reaches distance one.')],[[s] for s in ['_','U','UD','UD_','L_D_','____','UR','ULDR','U__D','RR_L','DDD_','L_R_U','UDLR_','UU__RR']],DISTANCE,[DISTANCE.replace("+moves.count('_')","-moves.count('_')"),DISTANCE.replace("abs(vertical)+abs(horizontal)","abs(vertical+horizontal)")],['Subtracts wildcard moves instead of using them to extend distance.','Combines axes before taking absolute value and loses opposing components.'],distance_oracle,random_distance,['Resolve the fixed moves into vertical and horizontal displacement.','Their current distance is |vertical|+|horizontal|.','Every wildcard can extend a nonzero axis, or choose any direction at the origin.','Therefore each underscore increases the attainable maximum by exactly one.'],'O(n)','O(1)',3),
3969:entry('count_digit_ended_subarrays',[('nums','list[int]'),('x','int')],'int',['arrays','prefix sums','enumeration'],['nums contains positive integers and x is one decimal digit.','A subarray qualifies when the decimal representation of its sum starts and ends with x.','Return the count of nonempty qualifying subarrays.'],[([[1,100,1],1],'The two single-value sums of one and the two different subarrays summing to 101 give four.'),([[2,3],5],'The complete subarray sums to five, which starts and ends with digit five.')],[[a,x] for a,x in [([1],1),([1,100,1],1),([2,3],5),([10],0),([11],1),([5,5],1),([9,1],1),([12,9],2),([1,2,3],3),([20,2],2),([7,7,7],1),([50,50],1),([3,8,10],1),([99,1,1],1)]],DIGIT_SUBARRAYS,[DIGIT_SUBARRAYS.replace("text[0]==str(x) and text[-1]==str(x)","text[0]==str(x) or text[-1]==str(x)"),DIGIT_SUBARRAYS.replace('range(left,len(nums))','range(left,len(nums)-1)')],['Accepts sums matching only one endpoint digit.','Never considers subarrays ending at the final array element.'],digit_subarrays_oracle,random_digit_subarrays,['Fix each left boundary and accumulate sums as the right boundary grows.','Convert each positive sum to decimal text.','Compare both its first and last character with x.','Every nonempty subarray is visited exactly once.'],'O(n^2)','O(1)',5),
3975:entry('filter_occupied_intervals',[('occupiedIntervals','list[list[int]]'),('freeStart','int'),('freeEnd','int')],'list[list[int]]',['arrays','intervals','sorting'],['Occupied intervals contain inclusive integer points.','First merge overlapping or touching intervals, then remove every point in the inclusive free interval.','Return the minimum sorted set of remaining non-touching intervals.'],[([[[2,6],[4,8],[10,10],[10,12],[14,16]],7,11],'Merging then removing 7 through 11 leaves [2,6], [12,12], and [14,16].'),([[[1,5]],1,5],'The free interval removes every occupied point.')],[[a,l,h] for a,l,h in [([[1,5]],1,5),([[1,5]],2,3),([[1,2],[3,4]],10,12),([[2,6],[4,8],[10,10],[10,12],[14,16]],7,11),([[0,0]],1,2),([[1,3],[5,7]],4,4),([[1,10]],0,0),([[1,10]],11,12),([[1,2],[2,3]],2,2),([[5,5],[7,7]],5,7),([[0,4],[6,9]],3,7),([[2,8],[9,10]],4,6),([[1,1],[3,3],[2,2]],2,2),([[10,20],[1,5]],6,9)]],INTERVAL_NAMED,[INTERVAL_NAMED.replace('left<=merged[-1][1]+1','left<=merged[-1][1]'),INTERVAL_NAMED.replace('freeStart-1','freeStart')],['Fails to merge touching integer intervals.','Retains the first supposedly free point on a left remainder.'],interval_oracle,random_intervals,['Sort and merge intervals when the next start is at most previous end plus one.','For each merged interval, retain only portions strictly before and after the free range.','Clip the left remainder at freeStart-1 and the right at freeEnd+1.','Merging before subtraction guarantees the returned pieces are minimal and ordered.'],'O(n log n)','O(n)',5),
3983:entry('subsequence_after_one_replacement',[('s','str'),('t','str')],'bool',['strings','dynamic programming','two pointers'],['You may replace at most one character of s with another lowercase letter.','Characters may not be deleted from s, but the resulting s only needs to be a subsequence of t.','Return whether such a choice exists.'],[(['cat','chat'],'Match c, replace a if needed, and match t along chat, so the result is true.'),(['abcd','ac'],'s is longer than t and cannot become its subsequence.')],[[s,t] for s,t in [('a','a'),('a','b'),('cat','chat'),('abcd','ac'),('abc','abc'),('abc','axc'),('abc','acb'),('aa','ab'),('cab','abc'),('bbb','abbb'),('abc','zzabc'),('abc','ab'),('aba','aca'),('ccc','abcabc')]],REPLACE,[REPLACE.replace('max(next_changed,unchanged+1)','unchanged+1'),REPLACE.replace('changed>=len(s)','unchanged>=len(s)')],['Overwrites progress already made in the replaced state.','Never permits a replacement and checks only the original subsequence.'],replace_oracle,random_replace,['Track the longest prefix matched with zero replacements and with at most one replacement.','At each t character, the changed state may consume it as the one replacement after the unchanged prefix.','Also advance either state on exact character matches.','These two states cover every position where the optional replacement could occur.'],'O(len(t))','O(1)',5),
3987:entry('minimum_processing_resource_cost',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','simulation'],['Start with k resources and process nums from left to right.','Before an item, buy k more resources as often as necessary; the j-th purchase costs j.','After processing, subtract the item requirement, flooring remaining resources at zero. Return minimum total cost modulo 1,000,000,007.'],[([[1,2,3,4],4],'Two purchases are necessary across the sequence and cost one plus two, totaling three.'),([[1],5],'The initial resources cover the item, so no purchase is needed.')],[[a,k] for a,k in [([1],5),([5],5),([6],5),([1,2,3,4],4),([10,1],3),([2,2,2],2),([1,1,1],1),([9,9],4),([3,8,2],5),([20],3),([5,10,15],5),([1,20,1],4),([7,7,7,7],6),([100,1,1],10)]],RESOURCES,[RESOURCES.replace('(need-current+k-1)//k','(need-current)//k'),RESOURCES.replace('operations*(operations+1)','operations*(operations-1)')],['Uses floor division and may buy too few resource blocks.','Starts purchase costs at zero instead of one.'],resources_oracle,random_resources,['When current resources are short, buy the smallest whole number of k-sized blocks that covers the deficit.','Ceiling division computes that count directly.','Only the total number of purchases matters because their costs are 1,2,...','Greedy minimum purchases at each forced deficit gives the global count and triangular cost.'],'O(n)','O(1)',5),
}
