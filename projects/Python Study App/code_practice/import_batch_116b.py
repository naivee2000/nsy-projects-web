"""Second reviewed group of workbook batch 116."""
import heapq,re
from itertools import combinations
from .import_batch_055 import entry

def or_o(a):
 nums=a[0];target=0
 for x in nums:target|=x
 return sum((lambda ids: __import__('functools').reduce(int.__or__,(nums[i] for i in ids),0)==target)(ids) for size in range(1,len(nums)+1) for ids in combinations(range(len(nums)),size))
def second_o(a):
 n,edges,travel,change=a;g=[[] for _ in range(n+1)]
 for x,y in edges:g[x].append(y);g[y].append(x)
 arrivals=[[] for _ in range(n+1)];q=[(0,1)]
 while q:
  elapsed,node=heapq.heappop(q)
  if arrivals[node] and arrivals[node][-1]==elapsed:continue
  if len(arrivals[node])==2:continue
  arrivals[node].append(elapsed)
  if node==n and len(arrivals[node])==2:return elapsed
  departure=elapsed
  if (departure//change)%2:departure=(departure//change+1)*change
  for neighbor in g[node]:heapq.heappush(q,(departure+travel,neighbor))
def list_o(a):return sorted(a[0])
def words_o(a):
 def valid(token):
  if any(c.isdigit() for c in token):return False
  if token.count('-')>1:return False
  if '-' in token:
   i=token.index('-')
   if i==0 or i==len(token)-1 or not token[i-1].isalpha() or not token[i+1].isalpha():return False
  return sum(c in '!.,' for c in token)<=1 and all(c.isalpha() or c=='-' or (c in '!.,' and i==len(token)-1) for i,c in enumerate(token))
 return sum(valid(t) for t in a[0].split())
def balanced_o(a):
 value=a[0]+1
 while True:
  counts={d:str(value).count(d) for d in set(str(value))}
  if all(int(d)==count for d,count in counts.items()):return value
  value+=1
def ror(r):return [[r.randint(0,31) for _ in range(r.randint(1,10))]]
def rsecond(r):
 n=r.randint(2,9);edges=[[i,r.randint(1,i-1)] for i in range(2,n+1)];present={tuple(sorted(e)) for e in edges}
 for i in range(1,n+1):
  for j in range(i+1,n+1):
   if (i,j) not in present and r.random()<.15:edges.append([i,j])
 return [n,edges,r.randint(1,6),r.randint(1,6)]
def rlist(r):
 values=sorted((r.randint(-30,30) for _ in range(r.randint(1,30))),key=abs);return [values]
def rwords(r):return [' '.join(r.choice(['cat','a-b','bad-','dog!','1x','!','a..','green']) for _ in range(r.randint(1,15)))]
def rbalanced(r):return [r.randint(0,100000)]

OR='''\
def count_maximum_or_subsets(nums):
    target=0
    for value in nums:target|=value
    answer=0
    def search(index,current):
        nonlocal answer
        if index==len(nums):
            answer+=current==target
            return
        search(index+1,current)
        search(index+1,current|nums[index])
    search(0,0)
    return answer-(target==0)
'''
SECOND='''\
def second_minimum_travel_time(n,edges,time,change):
    from collections import deque
    graph=[[] for _ in range(n+1)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    first=[10**9]*(n+1);second=[10**9]*(n+1);first[1]=0;queue=deque([(1,0)])
    while queue:
        node,steps=queue.popleft()
        for neighbor in graph[node]:
            candidate=steps+1
            if candidate<first[neighbor]:second[neighbor]=first[neighbor];first[neighbor]=candidate;queue.append((neighbor,candidate))
            elif first[neighbor]<candidate<second[neighbor]:second[neighbor]=candidate;queue.append((neighbor,candidate))
    elapsed=0
    for _ in range(second[n]):
        if (elapsed//change)%2:elapsed=(elapsed//change+1)*change
        elapsed+=time
    return elapsed
'''
LINK='''\
def sort_absolute_sorted_list(head):
    negative=None;nonnegative_dummy=ListNode(0);nonnegative=nonnegative_dummy
    node=head
    while node:
        following=node.next
        if node.val<0:node.next=negative;negative=node
        else:nonnegative.next=node;nonnegative=node;node.next=None
        node=following
    if negative is None:return nonnegative_dummy.next
    tail=negative
    while tail.next:tail=tail.next
    tail.next=nonnegative_dummy.next
    return negative
'''
WORDS='''\
def count_valid_sentence_words(sentence):
    import re
    pattern=re.compile(r'^[a-z]+(?:-[a-z]+)?[!.,]?$|^[!.,]$')
    return sum(pattern.fullmatch(token) is not None for token in sentence.split())
'''
BALANCED='''\
def next_numerically_balanced_number(n):
    candidate=n+1
    while True:
        text=str(candidate)
        if all(text.count(d)==int(d) for d in set(text)):return candidate
        candidate+=1
'''
def L(*x):return list(x)
BATCH={
2044:entry('count_maximum_or_subsets',[('nums','list[int]')],'int',['backtracking','bit manipulation','subsets'],['nums has 1 through 16 nonnegative integers.','Find the maximum bitwise OR obtainable by a nonempty index subset.','Return how many distinct index subsets attain that maximum.'],[([[3,1]],'Both subset [3] and subset [3,1] have maximum OR three, so the count is two.'),([[2,2,2]],'Every nonempty subset has OR two, yielding seven subsets.')],[[x] for x in [[0],[1],[3,1],[2,2,2],[0,0],[1,2],[1,2,3],[8,4,2,1],[5,1,5],[0,1,0],[7,7],[1,1,2,2],[3,5,6],[16,8,24]]],OR,[OR.replace('return answer-(target==0)','return answer'),OR.replace('current|nums[index]','current+nums[index]')],['Counts the empty subset when the maximum OR is zero.','Uses arithmetic addition instead of bitwise OR when including an element.'],or_o,ror,L('The target maximum is the OR of every element because OR only adds bits.','Backtrack over include/exclude choices while carrying the current OR and count leaves equal to the target.','DFS(index,current); branch without and with current|nums[index]; exclude the empty subset when target zero.','Every index subset corresponds to one leaf, and its carried value is its exact OR, so target-equal leaves count precisely the maximizing nonempty subsets.'),'O(2^n)','O(n)',5),
2045:entry('second_minimum_travel_time',[('n','int'),('edges','list[list[int]]'),('time','int'),('change','int')],'int',['graphs','breadth-first-search','shortest paths'],['The connected undirected graph has vertices 1 through n and equal edge traversal time.','All signals alternate green and red every change minutes in synchronization; departure is forbidden during red.','Return the smallest destination arrival time strictly greater than the minimum, allowing revisits.'],[([5,[[1,2],[1,3],[1,4],[3,4],[4,5]],3,5],'The second distinct arrival reaches vertex five at time thirteen.'),([2,[[1,2]],3,2],'The second route revisits the first vertex and reaches the destination at time eleven.')],[[n,e,t,c] for n,e,t,c in [(2,[[1,2]],1,1),(2,[[1,2]],3,2),(3,[[1,2],[2,3]],1,2),(3,[[1,2],[2,3],[1,3]],2,3),(5,[[1,2],[1,3],[1,4],[3,4],[4,5]],3,5),(4,[[1,2],[2,4],[1,3],[3,4]],2,2),(4,[[1,2],[2,3],[3,4]],3,4),(3,[[1,2],[1,3]],5,2),(5,[[1,2],[2,5],[1,3],[3,4],[4,5]],1,3),(6,[[1,2],[2,6],[1,3],[3,4],[4,6],[1,5]],2,5),(3,[[1,2],[2,3]],4,1),(4,[[1,4],[1,2],[2,3],[3,4]],1,10),(5,[[1,2],[2,3],[3,5],[1,4],[4,5]],5,3),(3,[[1,2],[2,3],[1,3]],1,1)]],SECOND,[SECOND.replace('first[neighbor]<candidate<second[neighbor]','first[neighbor]<=candidate<second[neighbor]'),SECOND.replace('(elapsed//change)%2','(elapsed//change)%2==0')],['Accepts another path with the same minimum step count as a distinct second arrival.','Waits during green phases instead of red phases.'],second_o,rsecond,L('With equal edge times and synchronized signals, arrival time depends only on the number of traversed edges.','BFS while retaining the two distinct smallest step counts per vertex, then simulate signal waits for the destination’s second count.','Relax candidate steps into first or strictly-between second; for each edge wait to next green when current phase is red.','Two-distance BFS enumerates walk lengths in order; deterministic synchronized waiting is monotone in length, so the second distinct hop count yields the second distinct arrival time.'),'O(n+edges)','O(n+edges)',8),
2046:entry('sort_absolute_sorted_list',[('head','ListNode | None')],'ListNode | None',['linked lists','two pointers'],['The singly linked list is sorted by nondecreasing absolute node value.','Rearrange existing nodes into nondecreasing actual value order.','Return the new head; an empty list remains empty.'],[([[0,2,-5,5,10,-10]],'Negative values appear in reverse absolute order before the nonnegative values, yielding [-10,-5,0,2,5,10].'),([[-1]],'A one-node list is already sorted.')],[[x] for x in [[],[0],[-1],[1],[-1,1],[0,-2,3],[1,-2,2,-3],[0,2,-5,5,10,-10],[-1,-2,-3],[1,2,3],[0,-1,1,-2,2],[-2,2,-4,4],[-1,2,-3,4,-5],[0,0,1,-1]]],LINK,[LINK.replace('node.next=negative;negative=node','node.next=None;negative=node'),LINK.replace('if node.val<0','if node.val<=0')],['Drops earlier negative nodes instead of prepending each new negative value.','Treats zero as negative and reverses equal zero nodes into the negative prefix.'],list_o,rlist,L('Absolute sorting means nonnegative nodes are already increasing, while negative nodes arrive from closest to zero toward most negative.','Prepend each negative node to reverse that subsequence and append each nonnegative node to a second chain, then join them.','Detach each node; negative goes to front, otherwise to nonnegative tail; connect negative tail to nonnegative head.','Reversing absolute-ordered negatives produces increasing actual values, nonnegatives retain increasing order, and every negative is no greater than every nonnegative.'),'O(n)','O(1)',5),
2047:entry('count_valid_sentence_words',[('sentence','str')],'int',['strings','regular expressions','parsing'],['Tokens are separated by spaces and may contain lowercase letters, digits, hyphens, and !., punctuation.','A valid token has no digit, at most one hyphen surrounded by lowercase letters, and at most one punctuation mark only at its end.','Return the number of valid tokens.'],[(['cat and dog'],'All three lowercase tokens are valid.'),(['!this  1-s b8d!'],'None of the three nonempty tokens satisfies all token rules.')],[[s] for s in ['a','!','cat and dog','!this  1-s b8d!','a-b','-ab','ab-','a-b.','a--b','a!','a!!','1','abc1','hello, world!','...','a.b','valid invalid- ok','c-o-d-e','x y-z !']],WORDS,[WORDS.replace('[!.,]?$','[!.,]*$'),WORDS.replace('[a-z]+(?:-[a-z]+)?','[a-z-]+')],['Allows multiple punctuation characters at the end.','Allows unrestricted or repeated hyphens without requiring letters on both sides.'],words_o,rwords,L('Token validity is a small grammar over lowercase runs, one optional internal hyphen, and one optional final punctuation mark.','Split on whitespace and match each whole token against that grammar, also allowing a punctuation-only token.','Use ^[a-z]+(?:-[a-z]+)?[!.,]?$|^[!.,]$.','Anchors require the entire token to match; the grouped optional pieces enforce every count and position rule directly.'),'O(sentence length)','O(1)',3),
2048:entry('next_numerically_balanced_number',[('n','int')],'int',['math','counting','brute force'],['0 <= n <= 1000000.','A positive integer is balanced when every digit d appearing in it occurs exactly d times.','Return the smallest balanced integer strictly greater than n.'],[([1],'The smallest balanced number greater than one is 22, where digit two appears twice.'),([1000],'The next balanced number is 1333: one occurs once and three occurs three times.')],[[n] for n in [0,1,21,22,23,99,100,300,999,1000,1333,2000,9999,100000]],BALANCED,[BALANCED.replace('candidate=n+1','candidate=n'),BALANCED.replace('text.count(d)==int(d)','text.count(d)<=int(d)')],['Starts at n itself and violates the strictly greater requirement when n is balanced.','Accepts digits that appear fewer times than their numeric value.'],balanced_o,rbalanced,L('The search range is small enough to test successive integers directly.','For each candidate, count its decimal digits and require each present digit’s frequency to equal its value.','Increment from n+1 until all(text.count(d)==int(d) for d in set(text)).','Candidates are inspected in increasing order, the predicate is exactly numerical balance, and therefore the first passing value is the required minimum.'),'O(gap*digits^2)','O(digits)',5)
}
BATCH[2046]['params'][0]=('head','ListNode | None','listnode')
BATCH[2046]['adapter']='listnode'
BATCH[2046]['wrong'][1]=LINK.replace('tail.next=nonnegative_dummy.next','tail.next=None')
BATCH[2046]['wrong_reasons'][1]='Fails to connect the reversed negative prefix to the nonnegative suffix.'
