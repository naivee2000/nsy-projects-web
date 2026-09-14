"""Third reviewed group of workbook batch 117."""
from itertools import combinations
from .import_batch_055 import entry

def cipher_o(a):
 text,rows=a;cols=len(text)//rows;grid=[text[i*cols:(i+1)*cols] for i in range(rows)];out=[]
 for col in range(cols):
  for row in range(rows):
   if col+row<cols:out.append(grid[row][col+row])
 return ''.join(out).rstrip()
def friends_o(a):
 n,restrictions,requests=a;groups=[{i} for i in range(n)];answer=[]
 for u,v in requests:
  gu=next(g for g in groups if u in g);gv=next(g for g in groups if v in g)
  allowed=gu is gv or not any((x in gu and y in gv) or (y in gu and x in gv) for x,y in restrictions)
  answer.append(allowed)
  if allowed and gu is not gv:gu|=gv;groups.remove(gv)
 return answer
def paths_o(a):
 n,edges=a;e={tuple(sorted(x)) for x in edges}
 return sum(all(tuple(sorted(x)) in e for x in ((i,j),(i,k),(j,k))) for i,j,k in combinations(range(1,n+1),3))
def colors_o(a):
 c=a[0];return max((j-i for i in range(len(c)) for j in range(i+1,len(c)) if c[i]!=c[j]),default=0)
def plants_o(a):
 plants,capacity=a;position=-1;water=capacity;steps=0
 for i,need in enumerate(plants):
  if water<need:steps+=position+1;position=-1;water=capacity
  steps+=i-position;position=i;water-=need
 return steps
def rcipher(r):
 rows=r.randint(1,6);cols=r.randint(1,8);return [''.join(r.choice('abc ') for _ in range(rows*cols)),rows]
def rfriends(r):
 n=r.randint(2,7);pairs=list(combinations(range(n),2));r.shuffle(pairs);restr=[list(x) for x in pairs[:r.randint(0,min(5,len(pairs)))]];r.shuffle(pairs);return [n,restr,[list(x) for x in pairs[:r.randint(1,min(8,len(pairs)))]]]
def rpaths(r):
 n=r.randint(2,9);return [n,[list(x) for x in combinations(range(1,n+1),2) if r.random()<.3]]
def rcolors(r):return [[r.randint(1,5) for _ in range(r.randint(2,20))]]
def rplants(r):
 cap=r.randint(1,12);return [[r.randint(1,cap) for _ in range(r.randint(1,20))],cap]

CIPHER='''\
def decode_slanted_ciphertext(encoded_text,rows):
    columns=len(encoded_text)//rows;answer=[]
    for start in range(columns):
        row,column=0,start
        while row<rows and column<columns:
            answer.append(encoded_text[row*columns+column]);row+=1;column+=1
    return ''.join(answer).rstrip()
'''
FRIENDS='''\
def restricted_friend_requests(n,restrictions,requests):
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    answer=[]
    for u,v in requests:
        ru,rv=find(u),find(v);allowed=True
        if ru!=rv:
            for x,y in restrictions:
                rx,ry=find(x),find(y)
                if (ru==rx and rv==ry) or (ru==ry and rv==rx):allowed=False;break
        answer.append(allowed)
        if allowed and ru!=rv:parent[ru]=rv
    return answer
'''
PATHS='''\
def count_triangle_rooms(n,corridors):
    graph=[set() for _ in range(n+1)]
    for a,b in corridors:graph[a].add(b);graph[b].add(a)
    answer=0
    for room in range(1,n+1):
        neighbors=sorted(graph[room])
        for i in range(len(neighbors)):
            for j in range(i+1,len(neighbors)):
                if neighbors[j] in graph[neighbors[i]]:answer+=1
    return answer//3
'''
COLORS='''\
def furthest_different_houses(colors):
    answer=0
    for index,color in enumerate(colors):
        if color!=colors[0]:answer=max(answer,index)
        if color!=colors[-1]:answer=max(answer,len(colors)-1-index)
    return answer
'''
PLANTS='''\
def watering_steps(plants,capacity):
    steps=0;water=capacity
    for index,need in enumerate(plants):
        if water<need:steps+=2*index;water=capacity
        steps+=1;water-=need
    return steps
'''
def L(*x):return list(x)
BATCH={
2075:entry('decode_slanted_ciphertext',[('encoded_text','str'),('rows','int')],'str',['strings','matrix simulation'],['encoded_text length is divisible by rows and represents the row-wise contents of the encoding matrix.','Read diagonals starting in the top row, moving down one row and right one column.','Remove trailing spaces only; preserve spaces inside the decoded message.'],[(['ch   ie   pr',3],'Reading the three top-row diagonals produces cipher.'),(['iveo    eed   l te   olc',4],'Diagonal reading reconstructs i love leetcode after trailing padding is removed.')],[[s,r] for s,r in [('a',1),('abc',1),('a b ',2),('abcd',2),('abcdefghi',3),('abcdefghijkl',3),('abcdefghijkl',4),('    ',2),('ab  cd  ',2),('x y z ',3),('python      ',2),('123456',2),('hello world ',3),('abcdefghijklmnop',4)]],CIPHER,[CIPHER.replace('column+=1','column+=2'),CIPHER.replace(".rstrip()",".strip()")],['Moves two columns per row and skips diagonal cells.','Removes meaningful leading whitespace instead of only padding at the end.'],cipher_o,rcipher,L('The encoded string is a row-major matrix with len(text)//rows columns.','Start once at every top-row column and walk down-right until leaving the matrix.','Append matrix[row][start+row] for each valid row, then rstrip the result.','Those diagonals are exactly the original write order; right stripping removes only encoding padding.'),'O(length)','O(length)',5),
2076:entry('restricted_friend_requests',[('n','int'),('restrictions','list[list[int]]'),('requests','list[list[int]]')],'list[bool]',['union find','graphs'],['People are numbered zero through n-1; each restriction forbids its two eventual friend groups from merging.','Process requests in order, permanently merging groups only for accepted requests.','Return one Boolean per request.'],[([3,[[0,1]],[[0,2],[2,1]]],'The first merge joins zero and two; the second would then connect restricted people zero and one.'),([5,[[0,1],[2,3]],[[0,4],[1,2],[3,1],[3,4]]],'The decisions reflect all group merges made by earlier accepted requests.')],[[n,r,q] for n,r,q in [(2,[],[[0,1]]),(2,[[0,1]],[[0,1]]),(3,[],[[0,1],[1,2]]),(3,[[0,2]],[[0,1],[1,2]]),(4,[[0,1]],[[2,3],[0,2],[1,3]]),(4,[[0,3]],[[0,1],[2,3],[1,2]]),(5,[[0,1],[2,3]],[[0,4]]),(5,[[0,4]],[[0,1],[1,2],[2,3]]),(3,[[0,1]],[[0,2],[0,2]]),(6,[[0,5],[1,4]],[[0,1],[2,3],[3,4]]),(4,[],[[0,1],[0,2],[0,3]]),(4,[[1,3]],[[0,1],[2,3],[0,2]]),(5,[[0,2]],[[3,4],[1,3],[0,4]]),(3,[[0,1]],[[1,2],[0,2]])]],FRIENDS,[FRIENDS.replace('answer.append(allowed)','answer.append(True)'),FRIENDS.replace('if allowed and ru!=rv','if ru!=rv')],['Reports every request accepted even when a restriction blocks it.','Merges groups even after rejecting a request, corrupting later decisions.'],friends_o,rfriends,L('Restrictions apply to connected components, not merely the two requested people.','Use union-find; before merging roots, test every restriction after mapping both endpoints to current roots.','Reject when a restriction crosses the two proposed roots; otherwise union them.','A merge is safe exactly when no forbidden pair would become connected, and accepted unions preserve all prior friendship decisions.'),'O(requests*(restrictions*alpha(n)))','O(n)',8),
2077:entry('count_triangle_rooms',[('n','int'),('corridors','list[list[int]]')],'int',['graphs','sets','counting'],['Rooms are numbered one through n and corridors are distinct undirected edges.','Count unordered triples in which every pair of rooms has a corridor.','Return the number of distinct triangular cycles.'],[([5,[[1,2],[5,2],[4,1],[2,4],[3,1],[3,4]]],'Rooms 1,2,4 and rooms 1,3,4 form the two triangles.'),([4,[[1,2],[2,3],[3,4]]],'A path contains no three mutually connected rooms.')],[[n,e] for n,e in [(2,[]),(3,[]),(3,[[1,2],[2,3]]),(3,[[1,2],[2,3],[1,3]]),(4,[[1,2],[2,3],[1,3],[1,4],[2,4]]),(4,[[1,2],[2,3],[3,4],[4,1]]),(5,[[1,2],[1,3],[2,3]]),(5,[[3,4],[4,5],[3,5]]),(6,[[1,2],[2,3],[1,3],[4,5],[5,6],[4,6]]),(4,[[1,2]]),(5,[]),(5,[[1,2],[1,3],[1,4],[1,5]]),(4,[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]),(6,[[1,6],[2,6],[1,2]])]],PATHS,[PATHS.replace('return answer//3','return answer'),PATHS.replace('neighbors[j] in graph[neighbors[i]]','neighbors[j] not in graph[neighbors[i]]')],['Counts every triangle once from each of its three rooms.','Counts open wedges instead of closed triangles.'],paths_o,rpaths,L('A triangle is detected at each vertex by an edge between two of its neighbors.','Store neighbor sets, inspect every neighbor pair, and divide the total by three.','For each room and each pair j,k in graph[room], add one if k is in graph[j].','Every triangle contributes at exactly its three vertices and no non-triangle contributes.'),'O(sum of squared degrees)','O(n+corridors)',5),
2078:entry('furthest_different_houses',[('colors','list[int]')],'int',['arrays','greedy'],['At least two houses are given and adjacent houses may share colors.','Distance is the absolute index difference; choose two houses with different colors.','Return the greatest possible distance.'],[([[1,1,1,6,1,1,1]],'The differently colored house at index three is distance three from either endpoint.'),([[1,8,3,8,3]],'The endpoints have different colors, giving the maximum possible distance four.')],[[x] for x in [[1,2],[1,1,2],[1,2,1],[1,2,2],[1,1,1,2],[2,1,1,1],[1,2,3],[3,3,2,3],[4,1,4,4,4],[1,1,2,2,1],[5,6,5,6,5,6],[9,9,9,8,9],[1,2,1,1,1,1],[7,7,6,6,5,7]]],COLORS,[COLORS.replace('len(colors)-1-index','len(colors)-2-index'),COLORS.replace('color!=colors[0]','color==colors[0]')],['Understates distances measured from the right endpoint by one.','Treats equal colors as a valid left-endpoint pair.'],colors_o,rcolors,L('At least one member of an optimal pair can be replaced by an endpoint without reducing distance.','Compare every house to the first and last colors while tracking the largest endpoint distance.','If color differs from first use index; if it differs from last use n-1-index.','For any different-colored pair, at least one color differs from the opposite endpoint, whose distance is no smaller.'),'O(n)','O(1)',3),
2079:entry('watering_steps',[('plants','list[int]'),('capacity','int')],'int',['arrays','simulation'],['Plants are watered from left to right; every need is at most capacity.','Start at the river immediately before index zero and refill only when remaining water cannot satisfy the next plant.','Return the total number of one-position steps.'],[([[2,2,3,3],5],'A refill before plant two adds four return-and-approach steps, for fourteen total.'),([[1,1,1,4,2,3],4],'Refills before plants three, four, and five produce thirty steps.')],[[p,c] for p,c in [([1],1),([1],5),([2,2],4),([2,2],3),([3,1,1],3),([1,3,1],3),([5,5,5],5),([1,1,1],2),([4,1,2],5),([2,4,1],4),([1,2,3,4],5),([2,1,2,1],3),([6,1,6],6),([1,1,5,1,1],5)]],PLANTS,[PLANTS.replace('2*index','2*index+1'),PLANTS.replace('water<need','water<=need')],['Adds an extra step on every refill trip.','Refills unnecessarily when the can contains exactly the needed amount.'],plants_o,rplants,L('Walking from the previous plant to the next costs one unless a refill is required.','At index i, a refill adds i steps back to the river and i steps to return to the previous position.','When water<need add 2*i, reset capacity, then always add one to reach and water the plant.','The simulation mirrors the only allowed route and accounts for every forward and refill step exactly once.'),'O(n)','O(1)',5)
}

BATCH[2075]['wrong'][1]=CIPHER.replace("return ''.join(answer).rstrip()","return ''.join(answer).rstrip()[:-1]")
BATCH[2075]['wrong_reasons'][1]='Drops the final decoded character through an off-by-one slice.'
BATCH[2075]['sample_contract_adapter']={
 'source_sample':'Input encodedText = "ch ie pr", rows = 3 → Output "cipher".',
 'arguments':['ch   ie   pr',3],
 'expected':'cipher',
 'reason':'The workbook display collapsed four matrix-padding spaces; the reviewed adapter restores the 3-by-4 row-major encoded text while preserving its stated decoded result.'
}
