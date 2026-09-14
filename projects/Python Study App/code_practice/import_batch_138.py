"""Medium-focused workbook batch 138."""

from .import_batch_055 import entry


def palindrome_oracle(args):
    text=args[0]
    return sum(text[i]!=text[-1-i] for i in range(len(text)//2))<=2


def random_palindrome(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,14)))]


def bus_oracle(args):
    buses,passengers,capacity=args;occupied=set(passengers);best=-1
    for candidate in range(max(buses)+1):
        if candidate in occupied:continue
        all_passengers=sorted(passengers+[candidate]);index=0;caught=False
        for bus in sorted(buses):
            seats=0
            while index<len(all_passengers) and all_passengers[index]<=bus and seats<capacity:
                if all_passengers[index]==candidate:caught=True
                index+=1;seats+=1
        if caught:best=candidate
    return best


def random_bus(rng):
    horizon=rng.randint(5,35);buses=sorted(rng.sample(range(2,horizon+1),rng.randint(1,min(5,horizon-1))));pool=[x for x in range(horizon+1) if x not in buses]
    passengers=sorted(rng.sample(pool,rng.randint(1,min(10,len(pool)))));return [buses,passengers,rng.randint(1,5)]


def trimmed_oracle(args):
    nums,queries=args;answer=[]
    for k,trim in queries:answer.append(sorted(range(len(nums)),key=lambda i:(nums[i][-trim:],i))[k-1])
    return answer


def random_trimmed(rng):
    length=rng.randint(1,8);width=rng.randint(1,6);nums=[f'{rng.randrange(10**width):0{width}d}' for _ in range(length)]
    return [nums,[[rng.randint(1,length),rng.randint(1,width)] for _ in range(rng.randint(1,8))]]


def mountains_oracle(args):
    peaks=args[0];intervals=[(x-y,x+y) for x,y in peaks];answer=0
    for i,(left,right) in enumerate(intervals):
        if not any(i!=j and other_left<=left and right<=other_right for j,(other_left,other_right) in enumerate(intervals)):answer+=1
    return answer


def random_mountains(rng):return [[[rng.randint(0,20),rng.randint(1,10)] for _ in range(rng.randint(1,12))]]


def groups_oracle(args):
    n=len(args[0]);best=0
    for groups in range(1,n+1):
        if groups*(groups+1)//2<=n:best=groups
    return best


def random_groups(rng):return [[rng.randint(1,100) for _ in range(rng.randint(1,100))]]


PALINDROME='''\
def can_make_palindrome_with_two_changes(s):
    mismatches=0
    for left in range(len(s)//2):
        if s[left]!=s[-1-left]:mismatches+=1
    return mismatches<=2
'''

BUS='''\
def latest_bus_arrival(buses,passengers,capacity):
    buses.sort();passengers.sort();index=0;last_boarded=-1;seats=0
    for bus in buses:
        seats=0
        while index<len(passengers) and passengers[index]<=bus and seats<capacity:last_boarded=passengers[index];index+=1;seats+=1
    candidate=buses[-1] if seats<capacity else last_boarded-1
    occupied=set(passengers)
    while candidate in occupied:candidate-=1
    return candidate
'''

TRIMMED='''\
def kth_smallest_trimmed_indices(nums,queries):
    answer=[]
    for k,trim in queries:answer.append(sorted(range(len(nums)),key=lambda index:(nums[index][-trim:],index))[k-1])
    return answer
'''

MOUNTAINS='''\
def count_visible_mountains(peaks):
    intervals=sorted((x-y,-(x+y)) for x,y in peaks);answer=0;farthest=-10**30;index=0
    while index<len(intervals):
        end=index+1
        while end<len(intervals) and intervals[end]==intervals[index]:end+=1
        left,negative_right=intervals[index];right=-negative_right
        if end-index==1 and right>farthest:answer+=1
        farthest=max(farthest,right);index=end
    return answer
'''

GROUPS='''\
def maximum_increasing_competition_groups(grades):
    groups=0;used=0;n=len(grades)
    while used+groups+1<=n:groups+=1;used+=groups
    return groups
'''


BATCH={
2330:entry('can_make_palindrome_with_two_changes',[('s','str')],'bool',['strings','two pointers'],['In one operation, change any character to another lowercase letter.','Return whether the string can become a palindrome using at most two changes.','A mirrored mismatch needs exactly one change; matching pairs need none.'],[(['abcdba'],'Only c and d form a mismatched mirrored pair, so changing either character makes the string a palindrome.'),(['abcdef'],'The three mirrored pairs all mismatch, so two changes are insufficient.')],[[s] for s in ['a','aa','ab','abc','abca','abcba','abecbea','abcdef','abcdefa','racecar','deeee','abbcca','abcddcxa','aaaaab','xyzyxq']],PALINDROME,[PALINDROME.replace('<=2','<=1'),PALINDROME.replace('mismatches+=1','mismatches+=2')],['Allows only one mismatched mirrored pair.','Incorrectly charges two changes for each mismatched pair.'],palindrome_oracle,random_palindrome,['Compare characters in mirrored positions from the two ends.','Each mismatched pair can be repaired with one character change.','Count mismatched pairs and accept when the count is at most two.','Pairs are independent: every mismatch requires one change and one change always repairs it, so the mismatch count is the exact minimum.'],'O(n)','O(1)',5),
2332:entry('latest_bus_arrival',[('buses','list[int]'),('passengers','list[int]'),('capacity','int')],'int',['arrays','sorting','greedy'],['Buses and passengers arrive at distinct integer times; buses depart in increasing time order after boarding up to capacity waiting passengers.','Choose an arrival time not equal to any passenger time.','Return the latest time that lets you board some bus.'],[([[10,20],[2,17,18,19],2],'The final bus fills with passengers seventeen and eighteen, so sixteen is the latest unused arrival that boards.'),([[20,30,10],[19,13,26,4,25,11,21],2],'After earlier buses board the earliest passengers, arriving twenty lets you board the final bus.')],[[b,p,c] for b,p,c in [([10],[1],1),([10],[10],1),([10],[1,2],3),([5,10],[4,9],1),([5,10],[4],1),([3,6],[1,2,4,5],2),([10,20],[2,17,18,19],3),([2],[0,1],2),([5,7,9],[1,3,6],1),([10],[8,9],1),([4,8],[2,3,4,7],2),([6,12],[1,5,6,10,11],3),([20,30],[5,10,15,25],2),([3,4],[1,2,3],2)]],BUS,[BUS.replace("candidate=buses[-1] if seats<capacity else last_boarded-1","candidate=buses[-1]"),BUS.replace('while candidate in occupied:candidate-=1','')],['Always chooses the last bus departure even when later-arriving passengers fill that bus first.','Does not move backward past occupied passenger arrival times.'],bus_oracle,random_bus,['Simulate sorted buses boarding sorted waiting passengers.','After the final bus, start from its departure if it has a free seat; otherwise start one before its last boarded passenger.','Move backward while the candidate is an existing passenger time.','The simulation fixes the final capacity boundary, and every later time is either too late, displaced, or forbidden, proving maximality.'],'O((b+p) log(b+p))','O(p)',5),
2343:entry('kth_smallest_trimmed_indices',[('nums','list[str]'),('queries','list[list[int]]')],'list[int]',['strings','sorting'],['All numeric strings have equal length.','For query [k,trim], compare only each string’s last trim digits, retaining leading zeroes.','Return the original index of the kth smallest trimmed value, breaking ties by smaller original index.'],[([['102','473','251','814'],[[1,1],[2,3],[4,2],[1,2]]],'Sorting the requested suffixes gives original indexes [2,2,1,0].'),([['24','37','96','04'],[[2,1],[2,2]]],'For one digit the order is 24(index 0), 04(3), 96(2), 37(1), so k=2 returns 3; for two digits, 04 then 24 makes k=2 return 0.')],[[n,q] for n,q in [(['1'],[[1,1]]),(['01','02'],[[1,1]]),(['10','00'],[[2,1]]),(['111','111'],[[2,3]]),(['123','234','345'],[[2,2]]),(['999','001','010'],[[1,3]]),(['12','21','11'],[[2,1]]),(['000','100','200'],[[3,2]]),(['5','4','3'],[[1,1],[3,1]]),(['1010','0010','1111'],[[2,2]]),(['90','09'],[[1,1]]),(['1234','0234','2234'],[[3,3]]),(['808','707','606'],[[2,1]]),(['42','24','42'],[[2,2]])]],TRIMMED,[TRIMMED.replace('nums[index][-trim:]','nums[index][:trim]'),TRIMMED.replace('(nums[index][-trim:],index)','(nums[index][-trim:],-index)')],['Uses leading digits instead of the required suffix.','Reverses the required original-index tie break.'],trimmed_oracle,random_trimmed,['For each query, pair every trimmed suffix with its original index.','Because strings have equal trim length, lexicographic and numeric suffix order agree, including leading zeroes.','Sort by (suffix,index) and return the index at position k-1.','The tuple key implements both the primary numeric order and the exact index tie break.'],'O(q*n log n*width)','O(n)',5),
2345:entry('count_visible_mountains',[('peaks','list[list[int]]')],'int',['sorting','intervals','geometry'],['Peak [x,y] defines a mountain spanning interval [x-y,x+y].','A mountain is hidden when its triangular region is contained in another mountain, including boundary containment.','Identical mountains hide each other; return the number of visible mountains.'],[([[[2,2],[6,3],[5,4]]],'The mountain centered at six is contained by the wider mountain centered at five, leaving two visible mountains.'),([[[1,3],[1,3]]],'The identical mountains each lie within the other, so neither is visible.')],[[p] for p in [[[1,1]],[[1,1],[3,1]],[[1,2],[2,1]],[[2,2],[2,1]],[[0,5],[1,4]],[[0,2],[4,2],[2,5]],[[5,1],[5,1],[10,2]],[[2,3],[6,1]],[[3,3],[4,4]],[[10,5],[8,1],[12,1]],[[1,10],[2,2],[3,1]],[[0,1],[2,1],[4,1]],[[5,5],[5,4],[5,3]],[[2,2],[6,3],[5,4],[9,1]]]],MOUNTAINS,[MOUNTAINS.replace('end-index==1 and ',''),MOUNTAINS.replace('right>farthest','right>=farthest')],['Counts one copy of an identical duplicated mountain as visible.','Treats an equal right boundary as escaping containment.'],mountains_oracle,random_mountains,['Transform each peak into its left and right ground endpoints.','Sort by left endpoint and scan groups of identical intervals while tracking the farthest right endpoint seen.','A unique interval is visible only when its right endpoint exceeds the prior farthest; duplicate intervals contribute zero.','Earlier sorted intervals are exactly the only possible containers, and farthest right summarizes whether one covers the current interval.'],'O(n log n)','O(n)',5),
2358:entry('maximum_increasing_competition_groups',[('grades','list[int]')],'int',['greedy','math'],['Use every student in at most one group; grade values may be assigned in any order.','Each next group must have strictly more students and a strictly larger grade sum than the previous group.','Return the maximum possible number of groups.'],[([[10,6,12,7,3,5]],'Six students can form groups of sizes one, two, and three with increasing grade sums.'),([[8,8]],'Two students cannot form two groups of sizes one and two, so only one group is possible.')],[[g] for g in [[1],[1,2],[1,2,3],[1,1,1,1,1,1],[5,4,3,2,1],[10]*10,[1,100,1],[2,2,2],[1,2,3,4,5,6,7,8,9,10],[9,1,8,2,7],[3,3,3,3,3,3],[1]*15,[5,10,15,20],[100,1,1,1,1,1]]],GROUPS,[GROUPS.replace('used+groups+1<=n','used+2*(groups+1)<=n'),GROUPS.replace('used+=groups','used+=groups+1')],['Incorrectly requires twice the next group size to remain available.','Consumes one extra student per group and underestimates the feasible group count.'],groups_oracle,random_groups,['Only the number of available students limits the group count because positive grades can be ordered to make sums rise with group size.','The smallest strictly increasing group sizes are one, two, ..., g.','Increase g while the triangular total g(g+1)/2 fits within n students.','Any g groups need at least that many students, and assigning sorted grades across those growing sizes realizes increasing sums, so the bound is tight.'],'O(sqrt n)','O(1)',5),
}
