"""Reviewed linked-list, prefix, bitmask, search, and combinatorics imports (85a)."""
from bisect import bisect_left
from collections import Counter
from itertools import combinations
from math import factorial, isqrt

from .import_batch_055 import entry

MOD=1_000_000_007

def zero_oracle(a):
 values=list(a[0])
 while True:
  found=False
  for i in range(len(values)):
   total=0
   for j in range(i,len(values)):
    total+=values[j]
    if total==0:values=values[:i]+values[j+1:];found=True;break
   if found:break
  if not found:return values
def prime_oracle(a):
 n=a[0]
 def prime(x):return x>=2 and all(x%d for d in range(2,isqrt(x)+1))
 p=sum(prime(x) for x in range(1,n+1));return factorial(p)*factorial(n-p)%MOD
def diet_oracle(a):
 calories,k,low,high=a;score=0
 for i in range(len(calories)-k+1):
  total=sum(calories[i:i+k]);score+=(total>high)-(total<low)
 return score
def palindrome_oracle(a):
 s,queries=a;out=[]
 for left,right,k in queries:
  odd=sum(v%2 for v in Counter(s[left:right+1]).values());out.append(odd//2<=k)
 return out
def puzzles_oracle(a):
 words,puzzles=a;return [sum(p[0] in w and set(w)<=set(p) for w in words) for p in puzzles]
def letters_oracle(a):
 s=a[0];return sum(len(set(s[i:j]))==1 for i in range(len(s)) for j in range(i+1,len(s)+1))
def phrases_oracle(a):
 phrases=a[0];answer=set()
 for i,x in enumerate(phrases):
  for j,y in enumerate(phrases):
   if i!=j and x.split()[-1]==y.split()[0]:answer.add(x+' '+y.split(' ',1)[1] if ' ' in y else x)
 return sorted(answer)
def color_oracle(a):
 colors,queries=a;return [min((abs(i-j) for j,v in enumerate(colors) if v==target),default=-1) for i,target in queries]
def ones_oracle(a):
 width,height,side,limit=a;counts=[]
 for r in range(side):
  for c in range(side):counts.append(sum(1 for y in range(r,height,side) for x in range(c,width,side)))
 return sum(sorted(counts,reverse=True)[:limit])
def bus_oracle(a):
 distance,start,dest=a
 if start>dest:start,dest=dest,start
 clockwise=sum(distance[start:dest]);return min(clockwise,sum(distance)-clockwise)

def random_zero(r):return [[r.randint(-5,5) for _ in range(r.randint(0,14))]]
def random_n(r):return [r.randint(1,100)]
def random_diet(r):
 n=r.randint(1,15);k=r.randint(1,n);low=r.randint(0,30);high=r.randint(low,50);return [[r.randint(0,15) for _ in range(n)],k,low,high]
def random_pal(r):
 n=r.randint(1,20);s=''.join(r.choice('abcde') for _ in range(n));q=[]
 for _ in range(r.randint(1,10)):a=r.randrange(n);b=r.randrange(a,n);q.append([a,b,r.randint(0,4)])
 return [s,q]
def random_puzzles(r):
 letters='abcdefg';words=[''.join(r.choice(letters) for _ in range(r.randint(1,7))) for _ in range(r.randint(1,12))];puzzles=[]
 for _ in range(r.randint(1,6)):puzzles.append(''.join(r.sample(letters,7)))
 return [words,puzzles]
def random_letters(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,30)))]
def random_phrases(r):
 words=['a','b','c','d'];return [[' '.join(r.choice(words) for _ in range(r.randint(1,3))) for _ in range(r.randint(2,8))]]
def random_colors(r):
 n=r.randint(1,20);colors=[r.randint(1,3) for _ in range(n)];return [colors,[[r.randrange(n),r.randint(1,3)] for _ in range(r.randint(1,12))]]
def random_ones(r):
 side=r.randint(1,5);return [r.randint(side,9),r.randint(side,9),side,r.randint(0,side*side)]
def random_bus(r):
 n=r.randint(2,15);return [[r.randint(1,20) for _ in range(n)],r.randrange(n),r.randrange(n)]

ZERO='''def remove_zero_sum_sublists(head):
 dummy=ListNode(0,head);prefix=0;last={}
 node=dummy
 while node:prefix+=node.val;last[prefix]=node;node=node.next
 prefix=0;node=dummy
 while node:prefix+=node.val;node.next=last[prefix].next;node=node.next
 return dummy.next
'''
PRIME='''def prime_index_arrangements(n):
 from math import factorial,isqrt
 def prime(value):return value>=2 and all(value%d for d in range(2,isqrt(value)+1))
 count=sum(prime(value) for value in range(1,n+1))
 return factorial(count)*factorial(n-count)%1000000007
'''
DIET='''def diet_plan_score(calories, k, lower, upper):
 window=sum(calories[:k]);score=(window>upper)-(window<lower)
 for i in range(k,len(calories)):
  window+=calories[i]-calories[i-k];score+=(window>upper)-(window<lower)
 return score
'''
PAL='''def can_make_palindrome_queries(s, queries):
 prefix=[0]
 for char in s:prefix.append(prefix[-1]^(1<<(ord(char)-97)))
 return [((prefix[right+1]^prefix[left]).bit_count()//2)<=k for left,right,k in queries]
'''
PUZZLES='''def valid_words_per_puzzle(words, puzzles):
 from collections import Counter
 counts=Counter()
 for word in words:
  mask=sum(1<<(ord(c)-97) for c in set(word))
  if mask.bit_count()<=7:counts[mask]+=1
 answer=[]
 for puzzle in puzzles:
  first=1<<(ord(puzzle[0])-97);rest=sum(1<<(ord(c)-97) for c in puzzle[1:]);sub=rest;total=0
  while True:
   total+=counts[sub|first]
   if sub==0:break
   sub=(sub-1)&rest
  answer.append(total)
 return answer
'''
LETTERS='''def count_single_character_substrings(s):
 answer=run=0;previous=''
 for char in s:
  run=run+1 if char==previous else 1;answer+=run;previous=char
 return answer
'''
PHRASES='''def before_after_puzzles(phrases):
 answer=set()
 for i,left in enumerate(phrases):
  for j,right in enumerate(phrases):
   if i!=j and left.split()[-1]==right.split()[0]:answer.add(left+' '+right.split(' ',1)[1] if ' ' in right else left)
 return sorted(answer)
'''
COLORS='''def shortest_color_distances(colors, queries):
 from bisect import bisect_left
 positions={1:[],2:[],3:[]}
 for i,color in enumerate(colors):positions[color].append(i)
 answer=[]
 for index,color in queries:
  spots=positions[color];at=bisect_left(spots,index);best=float('inf')
  if at<len(spots):best=min(best,spots[at]-index)
  if at:best=min(best,index-spots[at-1])
  answer.append(-1 if best==float('inf') else best)
 return answer
'''
ONES='''def maximum_periodic_ones(width, height, sideLength, maxOnes):
 counts=[]
 for row in range(sideLength):
  for column in range(sideLength):counts.append(((height-1-row)//sideLength+1)*((width-1-column)//sideLength+1))
 return sum(sorted(counts,reverse=True)[:maxOnes])
'''
BUS='''def shortest_bus_route_distance(distance, start, destination):
 if start>destination:start,destination=destination,start
 clockwise=sum(distance[start:destination]);return min(clockwise,sum(distance)-clockwise)
'''

E=entry
BATCH={
1171:E('remove_zero_sum_sublists',[('head','ListNode')],'ListNode | None',['linked-lists','prefix-sums'],['Remove every consecutive zero-sum segment, including segments exposed by earlier removals.','Return the remaining linked-list head.'],[([[1,2,-3,3,1]],'The prefix 1,2,-3 sums to zero, leaving 3,1.'),([[1,2,3,-3,4]],'Removing 3,-3 leaves 1,2,4.')],[[x] for x in [[],[1],[0],[1,-1],[1,2,-3],[1,2,-3,3,1],[1,2,3,-3,4],[1,2,3,-3,-2],[0,0],[1,-1,2,-2],[3,4,-7,5,-6,6],[1,3,2,-3,-2,5,5,-5,1],[2,-2,2],[1,-1,1,-1,1]]],ZERO,[ZERO.replace('node.next=last[prefix].next','node.next=node.next'),ZERO.replace('prefix=0;node=dummy','prefix=1;node=dummy')],['Computes prefix totals but never rewires links to remove a zero-sum span.','Starts the rewiring pass with the wrong prefix total.'],zero_oracle,random_zero,['Equal prefix sums enclose a zero-sum node segment.','Use a dummy zero node so removals may include the original head.','Map each prefix sum to its last node, then make each node skip to the node after that last occurrence.','Using last occurrences removes the widest zero-sum region and also handles segments revealed by deletion.'],'O(n)','O(n)',5),
1175:E('prime_index_arrangements',[('n','int')],'int',['math','counting'],['Indices and values are numbered 1 through n.','Prime values must occupy exactly the prime indices.'],[([5],'There are three prime and two non-prime slots, giving 3!*2!=12.'),([1],'The sole non-prime value has one arrangement.')],[[n] for n in [2,3,4,6,7,10,20,30,50,75,90,96,99,100]],PRIME,[PRIME.replace('value>=2','value>2'),PRIME.replace('factorial(count)*factorial(n-count)','factorial(count+1)*factorial(n-count)')],['Incorrectly excludes two from the primes.','Uses one extra prime permutation factor.'],prime_oracle,random_n,['Count primes from one through n with trial division through each square root.','Prime values can permute among prime positions independently.','Non-prime values likewise permute among the remaining positions.','Multiplying the two factorials counts exactly all valid assignments; apply the modulus.'],'O(n sqrt n)','O(1)',3),
1176:E('diet_plan_score',[('calories','list[int]'),('k','int'),('lower','int'),('upper','int')],'int',['sliding-window','arrays'],['Every contiguous k-day window contributes independently.','Below lower loses one; above upper gains one.'],[([[1,2,3,4,5],1,3,3],'Two days are below, two above, and one equal, totaling zero.'),([[3,2],2,0,1],'The only window exceeds upper, earning one point.')],[[c,k,l,u] for c,k,l,u in [([1],1,1,1),([1],1,2,3),([5],1,1,4),([1,2],2,3,3),([1,2,3],2,3,5),([1,2,3],2,4,4),([10,10,10],1,5,8),([0,0,0],2,1,2),([1,2,3,4],3,5,8),([5,1,5,1],2,5,7),([2,2,2,2],2,4,4),([1,10,1,10],1,3,8),([3,3,3],3,8,10),([4,1,2,7,3],2,4,8)]],DIET,[DIET.replace('window>upper','window>=upper'),DIET.replace('window<lower','window<=lower')],['Awards a point when the sum merely equals upper.','Deducts a point when the sum merely equals lower.'],diet_oracle,random_diet,['Maintain the sum of the current k-day window.','Score the first window, then slide by adding the entering and subtracting the leaving day.','Compare each sum strictly with lower and upper.','Every k-day interval is visited once with its exact sum.'],'O(n)','O(1)',3),
1177:E('can_make_palindrome_queries',[('s','str'),('queries','list[list[int]]')],'list[bool]',['prefix-sums','bitmasks'],['Each query is independent.','One replacement can repair two odd character counts.'],[(['abcda',[[0,4,1],[1,2,0]]],'abcda has two odd pairs repairable once; bc cannot be a palindrome without replacement.'),(['a',[[0,0,0]]],'A one-character substring is already a palindrome.')],[[s,q] for s,q in [('abcda',[[0,4,0]]),('abcda',[[0,4,1]]),('abcda',[[0,3,1]]),('aaa',[[0,2,0]]),('abcd',[[0,3,2]]),('abcd',[[0,3,1]]),('abccba',[[0,5,0]]),('abcabc',[[0,5,0],[1,4,1]]),('x',[[0,0,0]]),('abab',[[0,3,0]]),('abcde',[[1,3,1]]),('zzxy',[[0,3,1]]),('aabbccd',[[0,6,0]]),('leetcode',[[0,7,3],[1,6,2]])]],PAL,[PAL.replace('//2)<=k','//2)<k'),PAL.replace('prefix[right+1]','prefix[right]')],['Requires fewer rather than at most k repairs.','Omits the query’s right endpoint from the parity mask.'],palindrome_oracle,random_pal,['A palindrome can contain at most one odd-frequency character.','Store a prefix XOR mask toggling the bit for each character.','The substring mask is prefix[right+1] XOR prefix[left]; half its odd-bit count is the required replacements.','Each replacement pairs two odd counts, so odd_count//2<=k is necessary and sufficient.'],'O(n+queries)','O(n)',5),
1178:E('valid_words_per_puzzle',[('words','list[str]'),('puzzles','list[str]')],'list[int]',['bitmasks','hash-maps'],['Each puzzle has seven distinct letters.','A valid word contains the puzzle first letter and no outside letter.'],[([['aaaa','asas','able','ability','actt','actor','access'],['aboveyz','abrodyz','abslute','absoryz','actresz','gaswxyz']],'Enumerating puzzle submasks gives counts 1,1,3,2,4,0.'),([['a','b','ab'],['abcdefg']],'Words a and ab contain the required first letter and use only puzzle letters.')],[[w,p] for w,p in [(['a'],['abcdefg']),(['b'],['abcdefg']),(['abcdefg'],['abcdefg']),(['abcdefgh'],['abcdefg']),(['a','aa','aaa'],['abcdefg']),(['ab','ac','bc'],['abcdefg']),(['xyz','x'],['xyzabcd']),(['apple','pleas','please'],['aelwxyz']),(['aaaa','bbbb'],['bacdefg']),(['abc','def'],['abcdefg']),(['g','ag','bg'],['gabcdef']),(['hello','help'],['hpelxyz']),(['act','actor'],['actresz']),(['access','case'],['ascexyz'])]],PUZZLES,[PUZZLES.replace('sub|first','sub'),PUZZLES.replace('mask.bit_count()<=7','mask.bit_count()<7')],['Does not require the puzzle’s first letter.','Drops words using exactly seven distinct letters.'],puzzles_oracle,random_puzzles,['Compress every word’s distinct letters into a bitmask and count useful masks.','For each puzzle, separate the mandatory first-letter bit from the other six.','Enumerate all submasks of the six optional letters and add counts for submask|first.','These 64 masks are exactly all allowed letter sets containing the required letter.'],'O(total word chars + 64*puzzles)','O(unique word masks)',8),
1180:E('count_single_character_substrings',[('s','str')],'int',['strings','dynamic-programming'],['s is nonempty.','Count every substring whose characters are all identical.'],[(['aaaba'],'Runs aaa,b,a contribute 6+1+1=8 substrings.'),(['abc'],'Each individual character is the only valid substring, giving three.')],[[s] for s in ['a','aa','aaa','ab','aba','abb','aabb','aaaa','abcabc','zzzyzzz','mississippi','bbbbba','abababab','ccccaacc']],LETTERS,[LETTERS.replace('answer+=run','answer+=1'),LETTERS.replace('char==previous','char!=previous')],['Counts only individual characters.','Extends runs when characters differ instead of match.'],letters_oracle,random_letters,['A run of length L contributes 1+2+...+L valid substrings.','Track the length of the equal-character run ending at the current position.','Add that run length to the answer for every character.','The added value counts exactly the valid substrings ending at this position.'],'O(n)','O(1)',3),
1181:E('before_after_puzzles',[('phrases','list[str]')],'list[str]',['strings','hash-maps'],['Use two different phrase indices.','Return distinct merged phrases in lexicographic order.'],[([['writing code','code rocks']],'The shared word code joins the phrases into writing code rocks.'),([['mission statement','a quick bite','a chip off the old block','chocolate bar','mission impossible','a man on a mission','block party','eat my words','bar of soap']],'Matching end/start words generate the sorted distinct puzzle list.')],[[p] for p in [['a','a'],['a b','b c'],['a b','c d'],['a b','b'],['x y','y z','z q'],['a a','a a'],['one two','two three','three four'],['red blue','blue red'],['hello world','world peace','peace now'],['a b c','c d e','e f'],['same end','end same','same start'],['x','x y'],['a b','b c','a b'],['cat dog','dog fish','bird cat']]],PHRASES,[PHRASES.replace('i!=j','i==j'),PHRASES.replace('return sorted(answer)','return list(answer)')],['Combines a phrase only with itself instead of other phrases.','Returns set iteration order rather than required lexicographic order.'],phrases_oracle,random_phrases,['Compare the last word of each possible left phrase with the first word of each different right phrase.','When they match, append the right phrase without repeating its first word.','Use a set to remove duplicate merged strings.','Sorting that set produces the required deterministic result after considering both directions.'],'O(p^2*words)','O(results)',5),
1182:E('shortest_color_distances',[('colors','list[int]'),('queries','list[list[int]]')],'list[int]',['binary-search','arrays'],['Colors are only 1,2,3.','Return -1 when a queried color is absent.'],[([[1,1,2,1,3,2,2,3,3],[[1,3],[2,2],[6,1]]],'Nearest matching indices give distances 3,0,3.'),([[1,2],[[0,3]]],'Color three is absent, so the answer is -1.')],[[c,q] for c,q in [([1],[[0,1]]),([1],[[0,2]]),([1,2,3],[[0,3],[2,1]]),([1,1,1],[[2,1]]),([1,2,1,2],[[1,1]]),([3,2,1],[[1,3]]),([1,2,3,2,1],[[2,2]]),([2,2,3],[[0,3]]),([1,3,3,1],[[1,1]]),([1,2,3],[[1,2]]),([3,3,3],[[0,1]]),([1,2,1,3],[[3,2]]),([2,1,2,1,3],[[4,1]]),([1,1,2,1,3,2,2,3,3],[[8,1]])]],COLORS,[COLORS.replace('if at:best=min(best,index-spots[at-1])','if False and at:best=min(best,index-spots[at-1])'),COLORS.replace('answer.append(-1','answer.append(0')],['Checks only the insertion-point successor and ignores a nearer predecessor.','Returns zero instead of -1 when the color is absent.'],color_oracle,random_colors,['Store the sorted occurrence indices for each of the three colors.','Binary-search the query index in the requested color’s positions.','Only the insertion-point neighbor and its predecessor can be nearest.','Taking the smaller distance is exact; an empty occurrence list yields -1.'],'O(n+queries log n)','O(n)',5),
1183:E('maximum_periodic_ones',[('width','int'),('height','int'),('sideLength','int'),('maxOnes','int')],'int',['greedy','math'],['sideLength does not exceed width or height.','Every sideLength-square may contain at most maxOnes ones.'],[([3,3,2,1],'Choosing the most frequent residue position places four ones.'),([3,3,2,2],'The two most frequent residue positions place six ones.')],[[w,h,s,m] for w,h,s,m in [(1,1,1,0),(1,1,1,1),(2,2,1,1),(2,2,2,1),(2,2,2,4),(3,3,2,1),(3,3,2,2),(4,4,2,1),(4,4,3,2),(5,4,2,3),(6,5,3,4),(7,7,4,5),(8,3,3,2),(9,9,5,7)]],ONES,[ONES.replace('reverse=True','reverse=False'),ONES.replace('[:maxOnes]','[:maxOnes+1]')],['Chooses the least frequent periodic positions.','Uses one more residue class than permitted.'],ones_oracle,random_ones,['A sideLength-by-sideLength pattern repeats safely across the whole matrix.','Count how often every residue pair modulo sideLength appears.','Choose the maxOnes residue positions with greatest frequencies.','Every constrained square contains each residue once, and periodic placement reaches the upper bound.'],'O(sideLength^2 log sideLength)','O(sideLength^2)',8),
1184:E('shortest_bus_route_distance',[('distance','list[int]'),('start','int'),('destination','int')],'int',['prefix-sums','arrays'],['distance[i] connects stop i to (i+1) mod n.','Travel may use either direction.'],[([[1,2,3,4],0,1],'The direct clockwise edge has length one.'),([[1,2,3,4],0,3],'Counterclockwise uses the final edge of length four instead of clockwise length six.')],[[d,s,t] for d,s,t in [([1,2],0,1),([1,2,3],0,0),([1,2,3],0,2),([1,2,3],2,0),([5,5,5,5],1,3),([1,2,3,4],1,2),([1,2,3,4],1,3),([1,2,3,4],3,1),([10,1,1],0,1),([10,1,1],1,2),([3,7,2,9,1],0,4),([3,7,2,9,1],2,4),([1,1,1,1,1],0,3),([8,2,6,4],3,0)]],BUS,[BUS.replace('min(clockwise','max(clockwise'),BUS.replace('if start>destination','if start<destination')],['Returns the longer direction.','Swaps already-ordered endpoints and slices the wrong arc.'],bus_oracle,random_bus,['Normalize endpoints so start is not after destination.','Sum the direct slice between them in increasing index order.','The opposite route costs total route length minus that slice.','The two arcs are the only possible simple routes, so their minimum is optimal.'],'O(n)','O(1)',3),
}
BATCH[1171]['params'][0]=('head','ListNode | None','listnode')
BATCH[1171]['adapter']='listnode'
