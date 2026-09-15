"""Event mentions, frequency gains, alternating permutations, and meeting rescheduling."""
from itertools import product

from .import_batch_055 import entry


def mentions_oracle(args):
    users,events=args;answer=[0]*users;offline_until=[0]*users
    for kind,time,text in sorted(events,key=lambda event:(int(event[1]),0 if event[0]=='OFFLINE' else 1)):
        now=int(time)
        if kind=='OFFLINE':offline_until[int(text)]=now+60
        elif text=='ALL':
            for user in range(users):answer[user]+=1
        elif text=='HERE':
            for user in range(users):answer[user]+=offline_until[user]<=now
        else:
            for token in text.split():answer[int(token[2:])]+=1
    return answer


def random_mentions(rng):
    users=rng.randint(1,5);events=[];offline_until=[0]*users;now=0
    for _ in range(rng.randint(1,14)):
        now+=rng.randint(1,15);online=[user for user in range(users) if offline_until[user]<=now]
        if online and rng.random()<.25:
            user=rng.choice(online);events.append(['OFFLINE',str(now),str(user)]);offline_until[user]=now+60
        else:
            style=rng.randrange(3)
            if style==0:text='ALL'
            elif style==1:text='HERE'
            else:text=' '.join('id'+str(rng.randrange(users)) for _ in range(rng.randint(1,5)))
            events.append(['MESSAGE',str(now),text])
    rng.shuffle(events);return [users,events]


def frequency_oracle(args):
    nums,target=args;base=nums.count(target);answer=base
    for value in set(nums)-{target}:
        for left in range(len(nums)):
            gain=0
            for right in range(left,len(nums)):
                gain+=(nums[right]==value)-(nums[right]==target);answer=max(answer,base+gain)
    return answer


def random_frequency(rng):
    return [[rng.randint(1,6) for _ in range(rng.randint(1,14))],rng.randint(1,6)]


def distance_oracle(args):
    text,k=args;answer=0
    for changed in product('NSEW',repeat=len(text)):
        if sum(left!=right for left,right in zip(text,changed))>k:continue
        x=y=0
        for direction in changed:
            x+=(direction=='E')-(direction=='W');y+=(direction=='N')-(direction=='S');answer=max(answer,abs(x)+abs(y))
    return answer


def random_distance(rng):
    n=rng.randint(1,6)
    return [''.join(rng.choice('NSEW') for _ in range(n)),rng.randint(0,n)]


def ordered_meeting_oracle(args):
    event_time,k,starts,ends=args;gaps=[starts[0]]+[starts[i]-ends[i-1] for i in range(1,len(starts))]+[event_time-ends[-1]]
    return max(sum(gaps[left:left+k+1]) for left in range(len(gaps)-k))


def random_meetings_one(rng):
    event_time=rng.randint(4,28);n=rng.randint(1,min(7,event_time//2));points=sorted(rng.sample(range(event_time+1),2*n))
    starts=points[::2];ends=points[1::2]
    return [event_time,rng.randint(1,n),starts,ends]


def free_time(starts,ends,event_time):
    ordered=sorted(zip(starts,ends));last=0;answer=0
    for start,end in ordered:answer=max(answer,start-last);last=end
    return max(answer,event_time-last)


def movable_meeting_oracle(args):
    event_time,starts,ends=args;answer=free_time(starts,ends,event_time)
    for removed in range(len(starts)):
        duration=ends[removed]-starts[removed];other=[(starts[i],ends[i]) for i in range(len(starts)) if i!=removed]
        for new_start in range(event_time-duration+1):
            new_end=new_start+duration
            if all(new_end<=left or right<=new_start for left,right in other):
                pairs=other+[(new_start,new_end)];answer=max(answer,free_time([a for a,_ in pairs],[b for _,b in pairs],event_time))
    return answer


def random_meetings_two(rng):
    event_time=rng.randint(4,24);n=rng.randint(1,min(6,event_time//2));points=sorted(rng.sample(range(event_time+1),2*n))
    return [event_time,points[::2],points[1::2]]


MENTIONS='''def count_user_mentions(number_of_users,events):
    events=sorted(events,key=lambda event:(int(event[1]),0 if event[0]=='OFFLINE' else 1));answer=[0]*number_of_users;online_at=[0]*number_of_users;all_count=0
    for kind,timestamp,text in events:
        now=int(timestamp)
        if kind=='OFFLINE':online_at[int(text)]=now+60
        elif text=='ALL':all_count+=1
        elif text=='HERE':
            for user,ready in enumerate(online_at):
                if ready<=now:answer[user]+=1
        else:
            for token in text.split():answer[int(token[2:])]+=1
    return [count+all_count for count in answer]
'''

FREQUENCY='''def maximum_target_frequency_after_subarray(nums,k):
    base=nums.count(k);best=0
    for value in set(nums):
        if value==k:continue
        gain=current=0
        for number in nums:
            current=max(0,current+(number==value)-(number==k));gain=max(gain,current)
        best=max(best,gain)
    return base+best
'''

DISTANCE='''def maximum_changed_path_distance(s,k):
    def direction_score(first,second):
        current=changed=answer=0
        for direction in s:
            if direction==first or direction==second:current+=1
            elif changed<k:changed+=1;current+=1
            else:current-=1
            answer=max(answer,current)
        return answer
    return max(direction_score('N','E'),direction_score('N','W'),direction_score('S','E'),direction_score('S','W'))
'''

ORDERED='''def maximum_ordered_meeting_free_time(event_time,k,start_time,end_time):
    gaps=[start_time[0]]
    for index in range(1,len(start_time)):gaps.append(start_time[index]-end_time[index-1])
    gaps.append(event_time-end_time[-1]);window=sum(gaps[:k+1]);answer=window
    for right in range(k+1,len(gaps)):
        window+=gaps[right]-gaps[right-k-1];answer=max(answer,window)
    return answer
'''

MOVABLE='''def maximum_movable_meeting_free_time(event_time,start_time,end_time):
    n=len(start_time);gaps=[start_time[0]]+[start_time[i]-end_time[i-1] for i in range(1,n)]+[event_time-end_time[-1]]
    prefix=[0]*(n+1);suffix=[0]*(n+1)
    for i in range(n):prefix[i+1]=max(prefix[i],gaps[i])
    for i in range(n-1,-1,-1):suffix[i]=max(suffix[i+1],gaps[i+1])
    answer=0
    for i in range(n):
        duration=end_time[i]-start_time[i];combined=gaps[i]+gaps[i+1]
        answer=max(answer,combined+duration if max(prefix[i],suffix[i+1])>=duration else combined)
    return answer
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


MENTION_CASES=[[users,events] for users,events in [(2,[['MESSAGE','10','id1 id0'],['OFFLINE','11','0'],['MESSAGE','71','HERE']]),(2,[['MESSAGE','10','id1 id0'],['OFFLINE','11','0'],['MESSAGE','12','ALL']]),(1,[['MESSAGE','1','HERE']]),(1,[['OFFLINE','1','0'],['MESSAGE','2','HERE']]),(2,[['MESSAGE','5','id0 id0 id1']]),(3,[['MESSAGE','8','ALL']]),(3,[['OFFLINE','2','1'],['MESSAGE','2','HERE']]),(2,[['OFFLINE','10','0'],['MESSAGE','69','HERE'],['MESSAGE','70','HERE']]),(3,[['OFFLINE','5','2'],['MESSAGE','7','id2'],['MESSAGE','8','HERE']]),(4,[['MESSAGE','20','ALL'],['MESSAGE','10','id3'],['MESSAGE','15','HERE']]),(2,[['OFFLINE','5','1'],['MESSAGE','65','HERE']]),(3,[['OFFLINE','1','0'],['OFFLINE','2','1'],['MESSAGE','3','ALL']]),(4,[['MESSAGE','1','id0 id2'],['MESSAGE','1','ALL']]),(2,[['OFFLINE','10','0'],['MESSAGE','10','HERE'],['MESSAGE','10','id0']])]]
FREQUENCY_CASES=[[nums,k] for nums,k in [([1,2,3,4,5,6],1),([10,2,3,4,5,5,4,3,2,2],10),([1],1),([2],1),([1,1,1],1),([2,2,2],1),([1,2,1,2,1],1),([2,1,2,1,2],1),([3,1,3,3,1,3],1),([1,2,3,2,2,1],3),([4,4,1,4,1,1,4],1),([5,1,2,5,2,5,2],5),([1,2,3,4,3,2,1],4),([6,5,6,5,4,5,6],5)]]
DISTANCE_CASES=[[text,k] for text,k in [('NWSE',1),('NSWWEW',3),('N',0),('N',1),('NS',0),('NS',1),('EEEE',0),('NESW',2),('SSSNN',1),('EWEWEW',3),('NNSSWWEE',2),('SW',0),('WNES',4),('NWNWNW',2)]]
ORDERED_CASES=[[event,k,starts,ends] for event,k,starts,ends in [(5,1,[1,3],[2,5]),(10,1,[0,2,9],[1,4,10]),(5,1,[1],[2]),(5,1,[0],[5]),(10,2,[1,4],[2,5]),(10,1,[1,4],[2,5]),(20,3,[2,5,9],[3,7,12]),(12,2,[0,3,8],[2,5,10]),(15,1,[1,5,10],[3,7,12]),(8,2,[1,3,6],[2,5,7]),(30,4,[2,7,12,20],[5,9,15,25]),(9,1,[2,4],[3,8]),(16,2,[1,6,11],[4,8,13]),(25,3,[0,4,10,18],[2,7,14,20])]]
MOVABLE_CASES=[[event,starts,ends] for event,starts,ends in [(5,[1,3],[2,5]),(10,[0,7,9],[1,8,10]),(5,[1],[2]),(5,[0],[5]),(10,[1,4],[2,5]),(20,[2,5,9],[3,7,12]),(12,[0,3,8],[2,5,10]),(15,[1,5,10],[3,7,12]),(8,[1,3,6],[2,5,7]),(30,[2,7,12,20],[5,9,15,25]),(9,[2,4],[3,8]),(16,[1,6,11],[4,8,13]),(25,[0,4,10,18],[2,7,14,20]),(18,[2,6,13],[4,10,15])]]


BATCH={
3433:entry('count_user_mentions',[('number_of_users','int'),('events','list[list[str]]')],'list[int]',['arrays','sorting','simulation'],['There are 1–100 users, all initially online; events contain a type, integer timestamp string, and payload.','OFFLINE makes one online user unavailable for 60 time units and is processed before messages at the same timestamp.','ALL mentions every user, HERE mentions users online then, and explicit id tokens count even offline and count duplicates.'],[([2,[['MESSAGE','10','id1 id0'],['OFFLINE','11','0'],['MESSAGE','71','HERE']]],'The explicit message mentions both users, and both are online again for HERE at time 71, yielding [2,2].'),([2,[['OFFLINE','10','0'],['MESSAGE','10','HERE'],['MESSAGE','10','id0']]],'The offline event precedes HERE, so only user one receives it; explicit id0 still counts, yielding [1,1].')],MENTION_CASES,MENTIONS,[MENTIONS.replace("0 if event[0]=='OFFLINE' else 1","0 if event[0]=='MESSAGE' else 1"),MENTIONS.replace("elif text=='ALL':all_count+=1","elif text=='ALL':\n            for user,ready in enumerate(online_at):\n                if ready<=now:answer[user]+=1")],['Processes a same-time message before the status change.','Incorrectly excludes offline users from ALL mentions.'],mentions_oracle,random_mentions,lesson('Offline expiration timestamps avoid scheduling separate online events.','Sort chronologically with OFFLINE before MESSAGE, and handle the three mention forms separately.','Update one expiration for OFFLINE; count HERE from expirations, explicit tokens directly, and defer universal ALL additions.','Each event is evaluated against exactly the status required at its timestamp, while deferred ALL counts apply equally to every user.'),'O(e log e+e*u)','O(u+e)',6),
3434:entry('maximum_target_frequency_after_subarray',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming','prefix sums'],['nums has 1–100,000 values in 1..50 and k is in the same range.','Choose one nonempty subarray and add one integer x to every element in it.','Return the largest achievable frequency of k.'],[([[1,2,3,4,5,6],1],'Changing a subarray containing the six to one adds one occurrence without losing the existing one, so the maximum is two.'),([[10,2,3,4,5,5,4,3,2,2],10],'Changing the subarray after the first element by eight converts its three twos to tens, yielding four tens.')],FREQUENCY_CASES,FREQUENCY,[FREQUENCY.replace('-(number==k)',''),FREQUENCY.replace('return base+best','return best')],['Does not subtract target values destroyed inside the changed subarray.','Returns only the gained occurrences and omits targets already present outside the operation.'],frequency_oracle,random_frequency,lesson('For a chosen source value v, changing v to k gains one at v positions but loses one at existing k positions inside the same subarray.','Run maximum-subarray gain independently for each distinct source value.','Map v to +1, k to -1, and others to zero; use Kadane’s algorithm and add the best gain to the original k count.','Any useful x selects exactly one source value k-x, so enumerating those values covers every operation.'),'O(50*n)','O(1)',6),
3443:entry('maximum_changed_path_distance',[('s','str'),('k','int')],'int',['strings','greedy','counting'],['s has 1–100,000 characters drawn from N, S, E, and W; 0 <= k <= len(s).','Change at most k directions, then follow the movements from the origin in order.','Return the greatest Manhattan distance reached at any prefix of the changed path.'],[(['NWSE',1],'Changing S to N produces prefix position (-1,2), whose Manhattan distance is three.'),(['NSWWEW',3],'Changing opposing moves lets the path reach distance six.')],DISTANCE_CASES,DISTANCE,[DISTANCE.replace('answer=max(answer,current)','answer=current'),DISTANCE.replace("return max(direction_score('N','E'),direction_score('N','W'),direction_score('S','E'),direction_score('S','W'))","return direction_score('N','E')")],['Returns only the final distance for each directional quadrant and misses a larger earlier prefix.','Optimizes only the northeast quadrant and misses paths best directed elsewhere.'],distance_oracle,random_distance,lesson('Manhattan distance is the maximum signed projection toward NE, NW, SE, or SW.','For each quadrant, greedily spend changes on moves pointing outside it while scanning prefixes.','Score an aligned move as +1; change up to k opposing moves to +1, then score remaining opposing moves as -1.','Each change improves a fixed projection by two, so changing the earliest opposing moves maximizes every prefix for that quadrant.'),'O(n)','O(1)',6),
3439:entry('maximum_ordered_meeting_free_time',[('event_time','int'),('k','int'),('start_time','list[int]'),('end_time','list[int]')],'int',['arrays','sliding window','greedy'],['Meetings are positive-duration, sorted, non-overlapping, and contained in 0..event_time.','Move at most k meetings without changing durations or meeting order.','Return the longest continuous free interval possible.'],[([5,1,[1,3],[2,5]],'Moving the first meeting next to the second combines the two surrounding one-unit gaps into two free units.'),([10,2,[1,4],[2,5]],'Moving both meetings together consolidates all eight free time units into one interval.')],ORDERED_CASES,ORDERED,[ORDERED.replace('gaps[:k+1]','gaps[:k]'),ORDERED.replace('right-k-1','right-k')],['Combines only k gaps even though moving k meetings can merge k+1 gaps.','Removes the wrong outgoing gap as the window advances.'],ordered_meeting_oracle,random_meetings_one,lesson('Moving k consecutive meetings together can merge the k+1 free gaps around and between them.','Compute all free gaps and find the largest sum of k+1 consecutive gaps.','Build boundary and interior gaps, then slide a fixed window of length k+1.','Any order-preserving move affects a consecutive meeting block, and its total surrounding free space is both an upper bound and achievable.'),'O(n)','O(n)',6),
3440:entry('maximum_movable_meeting_free_time',[('event_time','int'),('start_time','list[int]'),('end_time','list[int]')],'int',['arrays','prefix maxima','greedy'],['Meetings are positive-duration, sorted, non-overlapping, and contained in 0..event_time.','Move at most one meeting, keeping its duration; unlike the ordered version, its position in the sequence may change.','Return the longest continuous free interval possible.'],[([5,[1,3],[2,5]],'The first meeting cannot fit elsewhere, but shifting it joins its adjacent gaps for two free units.'),([10,[1,4],[2,5]],'The one-unit first meeting fits after time five, freeing the entire interval from zero through four.')],MOVABLE_CASES,MOVABLE,[MOVABLE.replace('max(prefix[i],suffix[i+1])','prefix[i]'),MOVABLE.replace('combined+duration','combined')],['Checks relocation space only before the removed meeting and misses later gaps.','Never relocates a meeting outside its old span, so it cannot recover the meeting duration as free time.'],movable_meeting_oracle,random_meetings_two,lesson('Removing a meeting always joins its two adjacent gaps; relocating it elsewhere also frees its own duration when another gap can hold it.','Precompute the largest gap strictly before and after each meeting’s adjacent gaps.','For each meeting compare the joined gaps alone with joined gaps plus duration when an outside gap is large enough.','Only outside gaps may host the meeting without splitting the candidate joined interval, and prefix/suffix maxima test exactly those locations.'),'O(n)','O(n)',6),
}
