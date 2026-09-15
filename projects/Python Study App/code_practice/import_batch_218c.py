"""Linked filtering, two cake-cut strategies, fast hopping, and paired differences."""
from itertools import permutations

from .import_batch_055 import entry


def list_oracle(args):
    removed,values=args;blocked=set(removed);return [value for value in values if value not in blocked]


def random_list(rng):
    values=[rng.randint(0,12) for _ in range(rng.randint(1,18))];removed=list({rng.randint(0,12) for _ in range(rng.randint(1,7))});return [removed,values]


def cake_oracle(args):
    _,_,horizontal,vertical=args;cuts=[('h',value) for value in horizontal]+[('v',value) for value in vertical];best=10**30
    for order in permutations(cuts):
        hp=vp=1;cost=0
        for direction,value in order:
            if direction=='h':cost+=value*vp;hp+=1
            else:cost+=value*hp;vp+=1
        best=min(best,cost)
    return best


def random_cake(rng):
    m=rng.randint(1,4);n=rng.randint(1,4)
    return [m,n,[rng.randint(1,12) for _ in range(m-1)],[rng.randint(1,12) for _ in range(n-1)]]


def hopping_oracle(args):
    nums=args[0];dp=[-10**30]*len(nums);dp[0]=0
    for end in range(1,len(nums)):dp[end]=max(dp[start]+(end-start)*nums[end] for start in range(end))
    return dp[-1]


def random_hopping(rng):return [[rng.randint(1,50) for _ in range(rng.randint(2,16))]]


def changes_oracle(args):
    nums,k=args;answer=len(nums)
    for target in range(k+1):
        cost=0
        for index in range(len(nums)//2):
            a,b=nums[index],nums[-1-index]
            if abs(a-b)==target:continue
            if any(abs(value-b)==target or abs(a-value)==target for value in range(k+1)):cost+=1
            else:cost+=2
        answer=min(answer,cost)
    return answer


def random_changes(rng):
    k=rng.randint(1,12);size=2*rng.randint(1,8);return [[rng.randint(0,k) for _ in range(size)],k]


LIST='''def remove_list_values(nums,head):
    blocked=set(nums);dummy=ListNode(0,head);current=dummy
    while current.next:
        if current.next.val in blocked:current.next=current.next.next
        else:current=current.next
    return dummy.next
'''


CAKE_DP='''def minimum_cake_cut_cost_dp(m,n,horizontalCut,verticalCut):
    horizontalCut=sorted(horizontalCut,reverse=True);verticalCut=sorted(verticalCut,reverse=True);inf=10**30
    dp=[[inf]*n for _ in range(m)];dp[0][0]=0
    for h in range(m):
        for v in range(n):
            if h<m-1:dp[h+1][v]=min(dp[h+1][v],dp[h][v]+horizontalCut[h]*(v+1))
            if v<n-1:dp[h][v+1]=min(dp[h][v+1],dp[h][v]+verticalCut[v]*(h+1))
    return dp[-1][-1]
'''


CAKE_GREEDY='''def minimum_cake_cut_cost_greedy(m,n,horizontalCut,verticalCut):
    cuts=sorted([(cost,0) for cost in horizontalCut]+[(cost,1) for cost in verticalCut],reverse=True);pieces=[1,1];answer=0
    for cost,direction in cuts:answer+=cost*pieces[1-direction];pieces[direction]+=1
    return answer
'''


HOPPING='''def maximum_array_hopping_score_fast(nums):
    best=answer=0
    for index in range(len(nums)-1,0,-1):best=max(best,nums[index]);answer+=best
    return answer
'''


CHANGES='''def minimum_equal_pair_difference_changes(nums,k):
    pairs=len(nums)//2;delta=[0]*(k+2)
    for index in range(pairs):
        first,second=nums[index],nums[-1-index];difference=abs(first-second);limit=max(first,second,k-first,k-second)
        delta[0]-=1;delta[limit+1]+=1;delta[difference]-=1;delta[difference+1]+=1
    cost=2*pairs;answer=cost
    for change in delta:cost+=change;answer=min(answer,cost)
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


CAKE_CASES=[(3,2,[1,3],[5]),(1,1,[],[]),(2,2,[1],[1]),(2,3,[5],[1,2]),(3,3,[1,2],[3,4]),(4,2,[4,1,7],[3]),(2,4,[9],[1,5,2]),(4,4,[1,1,1],[1,1,1]),(3,2,[10,1],[2]),(2,3,[2],[10,1]),(3,4,[3,8],[2,7,1]),(4,3,[6,2,5],[4,9]),(1,4,[],[3,1,2]),(4,1,[3,1,2],[])]

BATCH={
3217:entry('remove_list_values',[('nums','list[int]'),('head','ListNode')],'ListNode',['linked lists','hash sets'],['nums is nonempty and head is a nonempty singly linked list.','Remove every node whose value occurs in nums while preserving the order of surviving nodes.','Return the first surviving node, or None if every node is removed.'],[([[1,2,3],[1,2,3,4,5]],'The first three nodes are removed and nodes four and five remain linked.'),([[5],[5,1,5,2]],'Both nodes valued five are removed, leaving one followed by two.')],[[n,h] for n,h in [([1],[1]),([1],[2]),([1,2,3],[1,2,3,4,5]),([5],[5,1,5,2]),([2],[1,2,3]),([1,3],[1,2,3,4]),([9],[9,9,9]),([0],[0,1,0]),([4,5],[1,2,3]),([2,4],[2,3,4,5]),([7],[1,7,2,7,3]),([1,2],[2,1]),([3],[3,2,1,3]),([8,9],[8,1,9,2,8])]],LIST,[LIST.replace('current.next=current.next.next','current=current.next'),LIST.replace('dummy=ListNode(0,head)','dummy=ListNode(0,head.next)')],['Advances across blocked nodes without unlinking them.','Unconditionally drops the original head even when its value is allowed.'],list_oracle,random_list,lesson('A dummy predecessor handles deletions at the head with the same splice used elsewhere.','Store forbidden values in a set and examine current.next before advancing.','If next is blocked, bypass it; otherwise move current forward; return dummy.next.','Each original node is visited once, every blocked node is bypassed, and surviving links retain their original relative order.'),'O(len(nums)+nodes)','O(len(nums))',5),
3218:entry('minimum_cake_cut_cost_dp',[('m','int'),('n','int'),('horizontalCut','list[int]'),('verticalCut','list[int]')],'int',['dynamic programming','sorting','greedy'],['horizontalCut and verticalCut have lengths m-1 and n-1 and contain positive costs.','A cut is applied separately to every existing piece it crosses, always charging its listed cost.','Return the minimum total cost to produce all 1x1 pieces; this version uses a small-grid order DP.'],[([3,2,[1,3],[5]],'Making the cost-five vertical cut before both horizontal cuts costs 5+2*3+2*1=13.'),([2,2,[1],[1]],'Either order costs one plus twice one, totaling three.')],[[m,n,h,v] for m,n,h,v in CAKE_CASES],CAKE_DP,[CAKE_DP.replace('reverse=True','reverse=False'),CAKE_DP.replace('horizontalCut[h]*(v+1)','horizontalCut[h]')],['Processes cheap cuts before expensive cuts and makes them repeat across more pieces.','Charges horizontal cuts once regardless of how many vertical pieces they cross.'],cake_oracle,random_cake,lesson('Only how many horizontal and vertical cuts have occurred affects the multiplier of the next cut.','Sort costs descending within each direction and use DP over counts taken from both lists.','Transition by next horizontal cost*(verticalPieces) or next vertical cost*(horizontalPieces).','An exchange argument fixes descending order within each orientation, while DP enumerates every interleaving of those two fixed orders.'),'O(mn+(m+n)log(m+n))','O(mn)',5),
3219:entry('minimum_cake_cut_cost_greedy',[('m','int'),('n','int'),('horizontalCut','list[int]'),('verticalCut','list[int]')],'int',['greedy','sorting'],['horizontalCut and verticalCut have lengths m-1 and n-1 and may be large.','Each listed line must cut every current piece it crosses, paying its fixed cost for each piece.','Return the minimum total cost to create 1x1 pieces using the scalable greedy strategy.'],[([3,2,[1,3],[5]],'Taking cuts in descending cost order—5,3,1—costs 5+6+2=13.'),([2,3,[5],[1,2]],'Cut horizontal cost five first, then vertical costs two and one, totaling fourteen.')],[[m,n,h,v] for m,n,h,v in CAKE_CASES],CAKE_GREEDY,[CAKE_GREEDY.replace('reverse=True','reverse=False'),CAKE_GREEDY.replace('pieces[1-direction]','pieces[direction]')],['Takes cheap cuts first, causing expensive cuts to be paid across more pieces.','Multiplies a cut by pieces in its own direction rather than the perpendicular direction.'],cake_oracle,random_cake,lesson('Performing a larger-cost cut earlier prevents it from being multiplied by pieces created by cheaper perpendicular cuts.','Sort all cuts descending; multiply each by the current number of perpendicular pieces.','For (cost,direction), add cost*pieces[other], then increment pieces[direction].','Swapping an adjacent cheaper-before-expensive cross-direction pair never increases cost, so descending order is globally optimal.'),'O((m+n)log(m+n))','O(m+n)',8),
3221:entry('maximum_array_hopping_score_fast',[('nums','list[int]')],'int',['greedy','monotonic stacks'],['nums contains at least two positive integers and may be large.','Start at index zero and make rightward hops ending at the final index; hop i→j earns (j-i)*nums[j].','Return the maximum score in linear time.'],[([[1,5,8]],'Jumping directly to index two earns 2*8=16.'),([[4,10,2,8]],'The optimal gap contributions are 10,8,8, totaling 26.')],[[n] for n in [[1,5,8],[4,10,2,8],[1,1],[5,2],[1,2,3],[3,2,1],[2,9,1],[8,1,8],[1,10,1,10],[5,4,20,1],[2,3,2,3,2],[10,1,1,1,9],[7,6,5,100],[1,4,2,8,3]]],HOPPING,[HOPPING.replace('best=max(best,nums[index])','best=nums[index]'),HOPPING.replace('answer+=best','answer+=nums[index]')],['Uses the immediate destination rather than the best reachable destination for earlier gaps.','Always hops one position at a time and misses profitable longer jumps.'],hopping_oracle,random_hopping,lesson('A hop contributes its destination value once per unit gap crossed.','Assign each gap the maximum value to its right; suffix maxima produce a realizable sequence of hop endpoints.','Scan right to left, maintaining maximum destination value and adding it for each gap.','Choosing a new hop whenever the suffix maximum changes realizes all optimal gap assignments simultaneously.'),'O(n)','O(1)',5),
3224:entry('minimum_equal_pair_difference_changes',[('nums','list[int]'),('k','int')],'int',['prefix sums','arrays'],['nums has even positive length and every value lies from zero through k.','One change replaces one element by any integer from zero through k.','Make abs(nums[i]-nums[n-1-i]) equal for every mirrored pair using the fewest changes.'],[([[1,0,1,2,4,3],4],'Choosing a common difference two lets one pair stay unchanged and fixes the other two with one change each.'),([[0,0,0,0],3],'Every mirrored difference is already zero, so no changes are needed.')],[[n,k] for n,k in [([1,0,1,2,4,3],4),([0,0,0,0],3),([0,1],1),([0,0],1),([1,1,1,1],1),([0,2,0,2],2),([0,3,1,2],3),([1,4,2,3],4),([0,5,5,0],5),([2,2,0,4],4),([1,2,3,4,5,6],6),([0,1,2,3,4,5],5),([3,0,3,0],3),([2,5,1,6,0,4],6)]],CHANGES,[CHANGES.replace('return answer',"return pairs-max(__import__('collections').Counter(abs(nums[i]-nums[-1-i]) for i in range(pairs)).values())"),CHANGES.replace('delta[difference]-=1','delta[difference]+=1')],['Assumes every pair not already at the modal difference can always be fixed with exactly one change.','Adds cost at the pair’s existing difference instead of saving the second change there.'],changes_oracle,random_changes,lesson('For a pair, its current difference costs zero; any target through a computable limit costs one; larger targets cost two.','Start every pair at cost two and apply range-difference savings for its one-change interval and exact current difference.','limit=max(a,b,k-a,k-b); subtract one on [0,limit] and one more at abs(a-b); prefix-scan targets.','The delta events reproduce each pair’s exact 0/1/2 cost function, so minimizing their sum over all targets is optimal.'),'O(n+k)','O(k)',5),
}
BATCH[3217]['params'][1]=('head','ListNode','listnode')
BATCH[3217]['adapter']='listnode'
