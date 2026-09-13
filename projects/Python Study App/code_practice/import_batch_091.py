"""First half of batch 91: deterministic string, matrix, graph, and greedy tasks."""
from collections import Counter, defaultdict
from itertools import combinations
from .import_batch_055 import entry

def vertical_o(a):
 words=a[0].split();return [''.join(w[i] if i<len(w) else ' ' for w in words).rstrip() for i in range(max(map(len,words)))]
def break_o(a):
 s=a[0];choices=[]
 for i in range(len(s)):
  for c in 'abcdefghijklmnopqrstuvwxyz':
   x=s[:i]+c+s[i+1:]
   if x!=x[::-1]:choices.append(x)
 return min(choices,default='')
def diagonal_o(a):
 mat=[row[:] for row in a[0]];groups=defaultdict(list)
 for i,row in enumerate(mat):
  for j,v in enumerate(row):groups[i-j].append(v)
 for values in groups.values():values.sort(reverse=True)
 for i,row in enumerate(mat):
  for j in range(len(row)):mat[i][j]=groups[i-j].pop()
 return mat
def rank_o(a):
 ordered=sorted(set(a[0]));return [ordered.index(v)+1 for v in a[0]]
def remove_pal_o(a):return 1 if a[0]==a[0][::-1] else 2
def restaurants_o(a):
 data,vegan,price,distance=a
 return [r[0] for r in sorted((r for r in data if (not vegan or r[2]) and r[3]<=price and r[4]<=distance),key=lambda r:(-r[1],-r[0]))]
def city_o(a):
 n,edges,limit=a;d=[[0 if i==j else 10**9 for j in range(n)] for i in range(n)]
 for x,y,w in edges:d[x][y]=d[y][x]=min(d[x][y],w)
 for k in range(n):
  for i in range(n):
   for j in range(n):d[i][j]=min(d[i][j],d[i][k]+d[k][j])
 return min(range(n),key=lambda i:(sum(d[i][j]<=limit for j in range(n) if j!=i),-i))
def weak_o(a):return [i for _,i in sorted((sum(row),i) for i,row in enumerate(a[0]))[:a[1]]]
def reduce_o(a):
 arr=a[0];counts=list(Counter(arr).values());target=(len(arr)+1)//2
 for size in range(len(counts)+1):
  if any(sum(c)>=target for c in combinations(counts,size)):return size
def steps_o(a):
 n=a[0];steps=0
 while n:steps+=1;n=n//2 if n%2==0 else n-1
 return steps

def rv(r):return [' '.join(''.join(r.choice('ABC') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,7)))]
def rbreak(r):
 half=''.join(r.choice('abc') for _ in range(r.randint(1,8)));return [half+half[::-1]]
def rdiag(r):
 h,w=r.randint(1,6),r.randint(1,6);return [[[r.randint(-9,9) for _ in range(w)] for _ in range(h)]]
def rrank(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]
def rpal(r):return [''.join(r.choice('ab') for _ in range(r.randint(1,40)))]
def rrest(r):
 n=r.randint(1,12);data=[[i,r.randint(1,10),r.randint(0,1),r.randint(1,60),r.randint(1,20)] for i in range(1,n+1)];return [data,r.randint(0,1),r.randint(1,60),r.randint(1,20)]
def rcity(r):
 n=r.randint(2,8);edges=[]
 for i in range(n):
  for j in range(i+1,n):
   if r.random()<.35:edges.append([i,j,r.randint(1,15)])
 return [n,edges,r.randint(1,25)]
def rweak(r):
 h,w=r.randint(1,10),r.randint(1,10);mat=[]
 for _ in range(h):ones=r.randint(0,w);mat.append([1]*ones+[0]*(w-ones))
 return [mat,r.randint(1,h)]
def rreduce(r):return [[r.randint(1,8) for _ in range(r.randint(2,16))]]
def rsteps(r):return [r.randint(0,10**9)]

VERTICAL='''def print_words_vertically(s):
 words=s.split();width=max(map(len,words));return [''.join(word[i] if i<len(word) else ' ' for word in words).rstrip() for i in range(width)]
'''
BREAK='''def break_palindrome(palindrome):
 if len(palindrome)==1:return ''
 chars=list(palindrome)
 for i in range(len(chars)//2):
  if chars[i]!='a':chars[i]='a';return ''.join(chars)
 chars[-1]='b';return ''.join(chars)
'''
DIAGONAL='''def sort_matrix_diagonals(mat):
 from collections import defaultdict
 groups=defaultdict(list)
 for i,row in enumerate(mat):
  for j,v in enumerate(row):groups[i-j].append(v)
 for values in groups.values():values.sort(reverse=True)
 for i,row in enumerate(mat):
  for j in range(len(row)):mat[i][j]=groups[i-j].pop()
 return mat
'''
RANK='''def array_rank_transform(arr):
 rank={value:i+1 for i,value in enumerate(sorted(set(arr)))};return [rank[value] for value in arr]
'''
REMOVE='''def palindrome_subsequence_removals(s):
 return 1 if s==s[::-1] else 2
'''
RESTAURANTS='''def filter_restaurant_ids(restaurants, vegan_friendly, max_price, max_distance):
 valid=[r for r in restaurants if (not vegan_friendly or r[2]) and r[3]<=max_price and r[4]<=max_distance]
 return [r[0] for r in sorted(valid,key=lambda r:(-r[1],-r[0]))]
'''
CITY='''def smallest_reachable_city(n, edges, distance_threshold):
 distance=[[0 if i==j else float('inf') for j in range(n)] for i in range(n)]
 for a,b,w in edges:distance[a][b]=distance[b][a]=min(distance[a][b],w)
 for k in range(n):
  for i in range(n):
   for j in range(n):distance[i][j]=min(distance[i][j],distance[i][k]+distance[k][j])
 return min(range(n),key=lambda i:(sum(distance[i][j]<=distance_threshold for j in range(n) if j!=i),-i))
'''
WEAK='''def weakest_matrix_rows(mat, k):
 return [i for _,i in sorted((sum(row),i) for i,row in enumerate(mat))[:k]]
'''
REDUCE='''def minimum_values_for_half_removal(arr):
 from collections import Counter
 removed=answer=0
 for count in sorted(Counter(arr).values(),reverse=True):
  removed+=count;answer+=1
  if removed*2>=len(arr):return answer
'''
STEPS='''def reduction_steps_to_zero(num):
 answer=0
 while num:answer+=1;num=num//2 if num%2==0 else num-1
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1324:S('print_words_vertically',[('s','str')],'list[str]',['strings','simulation'],['s contains uppercase words separated by single spaces.','Preserve internal spaces but trim trailing spaces from each vertical row.'],[(['HOW ARE YOU'],'Columns form HAY, ORO, and WEU.'),(['TO BE OR NOT TO BE'],'Shorter words contribute internal padding but no trailing padding.')],[[s] for s in ['A','AB C','A BC','ABC D','A B C','HELLO WORLD','ONE TWO THREE','X YY ZZZ','CODE PRACTICE','I LOVE PYTHON','LONG S','AA BBB CCCC','CAT DOG','UP DOWN LEFT RIGHT']],VERTICAL,[VERTICAL.replace('.rstrip()',''),VERTICAL.replace('word[i] if i<len(word)','word[-1-i] if i<len(word)')],['Keeps forbidden trailing spaces.','Reads each word from the end instead of top to bottom.'],vertical_o,rv,['Split the sentence into words and find the maximum word length.','For each character row, take that position from every word or a space if absent.','Right-trim the completed row.','This is exactly the column-wise view of left-aligned words.'],'O(total output)','O(total output)',5),
1328:S('break_palindrome',[('palindrome','str')],'str',['greedy','strings'],['Input is a lowercase palindrome.','Change exactly one character to obtain the lexicographically smallest non-palindrome, or empty string if impossible.'],[(['abccba'],'Changing the first non-a in the first half to a produces aaccba.'),(['a'],'Any one-character string remains a palindrome, so return empty.')],[[s] for s in ['aa','aba','aaa','abba','aaaa','baab','bb','abcba','racecar','aabaa','zz','azbza','aaaaaa','caaac']],BREAK,[BREAK.replace("chars[i]='a'","chars[i]='b'"),BREAK.replace('chars[-1]','chars[0]')],['Changes the first non-a to b rather than the smallest character a.','Changes the first character when all first-half characters are a, producing a larger answer than changing the last.'],break_o,rbreak,['A change in the first half dominates the mirrored position lexicographically.','Replace the first non-a before the midpoint with a.','If the first half is all a, change the final character to b; length one is impossible.','The earliest possible decrease is optimal, and the fallback makes the smallest possible increase latest.'],'O(n)','O(n)',5),
1329:S('sort_matrix_diagonals',[('mat','list[list[int]]')],'list[list[int]]',['matrices','sorting'],['Sort each top-left to bottom-right diagonal independently in ascending order.','Return the resulting matrix.'],[([[[3,3,1,1],[2,2,1,2],[1,1,1,2]]],'Each i-j diagonal is sorted and written back from top-left to bottom-right.'),([[[1,2],[3,4]]],'Every diagonal is already sorted.')],[[m] for m in [[[1]],[[2,1]],[[2],[1]],[[2,1],[1,2]],[[4,3],[2,1]],[[1,2,3],[4,5,6]],[[9,8,7],[6,5,4],[3,2,1]],[[3,1,2],[2,3,1]],[[1,1],[1,1]],[[5,4,3,2]],[[5],[4],[3]],[[2,9],[8,1],[7,6]],[[0,-1],[-2,3]],[[4,1,7],[3,2,6],[9,8,5]]]],DIAGONAL,[DIAGONAL.replace('sort(reverse=True)','sort()'),DIAGONAL.replace('groups[i-j]','groups[i+j]')],['Sorts ascending then pops the largest value first.','Groups anti-diagonals by i+j instead of diagonals by i-j.'],diagonal_o,rdiag,['Cells share a diagonal exactly when i-j is equal.','Group values by i-j and sort each group in reverse order.','Traverse row-major and pop the smallest remaining value for that diagonal.','Each group is independently written in increasing traversal order.'],'O(mn log min(m,n))','O(mn)',5),
1331:S('array_rank_transform',[('arr','list[int]')],'list[int]',['sorting','hash-maps'],['Rank starts at one; equal values share rank.','Ranks increase only between distinct values.'],[([[40,10,20,30]],'Sorted distinct values 10,20,30,40 map to ranks 1,2,3,4.'),([[100,100,100]],'All equal values receive rank one.')],[[x] for x in [[1],[2,1],[1,2],[1,1],[3,1,2],[-1,0,1],[10,20,10],[5,5,1,1],[100,-100,0],[4,2,2,8],[9,7,5,3],[1,3,3,5,2],[0,0,-1],[40,10,20,30]]],RANK,[RANK.replace('i+1','i'),RANK.replace('sorted(set(arr))','sorted(arr)')],['Uses zero-based ranks.','Assigns gaps and different ranks to duplicate values.'],rank_o,rrank,['Sort the distinct values once.','Map each distinct value to its one-based index in that ordering.','Replace each original value through the map.','The map preserves equality and strict value order while producing consecutive ranks.'],'O(n log n)','O(n)',3),
1332:S('palindrome_subsequence_removals',[('s','str')],'int',['strings','palindromes'],['s is nonempty and contains only a and b.','In one step remove any palindromic subsequence.'],[(['ababa'],'The entire string is a palindrome, so one removal suffices.'),(['abb'],'The string is not a palindrome, but all a characters then all b characters can be removed in two steps.')],[[s] for s in ['a','b','ab','ba','aa','bb','aba','abb','aab','abab','abba','baaab','aababb','bbbbba']],REMOVE,[REMOVE.replace('else 2','else 1'),REMOVE.replace("s==s[::-1]","s!=s[::-1]")],['Claims every string can be removed in one step.','Reverses the palindrome test.'],remove_pal_o,rpal,['If s is a palindrome, remove it whole.','Otherwise remove all a characters as one palindromic subsequence, then all b characters.','Return one for a palindrome and two otherwise.','A non-palindrome cannot be removed whole, while the two uniform subsequences always work.'],'O(n)','O(n)',3),
1333:S('filter_restaurant_ids',[('restaurants','list[list[int]]'),('vegan_friendly','int'),('max_price','int'),('max_distance','int')],'list[int]',['sorting','filtering'],['Each row is [id,rating,vegan,price,distance].','Sort accepted IDs by rating descending then ID descending.'],[([[[1,4,1,40,10],[2,8,0,50,5],[3,8,1,30,4],[4,10,0,10,3],[5,1,1,15,1]],1,50,10],'Vegan filtering leaves IDs 3,1,5 in rating and ID order.'),([[[1,5,0,10,1],[2,5,1,10,1]],0,10,1],'Equal ratings use descending ID, producing 2 then 1.')],[[r,v,p,d] for r,v,p,d in [([[1,1,1,1,1]],1,1,1),([[1,1,0,1,1]],1,1,1),([[1,1,0,1,1]],0,1,1),([[1,5,1,20,2],[2,6,1,10,3]],1,15,5),([[1,5,1,10,6],[2,4,1,10,5]],1,10,5),([[1,5,1,10,1],[2,5,1,10,1]],1,10,1),([[3,3,0,5,5],[4,4,1,6,6]],0,10,10),([[1,10,0,1,1],[2,1,1,1,1]],1,5,5),([[1,2,1,50,10],[2,3,1,51,10]],1,50,10),([[1,2,1,5,11],[2,3,1,5,10]],1,5,10),([[5,7,1,20,4],[2,7,1,20,4]],1,20,4),([[1,1,0,100,100],[2,2,1,1,1]],0,10,10),([[9,9,1,9,9]],0,8,10),([[1,4,1,40,10],[3,8,1,30,4]],1,50,10)]],RESTAURANTS,[RESTAURANTS.replace('-r[0]','r[0]'),RESTAURANTS.replace('(not vegan_friendly or r[2])','r[2]')],['Breaks rating ties by smaller ID first.','Always requires vegan-friendly restaurants even when the flag is zero.'],restaurants_o,rrest,['Filter before sorting.','The vegan flag is required only when vegan_friendly equals one; price and distance use inclusive limits.','Sort rows by negative rating then negative ID and return IDs.','The compound key implements both descending priorities exactly.'],'O(n log n)','O(n)',5),
1334:S('smallest_reachable_city',[('n','int'),('edges','list[list[int]]'),('distance_threshold','int')],'int',['graphs','shortest-path'],['Edges are undirected and weighted positively.','Minimize reachable other cities within threshold; ties choose greatest city index.'],[([4,[[0,1,3],[1,2,1],[1,3,4],[2,3,1]],4],'City three reaches the fewest neighbors within distance four.'),([5,[[0,1,2],[0,4,8],[1,2,3],[1,4,2],[2,3,1],[3,4,1]],2],'Compute all shortest paths before applying the threshold and tie rule.')],[[n,e,t] for n,e,t in [(2,[],1),(2,[[0,1,1]],1),(3,[[0,1,2],[1,2,2]],2),(3,[[0,1,2],[1,2,2]],4),(4,[[0,1,1],[2,3,1]],1),(4,[[0,1,5],[1,2,5],[2,3,5]],4),(4,[[0,1,5],[1,2,5],[2,3,5]],10),(3,[[0,1,1],[0,1,5],[1,2,1]],2),(5,[],100),(5,[[0,1,2],[1,2,2],[2,3,2],[3,4,2]],3),(4,[[0,1,1],[0,2,1],[0,3,1]],1),(4,[[0,1,2],[1,2,2],[2,3,2],[0,3,10]],6),(3,[[0,1,10]],5),(6,[[0,1,1],[2,3,1],[4,5,1]],1)]],CITY,[CITY.replace('-i','i'),'''def smallest_reachable_city(n, edges, distance_threshold):
 counts=[0]*n
 for a,b,w in edges:
  if w<=distance_threshold:counts[a]+=1;counts[b]+=1
 return min(range(n),key=lambda i:(counts[i],-i))
'''],['Breaks ties toward the smallest city index.','Counts only direct edges and ignores cities reachable through shorter multi-edge paths.'],city_o,rcity,['All-pairs shortest paths make each reachability count explicit.','Initialize direct edges and zero diagonals, then run Floyd-Warshall.','Count other cities within threshold and minimize (count,-index).','Floyd-Warshall considers every possible intermediate city; -index implements the required greatest-index tie.'],'O(n³)','O(n²)',5),
1337:S('weakest_matrix_rows',[('mat','list[list[int]]'),('k','int')],'list[int]',['sorting','matrices'],['Each binary row has ones before zeros.','Rank by soldier count ascending then row index ascending.'],[([[[1,1,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,1,0,0,0],[1,1,1,1,1]],3],'Counts and index ties select rows 2,0,3.'),([[[1,0],[1,0],[1,1]],2],'Equal weak rows keep their lower index first.')],[[m,k] for m,k in [([[0]],1),([[1]],1),([[0],[1]],1),([[1,0],[0,0]],2),([[1,0],[1,0]],1),([[1,1],[1,0]],1),([[1,1],[1,0]],2),([[0,0],[0,0],[0,0]],2),([[1,1,1],[1,0,0],[1,1,0]],3),([[1],[0],[1]],2),([[1,1,0],[1,0,0],[0,0,0]],1),([[1,1],[1,1]],2),([[1,0,0],[1,1,1]],1),([[0],[0],[1],[1]],3)]],WEAK,[WEAK.replace('(sum(row),i)','(-sum(row),i)'),WEAK.replace('sum(row),i','sum(row),-i')],['Ranks stronger rows before weaker rows.','Breaks equal-strength ties toward the larger index.'],weak_o,rweak,['A row’s strength is its number of ones.','Pair each strength with its row index.','Sort pairs ascending and return the first k indices.','Tuple order exactly matches the strength then index ranking.'],'O(rows*cols + rows log rows)','O(rows)',3),
1338:S('minimum_values_for_half_removal',[('arr','list[int]')],'int',['greedy','hash-maps'],['Remove all occurrences of each selected value.','Remove at least half the array using the fewest distinct values.'],[([[3,3,3,3,5,5,5,2,2,7]],'Removing values three and five removes seven of ten elements.'),([[7,7,7,7,7,7]],'Selecting seven alone removes the entire array.')],[[x] for x in [[1,2],[1,1],[1,2,3,4],[1,1,2,3],[1,1,2,2],[1,1,1,2,3],[1,2,2,3,3,3],[5]*8,[1,2,3,3,3,4,4,4],[1,1,2,2,3,3,4,4],[9,8,7,6,5,4],[1,1,1,1,2,2,3,4],[2,2,2,3,3,4],[1,2,2,2,3,3,3,3]]],REDUCE,[REDUCE.replace('reverse=True','reverse=False'),REDUCE.replace('removed*2>=len(arr)','removed*2>len(arr)')],['Removes rare values before frequent ones.','Requires strictly more than half instead of at least half.'],reduce_o,rreduce,['Only occurrence counts matter.','Sort frequencies descending and accumulate them.','Stop when removed count reaches at least half the array.','For any fixed number of selected values, choosing the largest frequencies maximizes removed elements.'],'O(n log n)','O(n)',5),
1342:S('reduction_steps_to_zero',[('num','int')],'int',['bit-manipulation','simulation'],['When num is even divide by two; when odd subtract one.','Count operations until zero.'],[([14],'14→7→6→3→2→1→0 takes six steps.'),([8],'Three divisions reach one, then one subtraction reaches zero.')],[[n] for n in [0,1,2,3,4,5,6,7,8,15,16,31,100,1000000000]],STEPS,['''def reduction_steps_to_zero(num):
 answer=0
 while num:answer+=1;num//=2
 return answer
''',STEPS.replace('answer+=1','answer+=2')],['Halves odd numbers directly instead of spending a subtraction step first.','Counts every operation twice.'],steps_o,rsteps,['Apply the stated rule directly.','Each even step removes one trailing binary zero; each odd step clears a trailing one.','Increment once per transition until num is zero.','Both operations strictly reduce positive num, so the simulation is exact and terminates.'],'O(log num)','O(1)',3),
}
