"""First reviewed group of workbook batch 117."""
from collections import Counter
from .import_batch_055 import entry
VOWELS=set('aeiou')

def vowel_sub_o(a):
 word=a[0];return sum(set(word[i:j])==VOWELS and all(c in VOWELS for c in word[i:j]) for i in range(len(word)) for j in range(i+1,len(word)+1))
def all_vowels_o(a):
 word=a[0];return sum(sum(c in VOWELS for c in word[i:j]) for i in range(len(word)) for j in range(i+1,len(word)+1))
def distribute_o(a):
 n,q=a
 for limit in range(1,max(q)+1):
  if sum((x+limit-1)//limit for x in q)<=n:return limit
def quality_o(a):
 values,edges,limit=a;g=[[] for _ in values]
 for x,y,t in edges:g[x].append((y,t));g[y].append((x,t))
 best=0
 def walk(node,time,seen,total):
  nonlocal best
  if node==0:best=max(best,total)
  for nxt,cost in g[node]:
   if time+cost<=limit:walk(nxt,time+cost,seen|{nxt},total+(0 if nxt in seen else values[nxt]))
 walk(0,0,{0},values[0]);return best
def equal_o(a):
 s,count=a;answer=0
 for i in range(len(s)):
  freq=Counter()
  for j in range(i,len(s)):
   freq[s[j]]+=1
   answer+=all(v==count for v in freq.values())
 return answer
def rvowelsub(r):return [''.join(r.choice('aeioubcdf') for _ in range(r.randint(1,25)))]
def rallvowel(r):return [''.join(r.choice('abcdeiou') for _ in range(r.randint(1,40)))]
def rdistribute(r):
 m=r.randint(1,10);q=[r.randint(1,50) for _ in range(m)];return [r.randint(m,m+20),q]
def rquality(r):
 n=r.randint(1,7);edges=[]
 for i in range(1,n):edges.append([i,r.randrange(i),r.randint(1,8)])
 return [[r.randint(0,20) for _ in range(n)],edges,r.randint(1,20)]
def requal(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,25))),r.randint(1,5)]

VOWEL_SUB='''\
def count_complete_vowel_substrings(word):
    vowels=set('aeiou');answer=0
    for left in range(len(word)):
        seen=set()
        for right in range(left,len(word)):
            if word[right] not in vowels:break
            seen.add(word[right])
            if len(seen)==5:answer+=1
    return answer
'''
ALL='''\
def total_vowels_over_substrings(word):
    n=len(word)
    return sum((index+1)*(n-index) for index,char in enumerate(word) if char in 'aeiou')
'''
DISTRIBUTE='''\
def minimized_store_maximum(n,quantities):
    low,high=1,max(quantities)
    while low<high:
        middle=(low+high)//2
        stores=sum((quantity+middle-1)//middle for quantity in quantities)
        if stores<=n:high=middle
        else:low=middle+1
    return low
'''
QUALITY='''\
def maximum_path_quality(values,edges,max_time):
    graph=[[] for _ in values]
    for a,b,cost in edges:graph[a].append((b,cost));graph[b].append((a,cost))
    visits=[0]*len(values);visits[0]=1;answer=0
    def search(node,elapsed,quality):
        nonlocal answer
        if node==0:answer=max(answer,quality)
        for neighbor,cost in graph[node]:
            if elapsed+cost>max_time:continue
            first=visits[neighbor]==0;visits[neighbor]+=1
            search(neighbor,elapsed+cost,quality+(values[neighbor] if first else 0))
            visits[neighbor]-=1
    search(0,0,values[0]);return answer
'''
EQUAL='''\
def count_equal_frequency_substrings(s,count):
    answer=0;n=len(s)
    for kinds in range(1,27):
        width=kinds*count
        if width>n:break
        frequencies=[0]*26;valid=0
        for right,char in enumerate(s):
            index=ord(char)-97
            if frequencies[index]==count:valid-=1
            frequencies[index]+=1
            if frequencies[index]==count:valid+=1
            if right>=width:
                old=ord(s[right-width])-97
                if frequencies[old]==count:valid-=1
                frequencies[old]-=1
                if frequencies[old]==count:valid+=1
            if right+1>=width and valid==kinds:answer+=1
    return answer
'''
def L(*x):return list(x)
BATCH={
2062:entry('count_complete_vowel_substrings',[('word','str')],'int',['strings','sliding windows','counting'],['word has 1 through 100 lowercase letters.','A qualifying substring is contiguous, contains only vowels, and contains all five vowel types.','Return the number of qualifying substrings.'],[(['aeiouu'],'The substrings aeiou and aeiouu both contain all vowels and no consonant.'),(['unicornarihan'],'No vowel-only segment contains all five vowel types.')],[[s] for s in ['a','aeiou','aeiouu','unicornarihan','cuaieuouac','bbbb','aeiobcu','uoiea','aaeeiioouu','xaeiou','aeioux','aeio','aeiouaeiou','aexiou']],VOWEL_SUB,[VOWEL_SUB.replace('if word[right] not in vowels:break','if word[right] not in vowels:continue'),VOWEL_SUB.replace('len(seen)==5','len(seen)>=4')],['Skips consonants but continues the same substring across them.','Accepts vowel-only substrings containing only four vowel types.'],vowel_sub_o,rvowelsub,L('Consonants divide the string into independent vowel-only segments.','For every left endpoint, extend right until a consonant while tracking distinct vowels, counting once all five appear.','Break on nonvowel; add vowel to seen; count when len(seen)==5.','Every vowel-only substring is visited at its unique endpoints, and the seen-set condition is equivalent to containing all required vowel types.'),'O(n^2)','O(1)',3),
2063:entry('total_vowels_over_substrings',[('word','str')],'int',['strings','combinatorics','counting'],['word has 1 through 100000 lowercase letters.','For every substring, count its vowel occurrences and sum those counts.','Return the total, which may exceed 32-bit range.'],[(['aba'],'The substrings contribute vowel counts totaling six.'),(['abc'],'The initial a appears in three substrings, so the total is three.')],[[s] for s in ['a','b','aba','abc','aeiou','zzzzz','aaaa','leetcode','xyzau','aeb','banana','education','u','abcdeiou']],ALL,[ALL.replace('(index+1)*(n-index)','index*(n-index)'),ALL.replace("char in 'aeiou'","char not in 'aeiou'")],['Omits choices where a vowel is the first character of a substring.','Counts consonant contributions instead of vowel contributions.'],all_vowels_o,rallvowel,L('A vowel contributes once to every substring containing its index.','Count choices of a left endpoint at or before it and a right endpoint at or after it.','For vowel at i add (i+1)*(n-i).','There are exactly i+1 left boundaries and n-i right boundaries, so their product counts every containing substring once.'),'O(n)','O(1)',5),
2064:entry('minimized_store_maximum',[('n','int'),('quantities','list[int]')],'int',['binary search','greedy'],['There are at least as many stores as product types; quantities are positive.','Each store receives products of at most one type, while a type may be split among stores.','Minimize the greatest number assigned to any store.'],[([6,[11,6]],'A maximum of three uses four stores for the first type and two for the second.'),([7,[15,10,10]],'A per-store maximum of five distributes the types among seven stores.')],[[n,q] for n,q in [(1,[1]),(2,[1]),(6,[11,6]),(7,[15,10,10]),(3,[1,1,1]),(4,[10]),(5,[10,10]),(10,[100]),(5,[2,3]),(8,[16,8,4]),(4,[7,7]),(100,[1000,1]),(6,[5,5,5]),(9,[20,20,20])]],DISTRIBUTE,[DISTRIBUTE.replace('(quantity+middle-1)//middle','quantity//middle'),DISTRIBUTE.replace('stores<=n','stores<n')],['Uses floor division and underestimates stores for a partial final batch.','Rejects feasible distributions that use exactly all n stores.'],distribute_o,rdistribute,L('Feasibility is monotone in a proposed per-store maximum.','A type with q products needs ceil(q/limit) stores; binary-search the smallest limit whose total need is at most n.','If sum((q+m-1)//m)<=n move high=m, else low=m+1.','Any feasible larger limit remains feasible, and the ceiling count is both necessary and sufficient because types split independently.'),'O(types*log max quantity)','O(1)',5),
2065:entry('maximum_path_quality',[('values','list[int]'),('edges','list[list[int]]'),('max_time','int')],'int',['graphs','backtracking','depth-first-search'],['The undirected graph has nonnegative node values, positive edge times, and degree at most four.','A valid walk starts and ends at node zero within max_time; revisits are allowed but each node value counts once.','Return the maximum achievable quality.'],[([[0,32,10,43],[[0,1,10],[1,2,15],[0,3,10]],49],'Visiting nodes zero, one, and three while returning to zero yields quality seventy-five.'),([[5,10,15,20],[[0,1,10],[1,2,10],[0,3,10]],30],'Only one branch can be visited and returned within time, so node three gives quality twenty-five.')],[[v,e,t] for v,e,t in [([5],[],0),([0,32,10,43],[[0,1,10],[1,2,15],[0,3,10]],49),([5,10,15,20],[[0,1,10],[1,2,10],[0,3,10]],30),([1,2],[[0,1,5]],10),([1,2],[[0,1,5]],9),([0,5,10],[[0,1,2],[1,2,2],[2,0,2]],6),([10,1,1],[[0,1,1],[0,2,1]],4),([0,100,1],[[0,1,10],[0,2,1]],5),([3,4,5,6],[[0,1,2],[1,2,2],[2,3,2],[3,0,2]],8),([1,10,20],[[0,1,3],[1,2,3]],12),([7,8],[[0,1,1]],2),([0,5,6,7],[[0,1,2],[1,2,2],[1,3,2]],8),([2,3,4],[[0,1,5],[0,2,5]],20),([1,50,2],[[0,1,10],[0,2,1],[2,1,1]],12)]],QUALITY,[QUALITY.replace('visits[neighbor]==0','visits[neighbor]<=1'),QUALITY.replace('if node==0:answer=max(answer,quality)','answer=max(answer,quality)')],['Counts a revisited node’s value a second time.','Accepts walks ending away from node zero.'],quality_o,rquality,L('The small time budget and degree bound permit enumerating feasible walks, while visit counts prevent duplicate value credit.','Depth-first search from zero, trying edges that fit; add a node value only on its first visit and update the answer only at zero.','Increment visits before recursion and decrement after; carry elapsed time and quality.','Every feasible walk is a DFS prefix, reversible visit counts exactly encode uniqueness, and only return-to-zero prefixes qualify for the maximum.'),'O(4^(max_time/min edge))','O(path length+n)',8),
2067:entry('count_equal_frequency_substrings',[('s','str'),('count','int')],'int',['strings','sliding windows','frequency counting'],['s has lowercase letters and count is positive.','A substring qualifies when every distinct character appearing in it occurs exactly count times.','Return the number of qualifying substrings.'],[(['aaabcbbcc',3],'Exactly three substrings have every present letter occurring three times.'),(['a',1],'The single-character substring qualifies once.')],[[s,c] for s,c in [('a',1),('a',2),('aa',1),('aa',2),('ab',1),('aaabcbbcc',3),('abcabc',2),('aaaa',2),('aabb',2),('abab',2),('abc',1),('abbcc',2),('zzzyyy',3),('abac',1)]],EQUAL,[EQUAL.replace('valid==kinds','valid>=kinds-1'),EQUAL.replace('width=kinds*count','width=kinds+count')],['Accepts windows with one character frequency not equal to count.','Uses an incorrect window length instead of kinds multiplied by count.'],equal_o,requal,L('If a valid substring contains d distinct letters, its length must be d*count.','Try each possible d from one to twenty-six with a fixed-width frequency window and track how many letters currently equal count.','For width=d*count, slide counts; add when exactly d frequencies equal count.','At the required width, d characters each occurring count times consume every position, so the frequency condition is necessary and sufficient.'),'O(26*n)','O(26)',5)
}
