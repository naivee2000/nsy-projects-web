"""First reviewed group of workbook batch 118."""
from collections import deque
from .import_batch_055 import entry

def pyramids_o(a):
 grid=a[0];rows=len(grid);cols=len(grid[0]);answer=0
 for direction in (1,-1):
  for r in range(rows):
   for c in range(cols):
    height=2
    while True:
     cells=[(r+direction*d,c+x) for d in range(height) for x in range(-d,d+1)]
     if all(0<=x<rows and 0<=y<cols and grid[x][y] for x,y in cells):answer+=1;height+=1
     else:break
 return answer
def indices_o(a):
 nums,target=a;return [i for i,x in enumerate(sorted(nums)) if x==target]
def averages_o(a):
 nums,k=a;width=2*k+1
 return [-1 if i<k or i+k>=len(nums) else sum(nums[i-k:i+k+1])//width for i in range(len(nums))]
def delete_o(a):
 nums=a[0];lo=nums.index(min(nums));hi=nums.index(max(nums));n=len(nums)
 best=n
 for left in range(n+1):
  for right in range(n+1-left):
   kept=set(range(left,n-right))
   if lo not in kept and hi not in kept:best=min(best,left+right)
 return best
def secret_o(a):
 n,meetings,first=a;know={0,first}
 for time in sorted({m[2] for m in meetings}):
  edges=[m[:2] for m in meetings if m[2]==time];changed=True
  while changed:
   changed=False
   for x,y in edges:
    if (x in know) != (y in know):know|={x,y};changed=True
 return sorted(know)
def rpyramids(r):
 rows,cols=r.randint(1,6),r.randint(1,7)
 return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def rindices(r):return [[r.randint(-5,5) for _ in range(r.randint(1,30))],r.randint(-5,5)]
def raverages(r):
 nums=[r.randint(0,30) for _ in range(r.randint(1,30))];return [nums,r.randint(0,15)]
def rdelete(r):
 n=r.randint(1,8);return [r.sample(range(-20,21),n)]
def rsecret(r):
 n=r.randint(2,8);meet=[]
 for _ in range(r.randint(1,12)):
  x,y=r.sample(range(n),2);meet.append([x,y,r.randint(1,6)])
 return [n,meet,r.randint(1,n-1)]

PYRAMIDS='''\
def count_fertile_pyramids(grid):
    rows,cols=len(grid),len(grid[0]);answer=0
    down=[[0]*cols for _ in range(rows)]
    for row in range(rows-1,-1,-1):
        for col in range(cols):
            if not grid[row][col]:continue
            down[row][col]=1
            if row+1<rows and 0<col<cols-1:down[row][col]+=min(down[row+1][col-1],down[row+1][col],down[row+1][col+1])
            answer+=down[row][col]-1
    up=[[0]*cols for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            if not grid[row][col]:continue
            up[row][col]=1
            if row>0 and 0<col<cols-1:up[row][col]+=min(up[row-1][col-1],up[row-1][col],up[row-1][col+1])
            answer+=up[row][col]-1
    return answer
'''
INDICES='''\
def sorted_target_indices(nums,target):
    smaller=sum(value<target for value in nums);equal=sum(value==target for value in nums)
    return list(range(smaller,smaller+equal))
'''
AVERAGES='''\
def k_radius_averages(nums,k):
    width=2*k+1;answer=[-1]*len(nums)
    if width>len(nums):return answer
    window=sum(nums[:width]);answer[k]=window//width
    for right in range(width,len(nums)):
        window+=nums[right]-nums[right-width];answer[right-k]=window//width
    return answer
'''
DELETE='''\
def remove_minimum_and_maximum(nums):
    first,last=sorted((nums.index(min(nums)),nums.index(max(nums))))
    n=len(nums)
    return min(last+1,n-first,first+1+n-last)
'''
SECRET='''\
def people_with_secret(n,meetings,first_person):
    from collections import deque
    knows=[False]*n;knows[0]=knows[first_person]=True
    meetings=sorted(meetings,key=lambda meeting:meeting[2]);index=0
    while index<len(meetings):
        end=index;time=meetings[index][2];graph={}
        while end<len(meetings) and meetings[end][2]==time:
            x,y,_=meetings[end];graph.setdefault(x,[]).append(y);graph.setdefault(y,[]).append(x);end+=1
        queue=deque(person for person in graph if knows[person]);seen=set(queue)
        while queue:
            person=queue.popleft();knows[person]=True
            for neighbor in graph[person]:
                if neighbor not in seen:seen.add(neighbor);queue.append(neighbor)
        index=end
    return [person for person,value in enumerate(knows) if value]
'''
def L(*x):return list(x)
BATCH={
2088:entry('count_fertile_pyramids',[('grid','list[list[int]]')],'int',['matrices','dynamic programming'],['grid is a nonempty rectangular binary matrix.','A pyramid has a fertile apex and successively wider fully fertile rows; an inverse pyramid points upward.','Count both orientations with height at least two.'],[([[[0,1,1,0],[1,1,1,1]]],'There is one downward and one upward height-two pyramid.'),([[[1,1,1],[1,1,1],[1,1,1]]],'The full 3-by-3 grid contains four height-two and two additional nested pyramids.')],[[g] for g in [[[1]],[[0]],[[1,1]],[[1],[1]],[[0,1,0],[1,1,1]],[[1,1,1],[0,1,0]],[[1,0,1],[1,1,1]],[[1,1,1],[1,0,1]],[[1,1,1,1],[1,1,1,1]],[[0,1,0],[1,1,1],[1,1,1]],[[1,1,1],[1,1,1],[0,1,0]],[[0,1,0,0],[1,1,1,0],[1,1,1,1]],[[1,0,1],[0,1,0],[1,1,1]],[[1,1,0,1],[1,1,1,1],[1,1,1,1]]]],PYRAMIDS,[PYRAMIDS.replace("answer+=down[row][col]-1","answer+=down[row][col]"),PYRAMIDS.replace('min(up[row-1][col-1],up[row-1][col],up[row-1][col+1])','max(up[row-1][col-1],up[row-1][col],up[row-1][col+1])')],['Counts height-one cells as pyramids.','Uses the strongest parent arm rather than requiring all three cells of the prior layer.'],pyramids_o,rpyramids,L('For each apex, only the minimum supported height among the three cells in the next row can extend it.','Run one DP bottom-up for downward pyramids and one top-down for inverse pyramids.','dp=1+min(three supporting neighbors); add dp-1 at each fertile cell.','A height h pyramid exists exactly when all three supporting subpyramids reach height h-1, and dp-1 counts every permitted height at that apex.'),'O(rows*cols)','O(rows*cols)',8),
2089:entry('sorted_target_indices',[('nums','list[int]'),('target','int')],'list[int]',['arrays','counting','sorting'],['nums is nonempty.','After conceptual nondecreasing sorting, return every index occupied by target.','Return indices in increasing order, or an empty list when target is absent.'],[([[1,2,5,2,3],2],'Two values are smaller than neither target? After sorting, the two target values occupy indices one and two.'),([[1,2,5,2,3],4],'Four is absent, so no sorted index qualifies.')],[[x,t] for x,t in [([1],1),([1],2),([2,2],2),([3,1,2],2),([5,4,3,2,1],3),([0,-1,0],0),([1,1,1],1),([1,2,3],0),([1,2,3],4),([2,1,2,1],1),([9,7,9,8],9),([-3,-2,-1],-2),([4,4,2,4],4),([10,0,5,5],5)]],INDICES,[INDICES.replace('value<target','value<=target'),INDICES.replace('smaller+equal','smaller+equal-1')],['Counts target values as smaller and shifts the output interval right.','Drops the final matching index with an exclusive-end off-by-one error.'],indices_o,rindices,L('Sorting is unnecessary when only the target block boundaries are needed.','Count values smaller than target and values equal to target.','Return range(smaller,smaller+equal).','In sorted order all smaller values precede exactly the equal values, so that interval contains precisely every target index.'),'O(n)','O(output)',3),
2090:entry('k_radius_averages',[('nums','list[int]'),('k','int')],'list[int]',['arrays','sliding windows'],['For center i, use the 2*k+1 elements from i-k through i+k.','Use floor integer division for the nonnegative window sum; positions without a full window receive -1.','Return one value per input element.'],[([[7,4,3,9,1,8,5,2,6],3],'Only centers three through five have full seven-value windows, producing 5,4,4.'),([[100000],0],'Radius zero uses the element itself as its average.')],[[x,k] for x,k in [([1],1),([1,2],1),([1,2,3],1),([1,2,3,4],1),([1,2,3,4,5],2),([0,0,0],1),([5,5,5,5,5],1),([1,9,1],1),([10,20,30,40,50],1),([1,2,3],0),([8,1,6,3,5,7],2),([100,0,0,0,100],2),([2,4,6,8,10,12,14],3),([9,8,7,6],5)]],AVERAGES,[AVERAGES.replace('width=2*k+1','width=2*k'),AVERAGES.replace('answer[right-k]','answer[right-k-1]')],['Uses a window of 2*k instead of including both endpoints and the center.','Writes each completed window average to the preceding center.'],averages_o,raverages,L('Consecutive radius windows differ by one outgoing and one incoming value.','Initialize the first full window, then slide its sum while writing at each center.','width=2*k+1; answer[k]=sum(first width)//width; for each next right update sum and answer[right-k].','The maintained sum is exactly the current centered window, and untouched boundary entries correctly remain -1.'),'O(n)','O(n)',5),
2091:entry('remove_minimum_and_maximum',[('nums','list[int]')],'int',['arrays','greedy'],['nums is nonempty and all values are distinct.','One deletion removes the current first or current last element.','Return the minimum deletions needed to remove both the original minimum and maximum.'],[([[2,10,7,5,4,1,8,6]],'Removing three from the front and two from the back removes both extremes in five deletions.'),([[0,-4,19,1,8,-2,-3,5]],'Removing three elements from the back and two from the front is optimal.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[3,2,1],[2,1,3],[3,1,2],[1,5,2,3,4],[5,1,2,3,4],[1,2,3,4,5],[-5,0,9],[9,0,-5],[4,-2,8,1],[6,2,9,1,7]]],DELETE,[DELETE.replace('last+1','first+1'),DELETE.replace('first+1+n-last','first+n-last')],['Uses the earlier extreme for a front-only strategy and may leave the later extreme.','Misses one deletion when removing from both ends.'],delete_o,rdelete,L('Only three strategies can be optimal: both from front, both from back, or one from each end.','Sort the two extreme indices as first and last, then evaluate those three deletion counts.','Take min(last+1, n-first, first+1+n-last).','Any valid end-deletion sequence falls into one of these strategies; each formula is the exact minimum within its class.'),'O(n)','O(1)',5),
2092:entry('people_with_secret',[('n','int'),('meetings','list[list[int]]'),('first_person','int')],'list[int]',['graphs','breadth first search','sorting'],['Person zero tells first_person at time zero.','At one timestamp, the secret may propagate through any connected chain of meetings at that same time.','Return all people who know the secret after processing every timestamp.'],[([6,[[1,2,5],[2,3,8],[1,5,10]],1],'The secret reaches two at time five, three at eight, and five at ten.'),([4,[[3,1,3],[1,2,2],[0,3,3]],3],'At time two person one does not yet know; at time three zero and three spread through the simultaneous component.')],[[n,m,f] for n,m,f in [(2,[[0,1,1]],1),(3,[[1,2,1]],1),(3,[[1,2,1]],2),(4,[[1,2,2],[2,3,2]],1),(4,[[1,2,2],[2,3,1]],1),(5,[[2,3,1],[1,2,2]],1),(5,[[1,2,1],[3,4,1]],1),(6,[[1,2,5],[2,3,8],[1,5,10]],2),(4,[[0,2,5],[1,3,5],[2,3,5]],1),(5,[[0,4,4],[4,3,4],[3,2,4]],1),(3,[[0,2,2],[1,2,1]],1),(6,[[4,5,1],[2,4,2],[1,2,3]],1),(5,[[0,2,3],[3,4,2],[2,3,3]],1),(4,[[1,2,1],[1,2,2],[2,3,2]],1)]],SECRET,[SECRET.replace('queue=deque(person for person in graph if knows[person])','queue=deque([meetings[index][0]] if knows[meetings[index][0]] else [])'),SECRET.replace('knows[person]=True','knows[person]=False')],['Starts propagation from only one meeting endpoint and misses another informed component at the same time.','Clears knowledge while traversing instead of recording newly informed people.'],secret_o,rsecret,L('Meetings at the same timestamp must be processed together because propagation is instantaneous within that group.','Sort by time; build a temporary graph for one timestamp and BFS from every participant who already knows.','Mark every vertex reachable in that time-local graph, then discard it and advance to the next time.','Reachability exactly captures all simultaneous chains, while separating timestamps prevents information from traveling backward in time.'),'O(meetings log meetings)','O(meetings+n)',8)
}
BATCH[2092]['comparator']='unordered'
