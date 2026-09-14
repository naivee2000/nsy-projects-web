"""Ordinary linked-list games/frequencies and simple array threshold/distribution problems."""
from collections import Counter
from .import_batch_055 import entry

def game_oracle(a):
    values=a[0];score=sum((values[i]>values[i+1])-(values[i]<values[i+1]) for i in range(0,len(values),2))
    return 'Even' if score>0 else 'Odd' if score<0 else 'Tie'
def random_game(r):
    pairs=[]
    for _ in range(r.randint(1,20)):pairs.extend((2*r.randint(1,50),2*r.randint(1,50)-1))
    return [pairs]
def frequencies_oracle(a):return list(Counter(a[0]).values())
def random_frequencies(r):return [[r.randint(1,20) for _ in range(r.randint(1,60))]]
def threshold_oracle(a):return sum(value<a[1] for value in a[0])
def random_threshold(r):return [[r.randint(1,100) for _ in range(r.randint(1,50))],r.randint(1,100)]
def distribute_oracle(a):
    nums=a[0];one=[nums[0]];two=[nums[1]]
    for value in nums[2:]:
        (one if one[-1]>two[-1] else two).append(value)
    return one+two
def random_distribute(r):return [[r.randint(1,100) for _ in range(r.randint(2,40))]]
def boxes_oracle(a):
    total=sum(a[0]);capacities=sorted(a[1],reverse=True);current=0
    for count,value in enumerate(capacities,1):
        current+=value
        if current>=total:return count
def random_boxes(r):
    apple=[r.randint(1,10) for _ in range(r.randint(1,15))];total=sum(apple);caps=[r.randint(1,20) for _ in range(r.randint(1,15))]
    if sum(caps)<total:caps.append(total)
    return [apple,caps]

GAME='''\
def linked_list_pair_game(head):
    even=odd=0;node=head
    while node:
        if node.val>node.next.val:even+=1
        elif node.val<node.next.val:odd+=1
        node=node.next.next
    return 'Even' if even>odd else 'Odd' if odd>even else 'Tie'
'''
FREQUENCIES='''\
def linked_list_value_frequencies(head):
    from collections import Counter
    counts=Counter();node=head
    while node:counts[node.val]+=1;node=node.next
    dummy=tail=ListNode()
    for count in counts.values():tail.next=ListNode(count);tail=tail.next
    return dummy.next
'''
THRESHOLD='''\
def operations_to_exceed_threshold(nums,k):
    return sum(value<k for value in nums)
'''
DISTRIBUTE='''\
def distribute_by_last_value(nums):
    result1=[nums[0]];result2=[nums[1]]
    for value in nums[2:]:
        if result1[-1]>result2[-1]:result1.append(value)
        else:result2.append(value)
    return result1+result2
'''
BOXES='''\
def minimum_boxes_for_apples(apple,capacity):
    needed=sum(apple);stored=0
    for count,space in enumerate(sorted(capacity,reverse=True),1):
        stored+=space
        if stored>=needed:return count
'''

BATCH={
3062:entry('linked_list_pair_game',[('head','ListNode | None')],'str',['linked lists','simulation'],['The nonempty linked list has even length and is read in consecutive node pairs.','The Even team scores when the even-indexed value is larger; Odd scores when the following odd-indexed value is larger.','Return Even, Odd, or Tie according to total points.'],[([[2,1]],'Two exceeds one, so the Even team wins the only pair.'),([[2,5,4,7,20,5]],'Odd wins two pairs and Even wins one, so return Odd.')],[[x] for x in [[2,1],[2,5],[4,5,2,1],[2,5,4,7,20,5],[10,9,8,7],[2,3,4,5],[6,1,2,9],[2,1,4,3,6,5],[2,9,8,1],[100,99],[2,99,100,1],[8,7,6,9],[20,1,2,3,4,5],[2,3,4,1,6,5]]],GAME,[GAME.replace('node.val>node.next.val','node.val<node.next.val',1),GAME.replace('node=node.next.next','node=node.next')],['Awards Even points using the reversed comparison.','Advances one node and then pairs overlapping/wrong parity positions.'],game_oracle,random_game,['Each even-indexed node is paired only with its immediate successor.','Compare their values and update one of two point totals.','Advance by two nodes after every comparison.','The traversal visits every declared pair exactly once, so comparing the final totals gives the game result.'],'O(n)','O(1)',3),
3063:entry('linked_list_value_frequencies',[('head','ListNode | None')],'ListNode | None',['linked lists','hash maps','counting'],['Count each distinct value in the input linked list.','Create and return a new linked list containing one frequency per distinct value.','Any frequency order is accepted; the input nodes must remain unchanged.'],[([[1,1,2,1,2,3]],'The frequencies are three, two, and one.'),([[1,1,2,2,2]],'The two distinct values occur two and three times.')],[[x] for x in [[1],[1,1],[1,2],[1,1,2,1,2,3],[1,1,2,2,2],[6,5,4,3,2,1],[3,3,3],[1,2,1,2],[5,4,5,4,5],[9,8,7,9],[2,2,3,3,4,4],[10,10,10,20],[1,2,3,4,1],[7,6,7,6,7,5]]],FREQUENCIES,[FREQUENCIES.replace('counts[node.val]+=1','counts[node.val]=1'),FREQUENCIES.replace('for count in counts.values()','for count in counts.keys()')],['Records only presence, so repeated values still produce frequency one.','Returns the distinct values themselves rather than their frequencies.'],frequencies_oracle,random_frequencies,['Traverse the input once and count values in a hash map.','Allocate one output node for each stored frequency.','Link those new nodes and return the first one.','The counter is exact by induction over visited nodes, and emitting its values produces exactly one frequency per distinct input value.'],'O(n)','O(k)',3),
3065:entry('operations_to_exceed_threshold',[('nums','list[int]'),('k','int')],'int',['arrays','counting'],['One operation removes one array value strictly less than k.','Continue until every remaining value is at least k.','Return the minimum number of operations.'],[([[2,11,10,1,3],10],'The values two, one, and three must be removed, giving three operations.'),([[1,1,2,4,9],1],'Every value already meets the threshold, so zero operations are needed.')],[[nums,k] for nums,k in [([1],1),([1],2),([2,11,10,1,3],10),([1,1,2,4,9],1),([5,5],5),([4,5],5),([1,2,3],4),([10,20,30],15),([0,1,2],1),([9,8,7],8),([3,3,3],4),([100,1],100),([2,4,6,8],7),([1,10,2,20],10)]],THRESHOLD,[THRESHOLD.replace('value<k','value<=k'),THRESHOLD.replace('sum(','len([').replace(' for value in nums)', ' for value in nums if value<k])')],['Removes values equal to k even though they already satisfy the goal.','The altered counting expression double-filters incorrectly.'],threshold_oracle,random_threshold,['Every below-threshold value must disappear, and removing it once is sufficient.','No operation is needed for a value already at least k.','Count the values strictly less than k.','This count is both a lower bound and an achievable removal plan, so it is minimal.'],'O(n)','O(1)',3),
3069:entry('distribute_by_last_value',[('nums','list[int]')],'list[int]',['arrays','simulation'],['Start result1 with nums[0] and result2 with nums[1].','For each later value, append it to result1 when result1’s last value is greater than result2’s last value; otherwise append to result2.','Return result1 followed by result2.'],[([[2,1,3]],'Because two is greater than one, three joins result1, producing [2,3,1].'),([[5,4,3,8]],'Both later values follow the changing last-value comparison, producing [5,3,8,4].')],[[x] for x in [[1,2],[2,1],[2,1,3],[5,4,3,8],[1,1,2],[3,2,1,4],[10,1,5,6],[2,9,8,1],[4,3,2,1,5],[1,5,2,6],[7,7,7],[9,1,8,2,7],[3,10,4,5,6],[100,50,75]]],DISTRIBUTE,[DISTRIBUTE.replace('result1[-1]>result2[-1]','result1[-1]<result2[-1]'),DISTRIBUTE.replace('result1+result2','result2+result1')],['Uses the reversed last-value comparison.','Concatenates the result arrays in the wrong order.'],distribute_oracle,random_distribute,['The rule depends only on the two current last elements.','Maintain the two result arrays directly.','Compare their tails for each next value and append to the selected array.','This mirrors every deterministic distribution step, and the final concatenation follows the required order.'],'O(n)','O(n)',3),
3074:entry('minimum_boxes_for_apples',[('apple','list[int]'),('capacity','list[int]')],'int',['arrays','sorting','greedy'],['All apples may be redistributed among available boxes.','Choose the fewest boxes whose combined capacity holds the total number of apples.','The input guarantees total capacity is sufficient.'],[([[1,3,2],[4,3,1,5,2]],'Six apples fit in the capacities five and four, so two boxes suffice.'),([[5,5,5],[2,4,2,7]],'All four boxes are needed to reach capacity fifteen.')],[[a,c] for a,c in [([1],[1]),([1],[2,3]),([1,3,2],[4,3,1,5,2]),([5,5,5],[2,4,2,7]),([10],[5,5]),([2,2],[4]),([2,2],[2,2]),([1,1,1],[10,1]),([9,1],[3,7]),([3,4,5],[6,6]),([1,2,3,4],[4,4,4]),([8,8],[20]),([6,5],[3,3,5]),([2,7,1],[1,9])]],BOXES,[BOXES.replace('reverse=True','reverse=False'),BOXES.replace('>=needed','>needed')],['Fills the smallest boxes first, which cannot minimize their count.','Requires excess capacity and rejects an exact fit.'],boxes_oracle,random_boxes,['Only total apple count matters because redistribution is unrestricted.','Sort box capacities from largest to smallest.','Accumulate them until their sum reaches the apple total.','For any fixed number of boxes, the largest capacities maximize available space, so the first sufficient prefix uses the fewest boxes.'],'O(b log b)','O(b)',3),
}
BATCH[3062]['params'][0]=('head','ListNode | None','listnode');BATCH[3062]['immutable_parameters']=[0]
BATCH[3063]['params'][0]=('head','ListNode | None','listnode');BATCH[3063]['adapter']='listnode';BATCH[3063]['immutable_parameters']=[0];BATCH[3063]['comparator']='unordered'
BATCH[3065]['wrong'][1]=THRESHOLD.replace('value<k','value>k')
BATCH[3062]['wrong'][1]='''def linked_list_pair_game(head):
    if head.val>head.next.val:return 'Even'
    if head.val<head.next.val:return 'Odd'
    return 'Tie'
'''
