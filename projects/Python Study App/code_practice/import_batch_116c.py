"""Third reviewed group of workbook batch 116."""
from collections import Counter,deque
from functools import lru_cache
from .import_batch_055 import entry

def score_o(a):
 parents=a[0];n=len(parents);children=[[] for _ in range(n)]
 for i in range(1,n):children[parents[i]].append(i)
 sizes=[0]*n
 def size(x):sizes[x]=1+sum(size(y) for y in children[x]);return sizes[x]
 size(0);scores=[]
 for x in range(n):
  parts=[sizes[y] for y in children[x]]
  if n-sizes[x]:parts.append(n-sizes[x])
  value=1
  for p in parts:value*=p
  scores.append(value)
 return scores.count(max(scores))
def courses_o(a):
 n,relations,times=a;before=[[] for _ in range(n)]
 for x,y in relations:before[y-1].append(x-1)
 @lru_cache(None)
 def finish(x):return times[x]+max((finish(y) for y in before[x]),default=0)
 return max(finish(i) for i in range(n))
def rows_o(a):
 words=a[0].split();k=a[1]
 @lru_cache(None)
 def dp(i):
  if i==len(words):return 0
  length=0;best=10**9
  for j in range(i,len(words)):
   length+=len(words[j])+(j>i)
   if length>k:break
   best=min(best,0 if j==len(words)-1 else (k-length)**2+dp(j+1))
  return best
 return dp(0)
def distinct_o(a):
 arr,k=a;counts=Counter(arr);values=[x for x in arr if counts[x]==1];return values[k-1] if k<=len(values) else ''
def events_o(a):
 events=a[0];best=max(v for _,_,v in events)
 for i,(s,e,v) in enumerate(events):
  for j,(s2,e2,v2) in enumerate(events):
   if i<j and (e<s2 or e2<s):best=max(best,v+v2)
 return best
def rscore(r):
 n=r.randint(2,30);return [[-1]+[r.randrange(i) for i in range(1,n)]]
def rcourses(r):
 n=r.randint(1,15);relations=[]
 for i in range(1,n+1):
  for j in range(i+1,n+1):
   if r.random()<.12:relations.append([i,j])
 return [n,relations,[r.randint(1,20) for _ in range(n)]]
def rrows(r):
 words=[''.join(r.choice('abc') for _ in range(r.randint(1,6))) for _ in range(r.randint(1,9))];k=r.randint(max(map(len,words)),15);return [' '.join(words),k]
def rdistinct(r):
 arr=[r.choice(['a','b','c','d','e']) for _ in range(r.randint(1,20))];return [arr,r.randint(1,8)]
def revents(r):
 events=[]
 for _ in range(r.randint(1,15)):
  start=r.randint(1,20);events.append([start,r.randint(start,25),r.randint(1,30)])
 return [events]

SCORE='''\
def count_highest_score_nodes(parents):
    n=len(parents);children=[[] for _ in range(n)]
    for node in range(1,n):children[parents[node]].append(node)
    best=count=0
    def visit(node):
        nonlocal best,count
        product=1;size=1
        for child in children[node]:
            child_size=visit(child);size+=child_size;product*=child_size
        if n-size:product*=n-size
        if product>best:best=product;count=1
        elif product==best:count+=1
        return size
    visit(0);return count
'''
COURSES='''\
def minimum_parallel_course_months(n,relations,time):
    graph=[[] for _ in range(n)];indegree=[0]*n
    for previous,nxt in relations:graph[previous-1].append(nxt-1);indegree[nxt-1]+=1
    from collections import deque
    queue=deque(i for i in range(n) if indegree[i]==0);finish=time[:]
    while queue:
        course=queue.popleft()
        for nxt in graph[course]:
            finish[nxt]=max(finish[nxt],finish[course]+time[nxt]);indegree[nxt]-=1
            if indegree[nxt]==0:queue.append(nxt)
    return max(finish)
'''
ROWS='''\
def minimum_sentence_row_cost(sentence,k):
    words=sentence.split();n=len(words);dp=[0]+[10**18]*n
    for end in range(1,n+1):
        length=0
        for start in range(end,0,-1):
            length+=len(words[start-1])+(start<end)
            if length>k:break
            cost=0 if end==n else (k-length)**2
            dp[end]=min(dp[end],dp[start-1]+cost)
    return dp[n]
'''
DISTINCT='''\
def kth_distinct_string(arr,k):
    counts=Counter(arr)
    for value in arr:
        if counts[value]==1:
            k-=1
            if k==0:return value
    return ''
'''
EVENTS='''\
def maximum_two_event_value(events):
    events.sort();from heapq import heappop,heappush
    ended=[];best_previous=answer=0
    for start,end,value in events:
        while ended and ended[0][0]<start:
            _,old=heappop(ended);best_previous=max(best_previous,old)
        answer=max(answer,best_previous+value);heappush(ended,(end,value))
    return answer
'''
def L(*x):return list(x)
BATCH={
2049:entry('count_highest_score_nodes',[('parents','list[int]')],'int',['trees','depth-first-search','subtree sizes'],['parents describes a rooted binary tree on nodes 0 through n-1 with parents[0]=-1.','Removing a node creates components; its score is the product of their node counts, ignoring empty components.','Return how many nodes attain the maximum score.'],[([[-1,2,0,2,0]],'Three nodes tie for the maximum component-size product.'),([[-1,0]],'Removing either node leaves one component of size one, so both tie.')],[[p] for p in [[-1,0],[-1,0,0],[-1,0,1],[-1,2,0,2,0],[-1,0,0,1],[-1,0,0,1,1,2,2],[-1,0,1,2],[-1,0,1,1,3],[-1,0,0,2,2],[-1,0,1,2,3,4],[-1,0,0,1,2,2],[-1,0,1,1,2,2,3],[-1,0,0,1,1],[-1,0,1,0,3,3]]],SCORE,[SCORE.replace('if n-size:product*=n-size','product*=n-size'),SCORE.replace('product*=child_size','product+=child_size')],['Multiplies by a zero-sized parent component at the root.','Adds child sizes instead of multiplying independent component sizes.'],score_o,rscore,L('Removing a node separates every child subtree and the remainder above it.','Compute subtree sizes postorder; multiply child sizes and n-subtree_size when nonzero.','DFS returns size; compare each component product with the global maximum and update its frequency.','The listed components are exactly those created by removal, and postorder provides every size before scoring its parent.'),'O(n)','O(height)',6),
2050:entry('minimum_parallel_course_months',[('n','int'),('relations','list[list[int]]'),('time','list[int]')],'int',['graphs','topological sorting','dynamic programming'],['Courses are numbered 1 through n; relations is an acyclic prerequisite graph.','Any number of available courses may run concurrently, and time[i] is course i+1 duration.','Return the minimum months until every course is complete.'],[([3,[[1,3],[2,3]],[3,2,5]],'Course three begins after the slower prerequisite at month three and finishes at month eight.'),([5,[[1,5],[2,5],[3,5],[3,4],[4,5]],[1,2,3,4,5]],'The longest prerequisite chain takes twelve months.')],[[n,r,t] for n,r,t in [(1,[],[5]),(2,[],[3,4]),(2,[[1,2]],[3,4]),(3,[[1,3],[2,3]],[3,2,5]),(3,[[1,2],[2,3]],[1,2,3]),(4,[[1,3],[2,3]],[2,4,5,1]),(4,[[1,2],[1,3],[2,4],[3,4]],[1,2,3,4]),(5,[[1,5],[2,5],[3,5],[3,4],[4,5]],[1,2,3,4,5]),(5,[],[5,4,3,2,1]),(4,[[1,4],[2,4],[3,4]],[10,1,1,2]),(6,[[1,2],[2,3],[4,5],[5,6]],[1,1,1,5,5,5]),(3,[[1,2],[1,3]],[10,1,1]),(5,[[1,2],[2,5],[1,3],[3,4],[4,5]],[2,2,2,2,2]),(4,[[1,2],[2,3],[3,4]],[4,3,2,1])]],COURSES,[COURSES.replace('max(finish[nxt],finish[course]+time[nxt])','finish[course]+time[nxt]'),COURSES.replace('return max(finish)','return sum(time)')],['Overwrites a course finish time with the latest processed prerequisite rather than the slowest prerequisite.','Adds all course durations and ignores concurrency.'],courses_o,rcourses,L('With unlimited concurrency, completion time is the longest weighted prerequisite path.','Process courses topologically, propagating the maximum predecessor finish plus the next duration.','Initialize sources with own durations; relax finish[v]=max(finish[v],finish[u]+time[v]).','Topological order finalizes every predecessor before its dependents, and the maximum incoming path is exactly the earliest possible dependent start.'),'O(n+relations)','O(n+relations)',8),
2052:entry('minimum_sentence_row_cost',[('sentence','str'),('k','int')],'int',['dynamic programming','strings'],['sentence contains space-separated words, each no longer than k.','Rows preserve word order, use one space between adjacent words, and have at most k characters.','Each nonfinal row costs (k-length)^2; the last row costs zero.'],[(['i love leetcode',12],'The optimal split places i love on the first row for cost (12-6)^2=36 and leetcode last for zero.'),(['a b c',3],'Using a b first and c last gives zero total cost.')],[[s,k] for s,k in [('a',1),('a b',1),('a b',3),('a b c',3),('i love leetcode',12),('hello world',5),('one two three',7),('aa bb cc',5),('a bb ccc',4),('abcd e f',4),('x y z w',3),('long short tiny',10),('a aa aaa aaaa',6),('code practice every day',13)]],ROWS,[ROWS.replace('cost=0 if end==n','cost=(k-length)**2 if end==n'),ROWS.replace('length+=len(words[start-1])+(start<end)','length+=len(words[start-1])')],['Charges unused space on the final row even though it is free.','Omits spaces between words when measuring row length.'],rows_o,rrows,L('The cost of a row depends only on its first and last word, enabling prefix dynamic programming.','Let dp[end] be minimum cost through word end; scan possible starts backward until the row exceeds k.','dp[end]=min(dp[start-1]+row_cost), using zero row_cost when end is the final word.','Every layout has a unique final-row start, so the recurrence considers every valid last break and combines it with an optimal preceding layout.'),'O(words^2)','O(words)',5),
2053:entry('kth_distinct_string',[('arr','list[str]'),('k','int')],'str',['hash maps','strings','counting'],['arr has 1 through 1000 strings and k is positive.','A distinct string appears exactly once in the full array.','Return the kth distinct string in original order, or empty string if fewer exist.'],[([['d','b','c','b','c','a'],2],'The distinct strings are d then a, so the second is a.'),([['aaa','aa','a'],1],'Every string appears once and aaa is first.')],[[a,k] for a,k in [(['a'],1),(['a'],2),(['d','b','c','b','c','a'],2),(['aaa','aa','a'],1),(['a','a'],1),(['a','b'],2),(['x','y','x','z'],1),(['x','y','x','z'],2),(['1','2','2','3'],2),(['same','same','other'],1),(['a','b','c'],3),(['a','b','c'],4),(['red','blue','red','green','blue','gold'],2),(['z','a','z','b'],2)]],DISTINCT,[DISTINCT.replace('counts[value]==1','counts[value]>=1'),DISTINCT.replace('return value','return arr[k-1]')],['Treats repeated strings as distinct occurrences.','Returns the kth raw array entry instead of the kth globally unique string.'],distinct_o,rdistinct,L('Distinctness depends on the entire array, but kth order depends on the original traversal.','Count all strings first, then scan again and decrement k only at frequency one.','On count[value]==1, k-=1 and return when k reaches zero; otherwise return empty.','The scan filters exactly the distinct strings without reordering them, making its kth accepted item the required result.'),'O(total characters)','O(unique strings)',3),
2054:entry('maximum_two_event_value',[('events','list[list[int]]')],'int',['sorting','heaps','intervals'],['Each event is [start,end,value] with inclusive endpoints and positive value.','Choose at most two events; two chosen events require the later start to be strictly greater than the earlier end.','Return the maximum total value.'],[([[[1,3,2],[4,5,2],[2,4,3]]],'The first two events do not overlap and total four.'),([[[1,3,2],[4,5,2],[1,5,5]]],'Taking the single value-five event is better than the compatible pair worth four.')],[[e] for e in [[[1,2,1]],[[1,3,2],[4,5,2],[2,4,3]],[[1,3,2],[4,5,2],[1,5,5]],[[1,1,5],[2,2,6]],[[1,2,5],[2,3,6]],[[1,10,100],[2,3,60],[4,5,60]],[[1,2,3],[3,4,4]],[[1,2,3],[2,2,10],[3,4,3]],[[5,6,1],[1,2,10],[3,4,20]],[[1,5,5],[6,10,5]],[[1,4,8],[5,5,9],[5,7,20]],[[1,1,1],[1,1,2],[2,2,3]],[[10,20,7],[1,9,8],[21,30,9]],[[2,8,4],[9,10,3],[1,1,10]]]],EVENTS,[EVENTS.replace('ended[0][0]<start','ended[0][0]<=start'),EVENTS.replace('answer=max(answer,best_previous+value)','answer=max(answer,best_previous)')],['Allows events sharing an inclusive endpoint to be selected together.','Forgets to add the current event value to the best compatible prior value.'],events_o,revents,L('Sort by start and maintain completed earlier events ordered by end.','Before each start, move all events ending strictly earlier into a best-prior value, then combine it with the current value.','Pop heap while end<start, update best_previous, and maximize best_previous+value.','The heap exposes exactly compatible prior events; the stored maximum is their best value, so each possible later event forms its optimal pair when processed.'),'O(n log n)','O(n)',5)
}
