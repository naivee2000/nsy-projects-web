"""Fourth reviewed group of workbook batch 108."""
from collections import Counter
from .import_batch_055 import entry
def product_o(a):
 nums=a[0];return max(min(nums[left:right+1])*sum(nums[left:right+1]) for left in range(len(nums)) for right in range(left,len(nums)))%(10**9+7)
def color_o(a):
 colors,edges=a;n=len(colors);graph=[[] for _ in range(n)]
 for start,end in edges:graph[start].append(end)
 state=[0]*n;cycle=False;best=0
 def visit(node,counts):
  nonlocal cycle,best
  if state[node]==1:cycle=True;return
  counts=counts.copy();counts[colors[node]]+=1;best=max(best,max(counts.values()));state[node]=1
  for nxt in graph[node]:visit(nxt,counts)
  state[node]=0
 for node in range(n):visit(node,Counter())
 return -1 if cycle else best
def word_o(a):
 words=set(a[0]);valid=[word for word in words if all(word[:length] in words for length in range(1,len(word)+1))];return min(valid,key=lambda word:(-len(word),word),default='')
def sentence_o(a):return ' '.join(word[:-1] for word in sorted(a[0].split(),key=lambda word:int(word[-1])))
def memory_o(a):
 first,second=a;second_number=1
 while max(first,second)>=second_number:
  if first>=second:first-=second_number
  else:second-=second_number
  second_number+=1
 return [second_number,first,second]
def rproduct(r):return [[r.randint(1,15) for _ in range(r.randint(1,12))]]
def rcolor(r):
 n=r.randint(1,8);colors=''.join(r.choice('abcd') for _ in range(n));edges=[]
 for left in range(n):
  for right in range(n):
   if left!=right and r.random()<.12:edges.append([left,right])
 return [colors,edges]
def rword(r):return [[''.join(r.choice('abc') for _ in range(r.randint(1,5))) for _ in range(r.randint(1,15))]]
def rsentence(r):
 count=r.randint(1,9);words=[r.choice(['One','cat','word','Hi'])+str(i+1) for i in range(count)];r.shuffle(words);return [' '.join(words)]
def rmemory(r):return [r.randint(0,100),r.randint(0,100)]
PRODUCT='''def maximum_subarray_min_product(nums):
 prefix=[0]
 for value in nums:prefix.append(prefix[-1]+value)
 stack=[];answer=0
 for index in range(len(nums)+1):
  current=nums[index] if index<len(nums) else 0
  while stack and nums[stack[-1]]>=current:
   middle=stack.pop();left=stack[-1]+1 if stack else 0;answer=max(answer,nums[middle]*(prefix[index]-prefix[left]))
  stack.append(index)
 return answer%(10**9+7)
'''
COLOR='''def largest_directed_path_color_value(colors, edges):
 from collections import deque
 n=len(colors);graph=[[] for _ in range(n)];degree=[0]*n
 for start,end in edges:graph[start].append(end);degree[end]+=1
 queue=deque(index for index in range(n) if degree[index]==0);counts=[[0]*26 for _ in range(n)];seen=0;answer=0
 while queue:
  node=queue.popleft();seen+=1;color=ord(colors[node])-97;counts[node][color]+=1;answer=max(answer,counts[node][color])
  for nxt in graph[node]:
   for shade in range(26):counts[nxt][shade]=max(counts[nxt][shade],counts[node][shade])
   degree[nxt]-=1
   if degree[nxt]==0:queue.append(nxt)
 return answer if seen==n else -1
'''
WORD='''def longest_word_with_all_prefixes(words):
 available=set(words);answer=''
 for word in words:
  if all(word[:length] in available for length in range(1,len(word)+1)) and (len(word)>len(answer) or len(word)==len(answer) and word<answer):answer=word
 return answer
'''
SENTENCE='''def restore_sorted_sentence(s):
 words=s.split();answer=['']*len(words)
 for word in words:answer[int(word[-1])-1]=word[:-1]
 return ' '.join(answer)
'''
MEMORY='''def memory_leak_result(memory1, memory2):
 second=1
 while max(memory1,memory2)>=second:
  if memory1>=memory2:memory1-=second
  else:memory2-=second
  second+=1
 return [second,memory1,memory2]
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1856:E('maximum_subarray_min_product',[('nums','list[int]')],'int',['arrays','prefix-sums','monotonic-stacks'],['The min-product of a nonempty contiguous subarray is its minimum times its sum.','Return the maximum min-product modulo 1,000,000,007 after maximizing the unmodded value.'],[([[1,2,3,2]],'Subarray [2,3,2] has minimum two and sum seven, producing fourteen.'),([[2,3,3,1,2]],'Subarray [2,3,3] has minimum two and sum eight, producing sixteen.')],[[x] for x in [[1],[1,2,3,2],[2,3,3,1,2],[5,5],[3,1,3],[1,1,1],[10,2,2],[2,4,6],[6,4,2],[1,5,1,5],[7,3,4,2],[9,8,1],[2,2,3,2],[4,1,2,3,1]]],PRODUCT,[PRODUCT.replace("nums[middle]*(prefix[index]-prefix[left])","nums[middle]*nums[middle]"),PRODUCT.replace('prefix[index]-prefix[left]','prefix[index]-prefix[left+1]')],['Considers only singleton subarrays instead of the full span for each minimum.', 'Drops the leftmost value from each candidate subarray sum.'],product_o,rproduct,H('For each value, find the widest subarray where it is a minimum.', 'A monotonic stack discovers that span when a smaller or equal value arrives.', 'Use prefix sums to obtain each popped span sum in constant time.', 'Every subarray’s minimum is popped once with its maximal valid span; positivity means that widest span maximizes the sum for that minimum.'),'O(n)','O(n)',7),
1857:E('largest_directed_path_color_value',[('colors','str'),('edges','list[list[int]]')],'int',['graphs','topological-sort','dynamic-programming','counting'],['Node i has colors[i]; a path follows directed edges and its color value is its most frequent color count.','Return the largest path color value, or -1 if any directed cycle exists.'],[(['abaca',[[0,1],[0,2],[2,3],[3,4]]],'Path 0-2-3-4 contains color a three times.'),(['a',[[0,0]]],'The self-loop is a directed cycle, so return -1.')],[[*x] for x in [('a',[]),('a',[[0,0]]),('abaca',[[0,1],[0,2],[2,3],[3,4]]),('abc',[[0,1],[1,2]]),('aaa',[[0,1],[1,2]]),('ab',[[0,1],[1,0]]),('abc',[]),('abca',[[0,1],[0,2],[1,3],[2,3]]),('zzzz',[[0,1],[1,2],[2,3]]),('abcd',[[0,1],[2,3]]),('aba',[[0,2],[1,2]]),('abc',[[0,1],[0,2]]),('cabca',[[0,1],[1,3],[0,2],[2,3],[3,4]]),('xyx',[[0,1],[1,2],[2,1]])]],COLOR,[COLOR.replace('counts[node][color]+=1','counts[node][color]=1'),COLOR.replace('seen==n','seen<=n')],['Resets a color count at each node instead of extending the path count.', 'Fails to reject cycles because the processed-node comparison is always true.'],color_o,rcolor,H('A cycle invalidates the graph; topological processing detects one when fewer than n nodes are removed.', 'For every node keep the best count of each of 26 colors along a path ending there.', 'Propagate all color counts across outgoing edges, adding the destination color when it is processed.', 'Topological order ensures all predecessors contribute before a node leaves the queue, so the DP represents every path; an unprocessed node proves a cycle.'),'O((n+edges)*26)','O(n*26+edges)',8),
1858:E('longest_word_with_all_prefixes',[('words','list[str]')],'str',['strings','tries','hash-maps'],['A word qualifies only when every nonempty prefix is also present in words.','Return the longest qualifying word, breaking ties lexicographically; return empty string if none.'],[([['k','ki','kir','kira','kiran']],'Every prefix of kiran is present, so kiran wins.'),([['a','banana','app','appl','ap','apply','apple']],'apple and apply qualify, and apple is lexicographically smaller.')],[[x] for x in [['a'],['abc'],['a','ab','abc'],['k','ki','kir','kira','kiran'],['a','banana','app','appl','ap','apply','apple'],['b','ba','ban'],['a','ab','abd','abc'],['x','xy','xyz','w'],['cat','c','ca'],['z','za','zb'],['a','aa','aaa'],['m','mo','moo','moon'],['ab','abc'],['d','do','dog','dogs','dot']]],WORD,[WORD.replace('range(1,len(word)+1)','range(2,len(word)+1)'),WORD.replace('word<answer','word>answer')],['Skips the one-character prefix requirement.', 'Breaks equal-length ties toward the lexicographically larger word.'],word_o,rword,H('A set can answer whether each required prefix exists.', 'Check prefixes of every candidate and compare only fully buildable words.', 'Prefer greater length, then smaller lexicographic order.', 'The predicate directly matches the definition, and the two-part comparison preserves exactly the required winner among all qualifying words.'),'O(total characters²)','O(total characters)',5),
1859:E('restore_sorted_sentence',[('s','str')],'str',['strings','sorting'],['Each shuffled word ends in its unique one-based position digit; there are at most nine words.','Remove digits and return the words in original order separated by spaces.'],[(['is2 sentence4 This1 a3'],'Positions 1-4 restore This is a sentence.'),(['Myself2 Me1 I4 and3'],'The suffix digits restore Me Myself and I.')],[[s] for s in ['word1','is2 sentence4 This1 a3','Myself2 Me1 I4 and3','b2 a1','C3 A1 B2','x1 y2 z3','last3 first1 middle2','One1','two2 one1 three3','World2 Hello1','d4 b2 a1 c3','red3 blue1 green2','cat2 The1','Test1 Case2']],SENTENCE,[SENTENCE.replace("int(word[-1])-1","int(word[-1])%len(words)"),SENTENCE.replace("word[:-1]","word")],['Rotates one-based positions instead of converting them to zero-based indices.', 'Leaves the position digits attached to words.'],sentence_o,rsentence,H('The final character of each word is its destination position.', 'Allocate an output list and place the word without its digit at index digit-1.', 'Join the filled positions with single spaces.', 'Position suffixes are unique and cover every slot, so direct placement reconstructs the original ordering exactly.'),'O(total characters)','O(words)',3),
1860:E('memory_leak_result',[('memory1','int'),('memory2','int')],'list[int]',['math','simulation'],['At second i allocate i bits from the stick with more memory, choosing the first on ties.','Crash when neither stick has i bits; return [crash_second,remaining1,remaining2].'],[([2,2],'Second one uses the first stick and second two uses the second, so the crash state is [3,1,0].'),([8,11],'Allocations through second five leave [0,4], then second six crashes.')],[[*x] for x in [(0,0),(1,0),(0,1),(2,2),(8,11),(10,10),(5,1),(1,5),(100,0),(0,100),(3,3),(4,6),(20,15),(7,7)]],MEMORY,[MEMORY.replace('memory1>=memory2','memory1>memory2'),MEMORY.replace('second+=1','second+=2')],['Breaks equal-memory ties toward the second stick.', 'Increases allocation size by two each second instead of one.'],memory_o,rmemory,H('Simulate seconds because each allocation changes which stick is larger.', 'At each second subtract from the larger stick, choosing memory1 on equality.', 'Continue while the larger remaining capacity can satisfy the current second.', 'If the maximum capacity is below the request then neither stick can serve it; otherwise the stated choice and subtraction exactly reproduce that second.'),'O(sqrt(memory1+memory2))','O(1)',5),
}
