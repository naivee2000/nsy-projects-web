"""Graph and dynamic-programming workbook batch 139."""

from collections import deque
from .import_batch_055 import entry

def meeting_oracle(args):
    edges,node1,node2=args
    def distances(start):
        result={};node=start;steps=0
        while node!=-1 and node not in result:result[node]=steps;node=edges[node];steps+=1
        return result
    first,second=distances(node1),distances(node2);common=set(first)&set(second)
    return min(common,key=lambda node:(max(first[node],second[node]),node)) if common else -1

def random_meeting(rng):
    n=rng.randint(2,18);edges=[]
    for i in range(n):edges.append(rng.choice([-1]+[j for j in range(n) if j!=i]))
    return [edges,rng.randrange(n),rng.randrange(n)]

def scheduler_oracle(args):
    tasks,space=args;last={};day=0
    for task in tasks:
        day+=1
        while task in last and day-last[task]<=space:day+=1
        last[task]=day
    return day

def random_scheduler(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,30))],rng.randint(1,8)]

def reachable_oracle(args):
    n,edges,restricted=args;blocked=set(restricted);graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    seen={0};queue=deque([0])
    while queue:
        node=queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in blocked and neighbor not in seen:seen.add(neighbor);queue.append(neighbor)
    return len(seen)

def random_reachable(rng):
    n=rng.randint(2,25);edges=[[node,rng.randrange(node)] for node in range(1,n)]
    return [n,edges,rng.sample(range(1,n),rng.randint(0,min(n-1,8)))]

def partition_oracle(args):
    nums=args[0]
    def search(index):
        if index==len(nums):return True
        if index+2<=len(nums) and nums[index]==nums[index+1] and search(index+2):return True
        if index+3<=len(nums):
            a,b,c=nums[index:index+3]
            if (a==b==c or (b==a+1 and c==b+1)) and search(index+3):return True
        return False
    return search(0)

def random_partition(rng):return [[rng.randint(1,7) for _ in range(rng.randint(2,14))]]

def ideal_oracle(args):
    text,k=args;best=0
    for mask in range(1<<len(text)):
        candidate=[text[i] for i in range(len(text)) if mask>>i&1]
        if all(abs(ord(candidate[i])-ord(candidate[i-1]))<=k for i in range(1,len(candidate))):best=max(best,len(candidate))
    return best

def random_ideal(rng):return [''.join(rng.choice('abcdefgh') for _ in range(rng.randint(1,12))),rng.randint(0,7)]

MEETING='''\
def closest_meeting_node(edges,node1,node2):
    def walk(start):
        distance=[-1]*len(edges);steps=0
        while start!=-1 and distance[start]==-1:
            distance[start]=steps;steps+=1;start=edges[start]
        return distance
    first,second=walk(node1),walk(node2);answer=-1;best=10**30
    for node in range(len(edges)):
        if first[node]!=-1 and second[node]!=-1 and max(first[node],second[node])<best:
            best=max(first[node],second[node]);answer=node
    return answer
'''

SCHEDULER='''\
def minimum_task_days(tasks,space):
    next_day={};day=0
    for task in tasks:
        day=max(day+1,next_day.get(task,1));next_day[task]=day+space+1
    return day
'''

REACHABLE='''\
def reachable_nodes_without_restrictions(n,edges,restricted):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    seen=set(restricted);stack=[0];seen.add(0);answer=0
    while stack:
        node=stack.pop();answer+=1
        for neighbor in graph[node]:
            if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
    return answer
'''

PARTITION='''\
def has_valid_array_partition(nums):
    possible=[False]*(len(nums)+1);possible[0]=True
    for end in range(2,len(nums)+1):
        if possible[end-2] and nums[end-2]==nums[end-1]:possible[end]=True
        if end>=3 and possible[end-3]:
            a,b,c=nums[end-3:end]
            if a==b==c or (b==a+1 and c==b+1):possible[end]=True
    return possible[-1]
'''

IDEAL='''\
def longest_ideal_subsequence(s,k):
    best=[0]*26
    for character in s:
        value=ord(character)-97
        length=1+max(best[max(0,value-k):min(26,value+k+1)],default=0)
        best[value]=max(best[value],length)
    return max(best,default=0)
'''

BATCH={
2359:entry('closest_meeting_node',[('edges','list[int]'),('node1','int'),('node2','int')],'int',['graphs','functional graphs'],['Node i has one directed edge to edges[i], or no outgoing edge when edges[i] is -1.','Among nodes reachable from both starts, minimize the larger of the two path distances.','Break equal maximum distances by returning the smaller node index; return -1 if no common node exists.'],[([[2,2,3,-1],0,1],'Both starts reach node 2 in one step, so its maximum distance is one and it is optimal.'),([[1,2,-1],0,2],'Node 2 is reachable from both starts; its distances are two and zero, so the answer is 2.')],[[e,a,b] for e,a,b in [([-1,-1],0,1),([1,-1],0,1),([1,0],0,1),([1,0,1],0,2),([1,2,3,-1],0,1),([1,0,3,2],0,2),([2,-1,3,4,-1],0,1),([2,3,3,-1],0,1),([1,2,3,4,-1],1,0),([3,3,4,2,-1],0,1),([1,2,0,2],3,1),([-1],0,0),([2,0,3,-1],1,0),([1,3,3,-1],0,2)]],MEETING,[MEETING.replace('<best','<=best'),MEETING.replace('max(first[node],second[node])','first[node]+second[node]')],['Overwrites an equal-quality answer with a larger index.','Minimizes the sum of distances instead of the required maximum.'],meeting_oracle,random_meeting,['Walk forward from each start and record the first distance to every visited node.','Stop a walk at -1 or at a previously visited node, which also handles cycles.','Scan node indexes in ascending order and keep a common node only when its maximum distance strictly improves.','The two walks give exact reachable distances; the scan evaluates the objective for every common node and its strict update preserves the smallest-index tie break.'],'O(n)','O(n)',5),
2365:entry('minimum_task_days',[('tasks','list[int]'),('space','int')],'int',['arrays','hash maps','simulation'],['Tasks must be completed in their given order.','After performing a task type, at least space full days must pass before that type can run again.','Each day either performs the next task or is idle; return the earliest finishing day.'],[([[1,2,1,2,3,1],3],'Tasks 1,2,1,2,3,1 can run on days 1,2,5,6,7,9, so nine days are required.'),([[5,8,8,5],2],'Run task 5 on day 1, task 8 on day 2, wait through days 3 and 4, then finish on days 5 and 6.')],[[t,s] for t,s in [([1],1),([1,1],1),([1,1],5),([1,2,3],3),([1,2,1],1),([1,2,1],2),([1,1,1],2),([1,2,3,1,2,3],2),([4,4,5,4],3),([1,2,2,1],1),([7,8,7,8],4),([1,2,3,2,1],2),([9]*8,1),([3,1,3,1,3],3)]],SCHEDULER,[SCHEDULER.replace('day+space+1','day+space'),SCHEDULER.replace('max(day+1','max(day')],['Allows only space-1 complete rest days between equal tasks.','Can schedule consecutive different tasks on the same day.'],scheduler_oracle,random_scheduler,['Track the first legal future day for each task type.','For the next task, choose the later of the following calendar day and that task’s stored legal day.','After scheduling it, store current day + space + 1 as its next legal day.','Waiting longer can never help later ordered tasks, so choosing the earliest legal day greedily gives the minimum completion day.'],'O(n)','O(u)',5),
2368:entry('reachable_nodes_without_restrictions',[('n','int'),('edges','list[list[int]]'),('restricted','list[int]')],'int',['trees','graphs','depth-first search'],['The n nodes and n-1 undirected edges form a tree rooted for this task at node 0.','A traversal may not enter any node listed in restricted; node 0 is never restricted.','Return how many nodes remain reachable from node 0.'],[([7,[[0,1],[1,2],[3,1],[4,0],[0,5],[5,6]],[4,5]],'Blocking nodes 4 and 5 also cuts off node 6; nodes 0,1,2,3 remain reachable, giving four.'),([3,[[0,1],[1,2]],[1]],'Restricted node 1 blocks both itself and the path to node 2, leaving only node 0.')],[[n,e,r] for n,e,r in [(2,[[0,1]],[]),(2,[[0,1]],[1]),(4,[[0,1],[0,2],[0,3]],[2]),(5,[[0,1],[1,2],[2,3],[3,4]],[4]),(5,[[0,1],[1,2],[2,3],[3,4]],[1]),(6,[[0,1],[0,2],[1,3],[1,4],[2,5]],[3,5]),(7,[[0,1],[1,2],[2,3],[0,4],[4,5],[5,6]],[2,5]),(3,[[0,1],[0,2]],[1,2]),(8,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7]],[4,6]),(4,[[0,1],[1,2],[1,3]],[]),(9,[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8]],[3]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]],[2,4]),(5,[[0,1],[0,2],[2,3],[2,4]],[3]),(10,[[1,0],[2,0],[3,1],[4,1],[5,2],[6,2],[7,3],[8,3],[9,4]],[7,8,9])]],REACHABLE,[REACHABLE.replace('seen=set(restricted)','seen=set()'),REACHABLE.replace('seen.add(0);answer=0','answer=0')],['Ignores the restricted set and visits every node.','Does not mark node 0 before traversal, so it is revisited through a child.'],reachable_oracle,random_reachable,['Build adjacency lists for the undirected tree.','Initialize the visited set with every restricted node so traversal can never enter one.','Traverse from node 0, marking each newly discovered neighbor and counting popped nodes.','A tree node is reachable exactly when the traversal can follow its unique path from 0 without encountering a blocked node.'],'O(n)','O(n)',5),
2369:entry('has_valid_array_partition',[('nums','list[int]')],'bool',['arrays','dynamic programming'],['Partition the entire array into contiguous groups with no unused elements.','A valid group is either two equal values, three equal values, or three consecutive increasing values.','For an increasing triple [a,b,c], require b=a+1 and c=b+1.'],[([[4,4,4,5,6]],'Split the array as [4,4] and [4,5,6]; both groups satisfy an allowed rule.'),([[1,1,1,2]],'Neither taking [1,1] nor [1,1,1] leaves a valid group for the remaining suffix, so no full partition exists.')],[[x] for x in [[1,1],[1,2],[1,1,1],[1,2,3],[3,2,1],[1,1,2,2],[1,2,3,4,5,6],[1,1,1,1],[2,2,3,4,5],[5,5,5,6,7],[1,3,5],[7,7,7,8,9,9,9],[1,2,3,3,3],[4,4,5,6,6,6]]],PARTITION,[PARTITION.replace('nums[end-2]==nums[end-1]','nums[end-2]<=nums[end-1]'),PARTITION.replace("a==b==c or (b==a+1 and c==b+1)","a==b==c")],['Incorrectly accepts any nondecreasing pair instead of two equal values.','Omits the allowed three-consecutive-values group.'],partition_oracle,random_partition,['Let possible[i] mean that the first i values have a valid complete partition.','A matching pair extends possible[i-2].','An equal or consecutive triple extends possible[i-3].','Every legal final group has length two or three, so these transitions examine every possible last group and no invalid split.'],'O(n)','O(n)',5),
2370:entry('longest_ideal_subsequence',[('s','str'),('k','int')],'int',['strings','dynamic programming'],['Choose a subsequence without changing character order.','Adjacent chosen letters may differ by at most k in alphabet position.','Return the maximum possible subsequence length.'],[(['acfgbd',2],'One longest valid subsequence is a,c,b,d; every adjacent alphabet difference is at most two, so the length is four.'),(['abcd',0],'With zero allowed difference, only identical adjacent chosen letters are valid; each letter occurs once, so the answer is one.')],[[s,k] for s,k in [('a',0),('aaaa',0),('abc',1),('az',25),('az',24),('ace',2),('ace',1),('leetcode',3),('xyzabc',2),('ababab',0),('dcba',1),('abczdef',3),('zzzaaa',25),('badcfe',1)]],IDEAL,[IDEAL.replace('value+k+1','value+k'),IDEAL.replace('max(0,value-k)','max(0,value-k+1)')],['Excludes letters exactly k positions above the current letter.','Excludes letters exactly k positions below the current letter.'],ideal_oracle,random_ideal,['Store the best ideal-subsequence length ending at each of the 26 letters.','For the current letter x, inspect prior ending letters in the inclusive range x-k through x+k.','Extend the best compatible subsequence by one and update the slot for x.','Every valid predecessor is in that range, and retaining only the best length per ending letter is sufficient for all future extensions.'],'O(26n)','O(1)',5),
}
