"""Mirror pairing, weighted windows/intervals, fast modes, and robot paths."""
from collections import Counter
from itertools import combinations

from .import_batch_055 import entry

MOD=1_000_000_007


def mirror_oracle(args):
    text=args[0];available=set();answer=0
    for index,char in enumerate(text):
        mirror=chr(219-ord(char));matches=[position for position in available if text[position]==mirror]
        if matches:
            chosen=max(matches);available.remove(chosen);answer+=index-chosen
        else:available.add(index)
    return answer


def random_mirror(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,30)))]


def coins_oracle(args):
    segments,k=args
    low=min(left for left,_,_ in segments)-k;high=max(right for _,right,_ in segments)
    def amount(position):
        return next((coins for left,right,coins in segments if left<=position<=right),0)
    return max(sum(amount(position) for position in range(start,start+k)) for start in range(low,high+1))


def random_coins(rng):
    positions=sorted(rng.sample(range(1,30),rng.randint(1,8)))
    return [[[position,position,rng.randint(1,8)] for position in positions],rng.randint(1,10)]


def intervals_oracle(args):
    intervals=args[0];best_weight=0;best=()
    for size in range(1,min(4,len(intervals))+1):
        for indices in combinations(range(len(intervals)),size):
            ordered=sorted(indices,key=lambda index:intervals[index][0])
            if all(intervals[ordered[i]][1]<intervals[ordered[i+1]][0] for i in range(len(ordered)-1)):
                weight=sum(intervals[index][2] for index in indices);candidate=tuple(sorted(indices))
                if weight>best_weight or (weight==best_weight and candidate<best):best_weight,best=weight,candidate
    return list(best)


def random_intervals(rng):
    result=[]
    for _ in range(rng.randint(1,9)):
        left=rng.randint(1,15);result.append([left,rng.randint(left,min(20,left+5)),rng.randint(1,12)])
    return [result]


def mode_oracle(args):
    nums=args[0];answer=0
    for indices in combinations(range(len(nums)),5):
        values=[nums[index] for index in indices];counts=Counter(values);middle=values[2]
        answer+=counts[middle]>max((count for value,count in counts.items() if value!=middle),default=0)
    return answer%MOD


def random_mode(rng):return [[rng.randint(-3,3) for _ in range(rng.randint(5,11))]]


def robot_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0]);answer=-10**30
    def visit(row,column,values):
        nonlocal answer
        values=values+[grid[row][column]]
        if row==rows-1 and column==columns-1:
            negatives=[index for index,value in enumerate(values) if value<0]
            best=sum(values)
            for count in range(1,min(2,len(negatives))+1):
                for chosen in combinations(negatives,count):best=max(best,sum(value for index,value in enumerate(values) if index not in chosen))
            answer=max(answer,best);return
        if row+1<rows:visit(row+1,column,values)
        if column+1<columns:visit(row,column+1,values)
    visit(0,0,[]);return answer


def random_robot(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5)
    return [[[rng.randint(-9,9) for _ in range(columns)] for _ in range(rows)]]


MIRROR='''def mirror_pair_score(s):
    positions=[[] for _ in range(26)];answer=0
    for index,char in enumerate(s):
        value=ord(char)-97;mirror=25-value
        if positions[mirror]:answer+=index-positions[mirror].pop()
        else:positions[value].append(index)
    return answer
'''

COINS='''def maximum_k_bag_coins(coins,k):
    from bisect import bisect_right
    segments=sorted(coins);starts=[left for left,_,_ in segments];prefix=[];total=0
    for left,right,value in segments:total+=(right-left+1)*value;prefix.append(total)
    def through(position):
        index=bisect_right(starts,position)-1
        if index<0:return 0
        before=prefix[index-1] if index else 0;left,right,value=segments[index]
        return before+max(0,min(position,right)-left+1)*value
    answer=0
    for left,right,_ in segments:
        for start in (left,right-k+1):answer=max(answer,through(start+k-1)-through(start-1))
    return answer
'''

INTERVALS='''def maximum_four_interval_indices(intervals):
    from bisect import bisect_right
    ordered=sorted((left,right,weight,index) for index,(left,right,weight) in enumerate(intervals));starts=[item[0] for item in ordered];n=len(ordered)
    previous=[(0,())]*(n+1)
    for count in range(1,5):
        current=[(0,())]*(n+1)
        for position in range(n-1,-1,-1):
            left,right,weight,index=ordered[position];following=bisect_right(starts,right)
            take=(weight+previous[following][0],tuple(sorted((index,)+previous[following][1])))
            skip=current[position+1]
            current[position]=take if take[0]>skip[0] or (take[0]==skip[0] and take[1]<skip[1]) else skip
        previous=current
    return list(previous[0][1])
'''

MODE='''def count_unique_middle_mode_large(nums):
    from collections import Counter
    from math import comb
    modulo=1000000007;n=len(nums);left=Counter();right=Counter(nums);left2=0;right2=sum(value*value for value in right.values());lr=lr2=l2r=0;answer=0
    for middle,x in enumerate(nums):
        old_right=right[x];old_left=left[x];right[x]-=1;new_right=old_right-1
        right2+=-2*old_right+1;lr-=old_left;lr2+=old_left*(-2*old_right+1);l2r-=old_left*old_left
        lx=old_left;rx=new_right;ln=middle-lx;rn=n-middle-1-rx
        at_least_two=0
        for a in range(3):
            for b in range(3):
                if a+b>=2 and a<=lx and 2-a<=ln and b<=rx and 2-b<=rn:
                    at_least_two+=comb(lx,a)*comb(ln,2-a)*comb(rx,b)*comb(rn,2-b)
        pair_left=(ln*ln-(left2-lx*lx))//2;pair_right=(rn*rn-(right2-rx*rx))//2
        shared=lr-lx*rx
        correction_left=rn*shared-(lr2-lx*rx*rx)
        correction_right=ln*shared-(l2r-lx*lx*rx)
        valid_once=lx*(ln*pair_right-correction_left)+rx*(rn*pair_left-correction_right)
        answer=(answer+at_least_two+valid_once)%modulo
        left[x]+=1;left2+=2*old_left+1;lr+=new_right;lr2+=new_right*new_right;l2r+=(2*old_left+1)*new_right
    return answer
'''

ROBOT='''def maximum_robot_money(coins):
    rows=len(coins);columns=len(coins[0]);negative=-10**30;previous=None
    for row in range(rows):
        current=[[negative]*3 for _ in range(columns)]
        for column in range(columns):
            parents=[negative]*3
            if row==0 and column==0:parents[0]=0
            else:
                for used in range(3):parents[used]=max(previous[column][used] if row else negative,current[column-1][used] if column else negative)
            value=coins[row][column]
            for used in range(3):
                if parents[used]>negative:current[column][used]=parents[used]+value
                if value<0 and used and parents[used-1]>negative:current[column][used]=max(current[column][used],parents[used-1])
        previous=current
    return max(previous[-1])
'''


def lesson(a,b,c,d):return [a,b,c,d]


MIRROR_CASES=[[s] for s in ['aczzx','a','az','za','abcxyz','abzy','aaaa','zaza','mnop','azbycx','leetcode','zyxabc','aazz','abcdefghijklmnopqrstuvwxyz','azz']]
COIN_CASES=[[segments,k] for segments,k in [
    ([[8,10,1],[1,3,2],[5,6,4]],4),([[1,1,5]],1),([[1,3,2]],2),([[1,3,2]],5),
    ([[1,2,3],[5,7,2]],3),([[1,1,10],[3,3,10]],2),([[2,4,1],[6,8,5]],4),
    ([[1,5,2],[10,10,9]],5),([[3,6,4],[8,9,3]],2),([[1,2,5],[4,6,1],[9,12,2]],6),
    ([[100,200,1]],50),([[1,1,2],[2,2,3],[3,3,4]],2),([[5,9,3],[15,20,2]],10),
    ([[1,4,1],[6,6,20],[8,10,2]],4)]]
INTERVAL_CASES=[[[x[:] for x in values]] for values in [
    [[1,3,2],[4,5,2],[1,5,5],[6,9,3],[6,7,1],[8,9,1]],[[1,1,5]],
    [[1,2,3],[2,3,4]],[[1,2,3],[3,4,4]],[[1,1,2],[2,2,2],[3,3,2],[4,4,2],[5,5,10]],
    [[1,5,7],[6,6,3],[7,7,3]],[[1,2,5],[4,5,5],[7,8,5],[10,11,5],[13,14,5]],
    [[1,10,20],[2,2,6],[4,4,6],[6,6,6],[8,8,6]],[[1,1,5],[3,3,5],[1,3,10]],
    [[5,8,4],[1,2,4],[3,4,4]],[[1,2,9],[2,2,10],[3,3,1]],
    [[1,1,4],[2,2,4],[3,3,4],[4,4,4]],[[1,4,5],[5,8,5],[9,12,5]],
    [[2,6,8],[1,1,2],[7,7,2],[8,9,9]]]]
MODE_CASES=[[[v for v in values]] for values in [[1,1,1,1,1,1],[1,2,3,4,5],[1,1,2,3,4],[1,2,1,2,1],[0,0,0,0,0],[1,2,2,2,3,4],[1,1,2,2,3,3],[1,2,3,2,1,2],[5,4,5,3,5,2,5],[-1,-1,0,1,-1,2],[1,2,1,3,1,4,1],[2,2,3,2,3,2,4],[0,1,0,1,0,2,0,3],[3,3,3,2,2,1,1,3]]]
ROBOT_CASES=[[[row[:] for row in grid]] for grid in [
    [[0,1,-1],[1,-2,3],[2,-3,4]],[[5]],[[-5]],[[1,2],[3,4]],[[-1,-2],[-3,-4]],
    [[1,-10,5]],[[1],[-10],[5]],[[0,-1,-2],[1,-3,4]],[[10,-100,10],[-1,-1,10]],
    [[-5,1],[1,-5]],[[2,-3,4],[-5,6,-7],[8,-9,10]],[[0,0],[0,0]],
    [[-1,5,-1],[2,-10,3]],[[4,-8,2],[-6,1,5],[3,-7,9]]]]


BATCH={
3412:entry('mirror_pair_score',[('s','str')],'int',['strings','stacks','greedy'],['s has 1–100,000 lowercase letters.','The mirror pairs a with z, b with y, and so on.','Scanning left to right, match each character with the closest earlier unmarked mirror when one exists and add their index distance.'],[(['aczzx'],'The z at index two pairs with a at zero, and x at four pairs with c at one, totaling five.'),(['az'],'The z pairs with the earlier a at distance one.')],MIRROR_CASES,MIRROR,[MIRROR.replace('.pop()','[-1]'),MIRROR.replace('mirror=25-value','mirror=24-value')],['Reuses an already marked mirror index for later characters.','Uses an off-by-one alphabet reflection.'],mirror_oracle,random_mirror,lesson('For each letter, unmatched positions are consumed in last-in-first-out order.','Maintain one stack per letter and consult the mirrored letter’s stack.','Pop the closest mirror and add the distance; otherwise push the current index.','A later unmatched mirror is always closer, and consuming it cannot improve any earlier index already processed.'),'O(n)','O(n)',5),
3413:entry('maximum_k_bag_coins',[('coins','list[list[int]]'),('k','int')],'int',['intervals','prefix sums','binary search'],['coins contains up to 100,000 pairwise non-overlapping inclusive segments [left,right,value].','Every bag in a segment holds value coins and bags outside all segments hold zero.','Return the maximum coins in any k consecutive integer positions.'],[([[[8,10,1],[1,3,2],[5,6,4]],4],'The four bags from three through six collect two plus zero plus four plus four, totaling ten.'),([[[1,3,2]],5],'A length-five window can cover the whole segment, collecting six coins.')],COIN_CASES,COINS,[COINS.replace('for start in (left,right-k+1)','for start in (left,)'),COINS.replace('start+k-1','start+k')],['Checks only windows beginning at a segment and misses an optimum ending at one.','Uses k+1 bags because the inclusive right endpoint is off by one.'],coins_oracle,random_coins,lesson('An optimal window can slide until its left edge meets a segment start or its right edge meets a segment end.','Build a prefix integral over sorted weighted segments and evaluate both endpoint-derived starts.','Use binary search to compute coins through any coordinate; subtract prefix values for each candidate length-k window.','Between segment boundaries the window total changes linearly, so a maximum occurs at one of the evaluated boundary events.'),'O(s log s)','O(s)',6),
3414:entry('maximum_four_interval_indices',[('intervals','list[list[int]]')],'list[int]',['intervals','dynamic programming','binary search'],['intervals has up to 50,000 inclusive [left,right,weight] entries with positive weights.','Choose at most four intervals that share no point, so the next start must exceed the previous end.','Maximize total weight and return the lexicographically smallest sorted list of original indices among ties.'],[([[[1,3,2],[4,5,2],[1,5,5],[6,9,3],[6,7,1],[8,9,1]]],'Intervals at indices two and three are disjoint and have maximum total weight eight.'),([[[1,1,4],[2,2,4],[3,3,4],[4,4,4]]],'All four point intervals are mutually disjoint, so return every index.')],INTERVAL_CASES,INTERVALS,[INTERVALS.replace('bisect_right(starts,right)','__import__("bisect").bisect_left(starts,right)'),INTERVALS.replace('take[1]<skip[1]','take[1]>skip[1]')],['Treats intervals touching at an endpoint as non-overlapping.','Chooses the lexicographically largest index list when weights tie.'],intervals_oracle,random_intervals,lesson('Sorting by start makes the next compatible interval a binary-search jump.','Use four bottom-up selection layers; each state compares skipping with taking and jumping past the current end.','Store total weight and a sorted index tuple, breaking equal-weight ties lexicographically.','The recurrence exhausts every compatible selection, while the tie comparison propagates the globally smallest optimal list.'),'O(4*n log n)','O(4*n)',8),
3416:entry('count_unique_middle_mode_large',[('nums','list[int]')],'int',['arrays','combinatorics','frequency counting'],['nums has 5–100,000 integers.','Choose five indices in increasing order; the third value must be the unique mode.','Return the count modulo 1,000,000,007.'],[([[1,1,1,1,1,1]],'Every five-index choice is valid, producing six.'),([[1,2,3,4,5]],'All selected values tie at frequency one, so the only subsequence is invalid.')],MODE_CASES,MODE,[MODE.replace('correction_left=rn*shared-(lr2-lx*rx*rx)','correction_left=0').replace('correction_right=ln*shared-(l2r-lx*lx*rx)','correction_right=0'),MODE.replace('+valid_once','')],['Allows another value to tie the middle value at frequency two.','Counts only cases with at least three copies of the middle value.'],mode_oracle,random_mode,lesson('The middle is uniquely modal with at least three copies, or with exactly two copies when the other three values are distinct.','Maintain global left/right frequency moments so distinct-triple corrections are available in O(1) per middle.','Update squared and cross moments when moving the middle; combine closed-form side choices for both valid cases.','Expanding the frequency sums yields the same distinct-value products as enumeration, but aggregates each middle in constant time.'),'O(n+d)','O(d)',8),
3418:entry('maximum_robot_money',[('coins','list[list[int]]')],'int',['matrices','dynamic programming','paths'],['coins has at most 500 rows and columns with values in -1,000..1,000.','Move only right or down from the top-left to bottom-right cell.','Collect cell values, but optionally neutralize the loss at up to two negative cells; maximize final money.'],[([[[0,1,-1],[1,-2,3],[2,-3,4]]],'Following the best path and neutralizing useful robbers yields eight.'),([[[-5]]],'Neutralize the robber in the only cell to finish with zero.')],ROBOT_CASES,ROBOT,[ROBOT.replace('return max(previous[-1])','return max(previous[-1][:2])'),ROBOT.replace('if value<0 and used and parents[used-1]>negative','if value<0 and used and (row,column)!=(rows-1,columns-1) and parents[used-1]>negative')],['Allows at most one neutralization instead of two.','Cannot neutralize a robber in the destination cell.'],robot_oracle,random_robot,lesson('Path position and neutralizations used fully determine future choices.','Keep three best values per cell, one for each used-neutralization count.','Transition from above or left by taking the cell value, and for a negative cell optionally advance the neutralization state without adding it.','Every path/state has one predecessor, so maximizing both transition types considers every legal strategy.'),'O(rows*cols)','O(cols)',6),
}
