"""Second reviewed group of workbook batch 118."""
from itertools import combinations
import heapq
from .import_batch_055 import entry

def discount_o(a):
 n,roads,discounts=a;edges=[]
 for x,y,c in roads:edges.extend(((x,y,c),(y,x,c)))
 inf=10**18;dist=[[inf]*(discounts+1) for _ in range(n)];dist[0][0]=0
 for _ in range(n*(discounts+1)):
  changed=False
  for x,y,c in edges:
   for used in range(discounts+1):
    if dist[x][used]+c<dist[y][used]:dist[y][used]=dist[x][used]+c;changed=True
    if used<discounts and dist[x][used]+c//2<dist[y][used+1]:dist[y][used+1]=dist[x][used]+c//2;changed=True
  if not changed:break
 answer=min(dist[-1]);return -1 if answer==inf else answer
def even_o(a):
 digits=a[0];answer=set()
 for i in range(len(digits)):
  for j in range(len(digits)):
   for k in range(len(digits)):
    if len({i,j,k})==3 and digits[i] and digits[k]%2==0:answer.add(100*digits[i]+10*digits[j]+digits[k])
 return sorted(answer)
def middle_o(a):
 values=a[0];return values[:len(values)//2]+values[len(values)//2+1:]
def directions_o(a):
 values,start,dest=a;parent={values[0]:(None,'')};queue=[values[0]];cursor=1
 while queue and cursor<len(values):
  node=queue.pop(0)
  for direction in 'LR':
   if cursor>=len(values):break
   child=values[cursor];cursor+=1
   if child is not None:parent[child]=(node,direction);queue.append(child)
 ancestors={};node=start;ups=''
 while node is not None:ancestors[node]=ups;node=parent[node][0];ups+='U'
 down=[];node=dest
 while node not in ancestors:
  node,next_direction=parent[node];down.append(next_direction)
 return ancestors[node]+''.join(reversed(down))
def largest_even_o(a):
 nums,k=a;values=[sum(c) for c in combinations(nums,k) if sum(c)%2==0];return max(values,default=-1)
def rdiscount(r):
 n=r.randint(2,7);roads=[]
 for i in range(1,n):roads.append([i,r.randrange(i),r.randint(1,20)])
 for x,y in combinations(range(n),2):
  if r.random()<.15 and not any({x,y}=={a,b} for a,b,_ in roads):roads.append([x,y,r.randint(1,20)])
 return [n,roads,r.randint(0,3)]
def reven(r):return [[r.randint(0,9) for _ in range(r.randint(3,9))]]
def rmiddle(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]
def rdirections(r):
 n=r.randint(1,20);values=list(range(1,n+1));r.shuffle(values);start,dest=r.sample(values,2) if n>1 else (values[0],values[0]);return [values,start,dest]
def rlargest(r):
 nums=[r.randint(0,30) for _ in range(r.randint(1,10))];return [nums,r.randint(1,len(nums))]

DISCOUNT='''\
def minimum_discounted_highway_cost(n,highways,discounts):
    import heapq
    graph=[[] for _ in range(n)]
    for a,b,toll in highways:graph[a].append((b,toll));graph[b].append((a,toll))
    distances=[[float('inf')]*(discounts+1) for _ in range(n)];distances[0][0]=0;queue=[(0,0,0)]
    while queue:
        cost,city,used=heapq.heappop(queue)
        if cost!=distances[city][used]:continue
        if city==n-1:return cost
        for neighbor,toll in graph[city]:
            options=[(used,cost+toll)]
            if used<discounts:options.append((used+1,cost+toll//2))
            for next_used,next_cost in options:
                if next_cost<distances[neighbor][next_used]:
                    distances[neighbor][next_used]=next_cost;heapq.heappush(queue,(next_cost,neighbor,next_used))
    return -1
'''
EVEN='''\
def three_digit_even_numbers(digits):
    from collections import Counter
    available=Counter(digits);answer=[]
    for value in range(100,1000,2):
        needed=Counter(map(int,str(value)))
        if all(needed[digit]<=available[digit] for digit in needed):answer.append(value)
    return answer
'''
MIDDLE='''\
def delete_middle_node(head):
    if head is None or head.next is None:return None
    slow=head;fast=head.next.next
    while fast and fast.next:
        slow=slow.next;fast=fast.next.next
    slow.next=slow.next.next
    return head
'''
DIRECTIONS='''\
def tree_step_directions(root,start_value,dest_value):
    def path(node,target,steps):
        if node is None:return False
        if node.val==target:return True
        steps.append('L')
        if path(node.left,target,steps):return True
        steps[-1]='R'
        if path(node.right,target,steps):return True
        steps.pop();return False
    start=[];dest=[];path(root,start_value,start);path(root,dest_value,dest)
    shared=0
    while shared<min(len(start),len(dest)) and start[shared]==dest[shared]:shared+=1
    return 'U'*(len(start)-shared)+''.join(dest[shared:])
'''
LARGEST='''\
def largest_even_subsequence_sum(nums,k):
    chosen=sorted(nums,reverse=True)[:k];remaining=sorted(nums,reverse=True)[k:];total=sum(chosen)
    if total%2==0:return total
    odd_out=min((x for x in chosen if x%2),default=None);even_out=min((x for x in chosen if x%2==0),default=None)
    even_in=max((x for x in remaining if x%2==0),default=None);odd_in=max((x for x in remaining if x%2),default=None)
    candidates=[]
    if odd_out is not None and even_in is not None:candidates.append(total-odd_out+even_in)
    if even_out is not None and odd_in is not None:candidates.append(total-even_out+odd_in)
    return max(candidates,default=-1)
'''
def L(*x):return list(x)
BATCH={
2093:entry('minimum_discounted_highway_cost',[('n','int'),('highways','list[list[int]]'),('discounts','int')],'int',['graphs','dijkstra','state expansion'],['Highways are undirected and have nonnegative integer tolls.','Each available discount may halve one traversed toll using floor division; using fewer discounts is allowed.','Return the minimum cost from city zero to city n-1, or -1 when unreachable.'],[([5,[[0,1,4],[2,1,3],[1,4,11],[3,2,3],[3,4,2]],1],'Discounting toll eleven to five yields total cost nine.'),([3,[[0,1,5],[1,2,5]],2],'Discounting both highways costs two plus two, totaling four.')],[[n,h,d] for n,h,d in [(2,[],0),(2,[[0,1,10]],0),(2,[[0,1,10]],1),(2,[[0,1,1]],1),(3,[[0,1,4]],2),(3,[[0,1,4],[1,2,6]],1),(3,[[0,2,20],[0,1,3],[1,2,4]],1),(4,[[0,1,8],[1,3,8],[0,2,3],[2,3,20]],1),(4,[[0,1,1],[1,2,1],[2,3,1]],5),(5,[[0,4,100],[0,1,10],[1,2,10],[2,3,10],[3,4,10]],1),(3,[[0,1,0],[1,2,1]],1),(4,[[0,1,7],[2,3,7]],2),(3,[[0,1,9],[1,2,9],[0,2,20]],0),(3,[[0,1,9],[1,2,9],[0,2,20]],2)]],DISCOUNT,[DISCOUNT.replace('cost+toll//2','cost+(toll+1)//2'),DISCOUNT.replace('used<discounts','used<=discounts')],['Rounds discounted odd tolls upward instead of down.','Attempts to spend a discount after all discounts are already used.'],discount_o,rdiscount,L('The same city with different numbers of discounts used represents different future choices.','Run Dijkstra on states (city,used), relaxing every highway at full cost and, if available, half cost.','Maintain dist[n][discounts+1] and a min-heap; return when any destination state is popped.','All expanded edge weights are nonnegative, so Dijkstra finalizes the globally cheapest destination state first.'),'O((cities*discounts+highways*discounts) log(cities*discounts))','O(cities*discounts+highways)',7),
2094:entry('three_digit_even_numbers',[('digits','list[int]')],'list[int]',['recursion','counting','enumeration'],['digits contains at least three decimal digits and occurrences may repeat.','Use three distinct input positions to form a number from 100 through 999 whose last digit is even.','Return all unique qualifying numbers in increasing order.'],[([[2,1,3,0]],'The ten constructible even values are 102,120,130,132,210,230,302,310,312,320.'),([[2,2,8,8,2]],'Repeated digits permit 222,228,282,288,822,828,882.')],[[x] for x in [[0,0,0],[1,2,3],[1,2,4],[2,2,2],[1,1,2],[0,1,2],[0,0,2],[9,8,7],[4,6,8],[1,3,5],[5,0,0],[9,9,8],[1,0,0,2],[7,6,5,4]]],EVEN,[EVEN.replace('range(100,1000,2)','range(0,1000,2)'),EVEN.replace('<=available[digit]','<available[digit]')],['Includes values below one hundred with a leading zero.','Requires an extra copy of every digit and rejects valid constructions using all available copies.'],even_o,reven,L('Enumerating the 450 three-digit even values automatically guarantees uniqueness and sorted order.','For each even value, compare its digit frequency map with the available input counts.','Accept value when needed[d]<=available[d] for every digit.','The count condition is necessary and sufficient to select distinct positions matching exactly the candidate digits.'),'O(900*digits)','O(10)',3),
2095:entry('delete_middle_node',[('head','ListNode | None')],'ListNode | None',['linked lists','two pointers'],['The middle index is floor(n/2), so an even-length list removes the second of its two central nodes.','Relink the existing nodes without changing retained values.','Return the remaining head, or None for a one-node list.'],[([[1,3,4,7,1,2,6]],'Length seven has middle index three, so node seven is removed.'),([[1,2,3,4]],'The second central node at index two is removed, leaving [1,2,4].')],[[x] for x in [[1],[1,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[0,0],[-1,2,-3],[9,8,7,6,5,4],[1,1,1,1,1],[5,4,3,2,1,0],[10,20],[2,4,6,8,10,12,14],[7,0,7],[3,1,4,1,5,9]]],MIDDLE,[MIDDLE.replace('fast=head.next.next','fast=head.next'),MIDDLE.replace('slow.next=slow.next.next','slow=slow.next.next')],['Deletes the first central node for even-length lists.','Moves a local pointer instead of unlinking the middle node.'],middle_o,rmiddle,L('A fast pointer moving twice as quickly positions slow immediately before floor(n/2).','Handle length one; start fast two nodes ahead and advance slow once for each two fast steps.','Set slow.next=slow.next.next and return the original head.','When fast stops, slow has advanced exactly floor(n/2)-1 times, so its successor is the required node.'),'O(n)','O(1)',5),
2096:entry('tree_step_directions',[('root','TreeNode | None'),('start_value','int'),('dest_value','int')],'str',['trees','depth first search','lowest common ancestor'],['Tree node values are unique and both requested values exist.','Return the shortest movement string using L and R toward children and U toward a parent.','The input tree must remain unchanged.'],[([[5,1,2,3,None,6,4],3,6],'Move up from three to one, up to five, right to two, then left to six: UURL.'),([[2,1],2,1],'The destination is the root left child, so the path is L.')],[[t,s,d] for t,s,d in [([1],1,1),([1,2,3],2,3),([1,2,3],3,2),([1,2,3,4,5,6,7],4,7),([1,2,3,4,5,6,7],1,7),([1,2,3,4,5,6,7],7,1),([5,1,2,3,None,6,4],6,4),([5,1,2,3,None,6,4],4,3),([1,2,None,3],3,1),([1,None,2,None,None,3,4],3,4),([10,5,15,2,7,12,20],7,12),([8,4,10,2,6,9,12],2,6),([8,4,10,2,6,9,12],9,12),([9,3,11,1,5,10,13],5,13)]],DIRECTIONS,[DIRECTIONS.replace("return 'U'*(len(start)-shared)","return 'U'*len(start)"),DIRECTIONS.replace("steps[-1]='R'","steps.append('R')")],['Moves all the way to the root instead of only to the lowest common ancestor.','Appends R without replacing the failed L step, corrupting right-child paths.'],directions_o,rdirections,L('Root-to-node paths share a prefix ending at the lowest common ancestor.','Find the L/R path from root to each endpoint and discard their common prefix.','Use U once per remaining start step, followed by the remaining destination path.','Any shortest route must rise to the lowest common ancestor and then descend; the two suffixes encode exactly those moves.'),'O(n)','O(tree height)',6),
2098:entry('largest_even_subsequence_sum',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','sorting'],['nums contains nonnegative integers and k is from one through its length.','Choose exactly k occurrences; order does not affect their sum.','Return the maximum even sum, or -1 if no such selection exists.'],[([[4,1,5,3,1],3],'Selecting 4,5,3 gives the maximum even sum twelve.'),([[1,3,5],1],'Every one-element sum is odd, so no valid selection exists.')],[[x,k] for x,k in [([2],1),([1],1),([1,2],1),([1,2],2),([2,4,6],2),([1,3,5],2),([1,2,3,4],3),([10,9,8,7],2),([0,1,2],1),([0,1,2],2),([5,5,4,4],3),([8,1,1,1],3),([6,4,3,1],3),([2,2,1,1,0],4)]],LARGEST,[LARGEST.replace('total%2==0','total%2==1'),LARGEST.replace('min((x for x in chosen if x%2)','max((x for x in chosen if x%2)')],['Returns the unconstrained chosen sum when it is odd.','Removes the largest chosen odd value instead of the smallest, losing optimality.'],largest_even_o,rlargest,L('Begin with the k largest values; only parity can make this unconstrained optimum invalid.','If the sum is odd, swap one chosen odd for the best remaining even, or one chosen even for the best remaining odd.','Evaluate both feasible parity-changing swaps and take their maximum; otherwise return -1.','Any even size-k selection differs in parity by at least one such swap, and using the least loss in either parity class is optimal.'),'O(n log n)','O(n)',6)
}
BATCH[2093]['wrong'][1]=DISCOUNT.replace('used<discounts','used<0')
BATCH[2093]['wrong_reasons'][1]='Never uses an available discount and therefore overpays on beneficial routes.'
BATCH[2098]['boundaries'][-1]=[[9,7,5,4],3]
BATCH[2096]['boundaries'][9]=[[1,None,2,3,4],3,4]
BATCH[2095]['params'][0]=('head','ListNode | None','listnode');BATCH[2095]['adapter']='listnode'
BATCH[2096]['params'][0]=('root','TreeNode | None','treenode')
