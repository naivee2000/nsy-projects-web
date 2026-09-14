"""First reviewed group of workbook batch 116."""
from bisect import bisect_left,bisect_right
from collections import deque
from .import_batch_055 import entry

def alternating_o(a):
 nums=a[0];return max(sum(value if (i-left)%2==0 else -value for i,value in enumerate(nums[left:right],left)) for left in range(len(nums)) for right in range(left+1,len(nums)+1))
def colors_o(a):
 s=a[0];moves={'A':0,'B':0};start=0
 while start<len(s):
  end=start
  while end<len(s) and s[end]==s[start]:end+=1
  moves[s[start]]+=max(0,end-start-2);start=end
 return moves['A']>moves['B']
def idle_o(a):
 edges,patience=a;n=len(patience);graph=[[] for _ in range(n)]
 for x,y in edges:graph[x].append(y);graph[y].append(x)
 dist=[-1]*n;dist[0]=0;q=deque([0])
 while q:
  x=q.popleft()
  for y in graph[x]:
   if dist[y]<0:dist[y]=dist[x]+1;q.append(y)
 return max((2*dist[i]-1)//patience[i]*patience[i]+2*dist[i] for i in range(1,n))+1
def product_o(a):
 x,y,k=a;return sorted(v*w for v in x for w in y)[k-1]
def ascending_o(a):
 numbers=[int(token) for token in a[0].split() if token.isdigit()];return all(x<y for x,y in zip(numbers,numbers[1:]))
def ralternate(r):return [[r.randint(-30,30) for _ in range(r.randint(1,40))]]
def rcolors(r):return [''.join(r.choice('AB') for _ in range(r.randint(1,50)))]
def ridle(r):
 n=r.randint(2,15);edges=[[i,r.randrange(i)] for i in range(1,n)];return [edges,[0]+[r.randint(1,10) for _ in range(n-1)]]
def rproduct(r):
 x=sorted(r.randint(-20,20) for _ in range(r.randint(1,10)));y=sorted(r.randint(-20,20) for _ in range(r.randint(1,10)));return [x,y,r.randint(1,len(x)*len(y))]
def rascending(r):
 tokens=[]
 for _ in range(r.randint(1,15)):tokens.append(str(r.randint(1,100)) if r.random()<.4 else r.choice(['a','box','red','green']))
 return [' '.join(tokens)]

ALT='''\
def maximum_alternating_subarray_sum(nums):
    plus=nums[0];minus=float('-inf');answer=plus
    for value in nums[1:]:
        next_plus=max(value,minus+value)
        next_minus=plus-value
        plus,minus=next_plus,next_minus
        answer=max(answer,plus,minus)
    return answer
'''
COLORS='''\
def alice_wins_color_removal(colors):
    alice=bob=0;run=1
    for index in range(1,len(colors)+1):
        if index<len(colors) and colors[index]==colors[index-1]:run+=1
        else:
            if colors[index-1]=='A':alice+=max(0,run-2)
            else:bob+=max(0,run-2)
            run=1
    return alice>bob
'''
IDLE='''\
def network_idle_time(edges,patience):
    from collections import deque
    graph=[[] for _ in patience]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    distance=[-1]*len(patience);distance[0]=0;queue=deque([0])
    while queue:
        node=queue.popleft()
        for neighbor in graph[node]:
            if distance[neighbor]<0:distance[neighbor]=distance[node]+1;queue.append(neighbor)
    latest=0
    for server in range(1,len(patience)):
        round_trip=2*distance[server]
        last_send=(round_trip-1)//patience[server]*patience[server]
        latest=max(latest,last_send+round_trip)
    return latest+1
'''
PRODUCT='''\
def kth_smallest_pair_product(nums1,nums2,k):
    from bisect import bisect_left,bisect_right
    def count_at_most(limit):
        count=0
        for value in nums1:
            if value>0:count+=bisect_right(nums2,limit//value)
            elif value==0:count+=len(nums2) if limit>=0 else 0
            else:
                threshold=-((-limit)//value)
                count+=len(nums2)-bisect_left(nums2,threshold)
        return count
    low,high=-10**10,10**10
    while low<high:
        middle=(low+high)//2
        if count_at_most(middle)>=k:high=middle
        else:low=middle+1
    return low
'''
ASC='''\
def numbers_are_strictly_ascending(sentence):
    previous=-1
    for token in sentence.split():
        if token.isdigit():
            value=int(token)
            if value<=previous:return False
            previous=value
    return True
'''
def L(*x):return list(x)
BATCH={
2036:entry('maximum_alternating_subarray_sum',[('nums','list[int]')],'int',['dynamic programming','arrays'],['nums is a nonempty integer list of length up to 100000.','For a contiguous subarray, add its first value, subtract its second, and continue alternating signs.','Return the maximum alternating sum over all nonempty subarrays.'],[([[3,-1,1,2]],'The subarray [3,-1,1] has alternating sum 3-(-1)+1=5.'),([[5]],'The sole nonempty subarray has sum five.')],[[x] for x in [[1],[-1],[5],[3,-1,1,2],[1,2],[2,1],[1,2,3],[-5,-2,-3],[5,-10,5],[0,0,0],[10,1,10,1],[1,-1,1,-1],[7,3,8,2,9],[-1,5,-2,6]]],ALT,[ALT.replace('next_minus=plus-value','next_minus=minus-value'),ALT.replace('max(value,minus+value)','minus+value')],['Extends a minus-ending state with another subtraction instead of alternating back from plus.','Never starts a new subarray at the current value.'],alternating_o,ralternate,L('A subarray ending here either places the current value under a plus sign or a minus sign.','Track the best plus-ending and minus-ending states, allowing a fresh plus start.','new_plus=max(x,old_minus+x); new_minus=old_plus-x; maximize both.','These are the only legal predecessors under alternating signs, so induction covers every ending subarray and the global maximum covers every endpoint.'),'O(n)','O(1)',5),
2038:entry('alice_wins_color_removal',[('colors','str')],'bool',['game theory','strings','counting'],['colors has 1 through 100000 A/B characters.','Alice removes an interior A with A neighbors; Bob similarly removes B, and Alice moves first.','Return whether Alice wins under optimal play.'],[(['AAABABB'],'Alice has one available removal and Bob has none, so Alice wins.'),(['AA'],'Neither player can remove a piece, so Alice loses.')],[[s] for s in ['A','B','AA','AAA','BBB','AAABABB','AAABBB','AAAA','BBBB','ABABAB','AAAAABBB','AABBAA','BAAAB','ABBBA','AAAAABBBBB']],COLORS,[COLORS.replace("colors[index-1]=='A'","colors[index-1]=='B'"),COLORS.replace('alice>bob','alice>=bob')],['Attributes A-run moves to Bob and corrupts both move totals.','Treats a tie as an Alice win even though Alice runs out first.'],colors_o,rcolors,L('Removing inside a same-color run shortens only that run and never creates choices in another run.','A run of length L contributes max(0,L-2) moves to its owner; compare total Alice and Bob moves.','Scan runs, accumulate length-2 for A or B, return A_moves>B_moves.','Each move consumes one independent available interior; alternating turns means Alice wins exactly when her move supply is strictly larger.'),'O(n)','O(1)',5),
2039:entry('network_idle_time',[('edges','list[list[int]]'),('patience','list[int]')],'int',['graphs','breadth-first-search','simulation'],['edges forms a connected undirected network rooted at master server zero.','A server’s message reply returns after twice its shortest-path distance; it resends every patience seconds before that reply.','Return the first second after every reply has arrived and no message is traveling.'],[([[[0,1],[1,2]],[0,2,1]],'Server two last resends at second three and its four-second round trip returns at seven, so the network is idle at eight.'),([[[0,1]],[0,2]],'The only reply arrives at second two, making second three the first idle time.')],[[e,p] for e,p in [([[0,1]],[0,2]),([[0,1],[1,2]],[0,2,1]),([[0,1],[0,2]],[0,1,1]),([[0,1],[1,2],[2,3]],[0,10,10,10]),([[0,1],[1,2],[1,3]],[0,1,2,3]),([[0,1],[0,2],[0,3]],[0,5,5,5]),([[0,1],[1,2]],[0,4,4]),([[0,1],[1,2]],[0,1,10]),([[0,1],[0,2],[2,3]],[0,2,3,1]),([[0,1],[1,2],[2,3],[3,4]],[0,2,2,2,2]),([[0,1],[0,2],[1,3],[2,4]],[0,1,1,1,1]),([[0,1],[1,2],[0,3],[3,4]],[0,3,2,3,2]),([[0,1],[1,2],[2,3]],[0,1,1,1]),([[0,1],[1,2],[2,3],[0,4]],[0,7,3,2,1])]],IDLE,[IDLE.replace('(round_trip-1)//patience[server]','round_trip//patience[server]'),IDLE.replace('return latest+1','return latest')],['Resends at the exact reply time even though the reply has already arrived.','Returns the last busy second rather than the following first idle second.'],idle_o,ridle,L('Shortest-path distance determines each message’s fixed round-trip time.','BFS from server zero, then compute the final resend strictly before each first reply.','round=2*d; last=((round-1)//patience)*patience; final arrival=last+round; answer=max+1.','BFS gives minimum travel time, integer division identifies the greatest resend multiple below the reply, and the network becomes idle one second after the latest arrival time.'),'O(n+edges)','O(n+edges)',6),
2040:entry('kth_smallest_pair_product',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'int',['binary search','sorted arrays','math'],['nums1 and nums2 are sorted integer arrays with lengths up to 50000 and values within ±100000.','Consider all len(nums1)*len(nums2) pair products with multiplicity.','Return the one-based kth smallest product.'],[([[2,5],[3,4],2],'The products are six, eight, fifteen, and twenty; the second is eight.'),([[-4,-2,0,3],[2,4],6],'Sorted products are -16,-8,-8,-4,0,0,6,12; the sixth is zero.')],[[a,b,k] for a,b,k in [([2,5],[3,4],1),([2,5],[3,4],2),([2,5],[3,4],4),([-4,-2,0,3],[2,4],6),([-2,-1],[3,4],2),([-2,-1],[-4,-3],2),([0],[0],1),([0,1],[-1,1],2),([-5,0,5],[-2,2],3),([1,2,3],[1,2,3],5),([-3,-1,2],[-2,0,4],7),([100000],[100000],1),([-100000],[100000],1),([-2,2],[-2,2],4)]],PRODUCT,[PRODUCT.replace('bisect_right(nums2,limit//value)','bisect_left(nums2,limit//value)'),PRODUCT.replace('threshold=-((-limit)//value)','threshold=limit//value')],['Uses a strict boundary for positive products and loses values equal to the limit.','Uses floor rather than ceiling division when a negative multiplier reverses the inequality.'],product_o,rproduct,L('Binary-search a product value and count how many pairs are at most it.','For each first value, use upper bound for positive, all-or-none for zero, and a ceiling threshold with lower bound for negative.','If count(mid)>=k move high to mid, else low to mid+1.','The count is monotone in the product limit and handles inequality reversal exactly, so lower-bound search returns the smallest value with at least k products—precisely the kth product.'),'O(len(nums1)*log len(nums2)*log range)','O(1)',8),
2042:entry('numbers_are_strictly_ascending',[('sentence','str')],'bool',['strings','parsing'],['The sentence has single-space-separated word or positive-integer tokens with no leading zeros.','Read numeric tokens from left to right while ignoring words.','Return whether every number is strictly greater than the preceding number.'],[(['1 box has 3 blue 4 red 6 green and 12 yellow marbles'],'The numbers 1,3,4,6,12 are strictly increasing.'),(['hello 5 world 5'],'The repeated value five violates strict increase.')],[[s] for s in ['1 box has 3 blue 4 red 6 green and 12 yellow marbles','hello 5 world 5','no numbers here','1','1 2 3','3 2 1','a 1 b 10 c 100','a 10 b 2','5 apples','apples 5','1 a 1','9 x 10 y 11','100 then 101','2 dogs and 20 cats then 200 birds']],ASC,[ASC.replace('value<=previous','value<previous'),ASC.replace('previous=value','previous+=value')],['Allows equal consecutive numeric values despite strictness.','Adds each number to the previous threshold instead of replacing it.'],ascending_o,rascending,L('Only numeric tokens participate, but their order in the sentence must be preserved.','Split on spaces, convert digit-only tokens, and compare each with the last number.','Initialize previous below all valid values; reject value<=previous; otherwise assign previous=value.','Each numeric token is compared with its immediate numeric predecessor, whose strict increase inductively guarantees the entire sequence is increasing.'),'O(sentence length)','O(1)',3)
}
BATCH[2042]['params']=[('s','str','raw')]
