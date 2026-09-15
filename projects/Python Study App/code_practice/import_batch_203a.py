"""Graph similarity, simulations, interval markup, chunks, and sliding puzzles."""
from collections import Counter,deque
from itertools import permutations
from .import_batch_055 import entry

def similar_o(a):
    first,second,pairs=a
    if len(first)!=len(second):return False
    graph={}
    for x,y in pairs:graph.setdefault(x,set()).add(y);graph.setdefault(y,set()).add(x)
    for start,target in zip(first,second):
        if start==target:continue
        seen={start};todo=[start]
        while todo:
            node=todo.pop()
            for nxt in graph.get(node,()):
                if nxt not in seen:seen.add(nxt);todo.append(nxt)
        if target not in seen:return False
    return True
def rsimilar(r):
    words=[chr(97+i) for i in range(r.randint(2,10))];pairs=[]
    for i in range(len(words)):
        for j in range(i):
            if r.random()<.25:pairs.append([words[i],words[j]])
    n=r.randint(1,8);return [[r.choice(words) for _ in range(n)],[r.choice(words) for _ in range(n)],pairs]

def water_o(a):
    heights,volume,k=list(a[0]),a[1],a[2]
    for _ in range(volume):
        destination=k;best=heights[k];i=k-1
        while i>=0 and heights[i]<=heights[i+1]:
            if heights[i]<best:best=heights[i];destination=i
            i-=1
        if destination==k:
            i=k+1
            while i<len(heights) and heights[i]<=heights[i-1]:
                if heights[i]<best:best=heights[i];destination=i
                i+=1
        heights[destination]+=1
    return heights
def rwater(r):
    heights=[r.randint(0,8) for _ in range(r.randint(1,12))];return [heights,r.randint(0,20),r.randrange(len(heights))]

def bold_o(a):
    words,text=a;covered=[]
    for i in range(len(text)):covered.append(any(i>=start and i<start+len(word) for word in words for start in range(len(text)-len(word)+1) if text[start:start+len(word)]==word))
    out='';i=0
    while i<len(text):
        if not covered[i]:out+=text[i];i+=1;continue
        j=i
        while j<len(text) and covered[j]:j+=1
        out+='<b>'+text[i:j]+'</b>';i=j
    return out
def rbold(r):
    text=''.join(r.choice('abcd') for _ in range(r.randint(1,18)));words=[]
    for _ in range(r.randint(1,6)):
        if r.random()<.7:
            i=r.randrange(len(text));j=r.randint(i+1,min(len(text),i+5));words.append(text[i:j])
        else:words.append(''.join(r.choice('abcd') for _ in range(r.randint(1,4))))
    return [words,text]

def chunks_o(a):
    arr=a[0];best=0
    for mask in range(1<<(len(arr)-1)):
        result=[];start=0
        for i in range(len(arr)-1):
            if mask>>i&1:result.extend(sorted(arr[start:i+1]));start=i+1
        result.extend(sorted(arr[start:]));
        if result==sorted(arr):best=max(best,mask.bit_count()+1)
    return best
def rchunks(r):return [[r.randint(-5,5) for _ in range(r.randint(1,8))]]

_DIST=None
def puzzle_o(a):
    global _DIST
    if _DIST is None:
        goal=(1,2,3,4,5,0);_DIST={goal:0};todo=deque([goal]);moves=((1,3),(0,2,4),(1,5),(0,4),(1,3,5),(2,4))
        while todo:
            state=todo.popleft();z=state.index(0)
            for p in moves[z]:
                nxt=list(state);nxt[z],nxt[p]=nxt[p],nxt[z];nxt=tuple(nxt)
                if nxt not in _DIST:_DIST[nxt]=_DIST[state]+1;todo.append(nxt)
    return _DIST.get(tuple(a[0][0]+a[0][1]),-1)
def rpuzzle(r):
    values=list(range(6));r.shuffle(values);return [[values[:3],values[3:]]]

SIMILAR='''def are_sentences_similar(sentence1,sentence2,similar_pairs):
    if len(sentence1)!=len(sentence2):return False
    parent={}
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    for a,b in similar_pairs:parent[find(a)]=find(b)
    return all(a==b or find(a)==find(b) for a,b in zip(sentence1,sentence2))
'''
WATER='''def pour_water(heights,volume,k):
    heights=heights[:]
    for _ in range(volume):
        for direction in (-1,1):
            i=best=k
            while 0<=i+direction<len(heights) and heights[i+direction]<=heights[i]:
                if heights[i+direction]<heights[i]:best=i+direction
                i+=direction
            if best!=k:heights[best]+=1;break
        else:heights[k]+=1
    return heights
'''
BOLD='''def add_bold_tags(words,s):
    marked=[False]*len(s)
    for i in range(len(s)):
        end=max((i+len(word) for word in words if s.startswith(word,i)),default=i)
        for j in range(i,min(end,len(s))):marked[j]=True
    answer=[];i=0
    while i<len(s):
        if not marked[i]:answer.append(s[i]);i+=1;continue
        j=i
        while j<len(s) and marked[j]:j+=1
        answer.extend(('<b>',s[i:j],'</b>'));i=j
    return ''.join(answer)
'''
CHUNKS='''def maximum_chunks_with_duplicates(arr):
    ordered=sorted(arr);left=right=0;answer=0
    for a,b in zip(arr,ordered):
        left+=a;right+=b
        if left==right:answer+=1
    return answer
'''
PUZZLE='''def sliding_puzzle_moves(board):
    start=tuple(board[0]+board[1]);goal=(1,2,3,4,5,0);moves=((1,3),(0,2,4),(1,5),(0,4),(1,3,5),(2,4));queue=deque([(start,0)]);seen={start}
    while queue:
        state,distance=queue.popleft()
        if state==goal:return distance
        zero=state.index(0)
        for place in moves[zero]:
            nxt=list(state);nxt[zero],nxt[place]=nxt[place],nxt[zero];nxt=tuple(nxt)
            if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
    return -1
'''

BATCH={
737:entry('are_sentences_similar',[('sentence1','list[str]'),('sentence2','list[str]'),('similar_pairs','list[list[str]]')],'bool',['graphs','union find'],['Sentences must have equal lengths.','Words are similar to themselves, and supplied similarity pairs are symmetric and transitive.','Return whether every aligned word pair is similar.'],[([['great','acting','skills'],['fine','drama','talent'],[['great','good'],['fine','good'],['drama','acting'],['skills','talent']]],'Great connects transitively to fine, while the other aligned pairs are directly connected.'),([['a'],['c'],[['a','b'],['b','c']]],'The two supplied edges create a transitive path from a to c.')],[[*x] for x in [(['a'],['a'],[]),(['a'],['b'],[]),(['a'],['b'],[['a','b']]),(['a','x'],['c','x'],[['a','b'],['b','c']]),(['a'],['d'],[['a','b'],['c','d']]),([],[],[]),(['a'],[],[]),(['x','y'],['y','x'],[['x','y']]),(['a','b'],['c','d'],[['a','c'],['b','d']]),(['a'],['c'],[['a','b'],['b','c']]),(['m','n'],['m','q'],[['n','o'],['o','q']]),(['a','b'],['a','c'],[['b','c']]),(['one'],['two'],[['one','mid'],['mid','two']]),(['u','v'],['w','v'],[['u','w']])]],SIMILAR,[SIMILAR.replace('parent[find(a)]=find(b)','parent[a]=b'),SIMILAR.replace('a==b or ','')],['Does not merge component roots, so longer transitive chains can break.','Forgets that every word is similar to itself.'],similar_o,rsimilar,['Model words as vertices joined by similarity pairs.','Union every supplied pair, then compare component representatives for aligned words.','Also accept identical aligned words directly.','Union-find computes exactly the symmetric transitive closure required by the definition.'],'O(words+pairs*alpha)','O(distinct words)',5),
755:entry('pour_water',[('heights','list[int]'),('volume','int'),('k','int')],'list[int]',['arrays','simulation'],['Each unit falls at k, preferring the left side if following a nonincreasing path reaches a lower level.','If left cannot fall, try right by the same rule; otherwise remain at k.','Return final column levels after all units settle.'],[([[2,1,1,2,1,2,2],4,3],'Two units settle left, one right, and one at k.'),([[1,2,3,4],2,2],'Both units travel left to the lowest reachable positions.')],[[*x] for x in [([1],0,0),([1],3,0),([2,1],1,0),([1,2],1,1),([3,1,3],5,1),([2,1,1,2,1,2,2],4,3),([1,2,3,4],2,2),([4,3,2,1],3,1),([2,2,2],2,1),([5,1,2,1,5],6,2),([0,0],1,0),([2,0,2],4,1),([3,2,2,3],3,0),([1,0,1,0,1],5,2)]],WATER,[WATER.replace('(-1,1)','(1,-1)'),WATER.replace('<=heights[i]','<heights[i]')],['Prefers right before left.','Cannot traverse across equal-height columns to reach a later drop.'],water_o,rwater,['Simulate one unit at a time.','Scan left across nonincreasing levels while remembering the latest strict drop; only if none exists scan right.','Increase the chosen column by one.','The scan order implements left preference and the last lower point is where gravity ultimately settles the unit.'],'O(volume*n)','O(n)',5),
758:entry('add_bold_tags',[('words','list[str]'),('s','str')],'str',['strings','intervals'],['Bold every character covered by an occurrence of any dictionary word.','Merge overlapping or adjacent bold regions into one tag pair.','Return the original text with lowercase HTML b tags inserted.'],[([['ab','bc'],'aabcd'],'Occurrences overlap across abc, producing one merged bold region.'),([['abc','123'],'abcxyz123'],'Two separated occurrences receive separate tag pairs.')],[[*x] for x in [(['a'],'a'),(['x'],'abc'),(['ab','bc'],'aabcd'),(['abc','123'],'abcxyz123'),(['aa'],'aaaa'),(['ab','cd'],'abcd'),(['ab','de'],'abXde'),(['aba','bab'],'ababa'),(['z'],'zzz'),(['long'],'short'),(['a','c'],'abc'),(['abc','b'],'abc'),(['xy','yz'],'wxyz'),(['bcd'],'abcde')]],BOLD,[BOLD.replace('max((i+len(word)','min((i+len(word)'),BOLD.replace('and marked[j]','and not marked[j]')],['Keeps only the shortest word beginning at each position.','Extends a bold segment while characters are unmarked.'],bold_o,rbold,['Mark text positions covered by any matching word occurrence.','After marking, scan maximal consecutive true regions.','Emit ordinary characters directly and wrap each true run once.','The union of marked positions merges every overlap and adjacency without losing original text order.'],'O(len(s)*words*word length)','O(len(s))',5),
768:entry('maximum_chunks_with_duplicates',[('arr','list[int]')],'int',['arrays','sorting','greedy'],['Split arr into the maximum number of nonempty contiguous chunks.','Sorting every chunk independently and concatenating must equal the globally sorted array.','Duplicates and negative values are allowed.'],[([[5,4,3,2,1]],'No proper prefix contains the same values as the corresponding globally sorted prefix.'),([[2,1,3,4,4]],'The array can be divided into four valid chunks.')],[[x] for x in [[1],[2,1],[1,2],[5,4,3,2,1],[2,1,3,4,4],[1,1,0,0,1],[0,0],[1,0,1,3,2],[4,2,2,1,1],[1,3,2,4],[2,0,1],[3,3,2,2,1,1],[-1,-2,0],[2,1,2,1]]],CHUNKS,[CHUNKS.replace('left+=a','left-=a'),CHUNKS.replace('if left==right','if left<=right')],['Subtracts original-prefix values instead of accumulating them.','Cuts at prefixes whose sum has not yet reached the sorted prefix sum.'],chunks_o,rchunks,['Compare each original prefix with the same-length prefix of sorted(arr).','Maintain their running sums and cut whenever the sums match.','Count every matching boundary.','The sorted prefix contains the globally smallest values, so an equal sum is possible only when the two prefix multisets agree; every such independent boundary should be used.'],'O(n log n)','O(n)',8),
773:entry('sliding_puzzle_moves',[('board','list[list[int]]')],'int',['matrices','breadth-first search'],['board is two by three and contains each value zero through five exactly once.','A move swaps zero with an orthogonally adjacent tile.','Return the fewest moves to reach rows [1,2,3] and [4,5,0], or -1.'],[([[[1,2,3],[4,0,5]]],'Swapping zero with five reaches the target in one move.'),([[[1,2,3],[5,4,0]]],'This parity class cannot reach the target.')],[[b] for b in [[[1,2,3],[4,5,0]],[[1,2,3],[4,0,5]],[[1,2,3],[5,4,0]],[[4,1,2],[5,0,3]],[[3,2,4],[1,5,0]],[[1,2,0],[4,5,3]],[[1,0,3],[4,2,5]],[[0,1,2],[3,4,5]],[[1,3,5],[4,2,0]],[[2,1,3],[4,5,0]],[[4,0,2],[1,3,5]],[[5,4,3],[2,1,0]],[[3,1,2],[0,4,5]],[[2,3,5],[1,4,0]]]],PUZZLE,[PUZZLE.replace('(1,2,3,4,5,0)','(1,2,3,4,0,5)'),PUZZLE.replace('distance+1','distance+2')],['Searches for the wrong target arrangement.','Charges two moves for every legal swap.'],puzzle_o,rpuzzle,['Encode the six cells as an immutable tuple.','Breadth-first search tuple states; zero’s position determines its legal swap indices.','Return the layer where the target first appears.','Every edge is one move, so BFS first reaches each state by its shortest path and exhausts the reachable parity class before returning -1.'],'O(6!*6)','O(6!)',8),
}
BATCH[758]['wrong'][1]=BOLD.replace("while j<len(s) and marked[j]:j+=1","j+=1")
BATCH[758]['wrong_reasons'][1]='Wraps only the first character of every bold region.'
BATCH[768]['wrong'][1]=CHUNKS.replace('if left==right','if left!=right')
BATCH[768]['wrong_reasons'][1]='Cuts at precisely the prefixes whose multisets do not match.'
