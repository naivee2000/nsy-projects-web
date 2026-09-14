"""Third reviewed group of workbook batch 120."""
from collections import deque
from itertools import combinations
from .import_batch_055 import entry

def hidden_o(a):
 differences,lower,upper=a;prefix=[0]
 for d in differences:prefix.append(prefix[-1]+d)
 return sum(all(lower<=start+x<=upper for x in prefix) for start in range(lower,upper+1))
def ranked_o(a):
 grid,pricing,start,k=a;rows=len(grid);cols=len(grid[0]);distance={tuple(start):0};queue=deque([tuple(start)])
 while queue:
  r,c=queue.popleft()
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] and (nr,nc) not in distance:distance[(nr,nc)]=distance[(r,c)]+1;queue.append((nr,nc))
 low,high=pricing;items=sorted((d,grid[r][c],r,c) for (r,c),d in distance.items() if low<=grid[r][c]<=high)
 return [[r,c] for _,_,r,c in items[:k]]
def corridor_o(a):
 text=a[0];answer=0
 for mask in range(1<<(len(text)-1)):
  pieces=[];start=0
  for i in range(len(text)-1):
   if mask>>i&1:pieces.append(text[start:i+1]);start=i+1
  pieces.append(text[start:]);answer+=all(piece.count('S')==2 for piece in pieces)
 return answer%(10**9+7)
def elements_o(a):
 nums=a[0];return sum(any(y<x for y in nums) and any(y>x for y in nums) for x in nums)
def signs_o(a):
 nums=a[0];positive=[x for x in nums if x>0];negative=[x for x in nums if x<0];return [x for pair in zip(positive,negative) for x in pair]
def rhidden(r):return [[r.randint(-5,5) for _ in range(r.randint(1,12))],r.randint(-10,0),r.randint(1,10)]
def rranked(r):
 rows,cols=r.randint(1,5),r.randint(1,5);grid=[[r.randint(0,8) for _ in range(cols)] for _ in range(rows)];start=[r.randrange(rows),r.randrange(cols)];grid[start[0]][start[1]]=max(1,grid[start[0]][start[1]]);a,b=sorted((r.randint(2,8),r.randint(2,8)));return [grid,[a,b],start,r.randint(1,8)]
def rcorridor(r):return [''.join(r.choice('SP') for _ in range(r.randint(1,12)))]
def relements(r):return [[r.randint(-10,10) for _ in range(r.randint(1,20))]]
def rsigns(r):
 n=r.randint(1,8);values=[r.randint(1,20) for _ in range(n)]+[-r.randint(1,20) for _ in range(n)];r.shuffle(values);return [values]

HIDDEN='''\
def count_hidden_sequences(differences,lower,upper):
    current=smallest=largest=0
    for difference in differences:
        current+=difference;smallest=min(smallest,current);largest=max(largest,current)
    return max(0,upper-lower-(largest-smallest)+1)
'''
RANKED='''\
def highest_ranked_items(grid,pricing,start,k):
    from collections import deque
    rows,cols=len(grid),len(grid[0]);low,high=pricing;queue=deque([tuple(start)]);distance={tuple(start):0};items=[]
    while queue:
        row,col=queue.popleft();value=grid[row][col]
        if low<=value<=high:items.append((distance[(row,col)],value,row,col))
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,col+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]>0 and (nr,nc) not in distance:
                distance[(nr,nc)]=distance[(row,col)]+1;queue.append((nr,nc))
    items.sort();return [[row,col] for _,_,row,col in items[:k]]
'''
CORRIDOR='''\
def corridor_division_ways(corridor):
    seats=[i for i,char in enumerate(corridor) if char=='S']
    if not seats or len(seats)%2:return 0
    answer=1;mod=10**9+7
    for index in range(2,len(seats),2):answer=answer*(seats[index]-seats[index-1])%mod
    return answer
'''
ELEMENTS='''\
def count_strictly_between_elements(nums):
    smallest,largest=min(nums),max(nums)
    return sum(smallest<value<largest for value in nums)
'''
SIGNS='''\
def alternate_array_signs(nums):
    positive=[value for value in nums if value>0];negative=[value for value in nums if value<0];answer=[]
    for pos,neg in zip(positive,negative):answer.extend((pos,neg))
    return answer
'''
def L(*x):return list(x)
BATCH={
2145:entry('count_hidden_sequences',[('differences','list[int]'),('lower','int'),('upper','int')],'int',['arrays','prefix sums'],['A hidden sequence has one more value than differences and every value lies inclusively between lower and upper.','Consecutive hidden values differ by the corresponding differences entry.','Return the number of possible integer sequences.'],[([[1,-3,4],1,6],'The relative prefix range has width four, leaving two valid starting values.'),([[3,-4,5,1,-2],-4,5],'The cumulative spread exceeds the permitted interval, so no sequence exists.')],[[d,l,u] for d,l,u in [([0],0,0),([1],0,1),([2],0,1),([-1],0,1),([1,-1],0,1),([5,-5],1,6),([1,1,1],0,5),([-1,-1],-3,0),([2,-3,2],-2,3),([0,0,0],-1,1),([10],-10,10),([3,-1,-2],5,5),([4,-8,4],-4,4),([1,-3,4],-10,10)]],HIDDEN,[HIDDEN.replace('+1)',')'),HIDDEN.replace('largest-smallest','largest+smallest')],['Omits one valid endpoint starting value.','Adds the prefix extremes instead of measuring their spread.'],hidden_o,rhidden,L('All hidden sequences are translations of the same cumulative-difference prefix sequence.','Find the minimum and maximum relative prefix values; a start must keep both within the allowed range.','Return max(0,(upper-lower)-(maximum-minimum)+1).','Every intermediate prefix lies between the extrema, so satisfying the two extreme bounds is necessary and sufficient.'),'O(n)','O(1)',5),
2146:entry('highest_ranked_items',[('grid','list[list[int]]'),('pricing','list[int]'),('start','list[int]'),('k','int')],'list[list[int]]',['matrices','breadth first search','sorting'],['Grid zero cells are walls, one cells are empty, and values above one are item prices; start is traversable.','Rank reachable in-range items by distance, then price, row, and column ascending.','Return up to k item coordinates in exact rank order without modifying grid.'],[([[[1,2,0,1],[1,3,0,1],[0,2,5,1]],[2,5],[0,0],3],'The closest price-two item ranks first, followed by price three and the farther price-two item.'),([[[1,2],[3,4]],[2,3],[0,0],5],'Only two reachable items have in-range prices, so both are returned.')],[[g,p,s,k] for g,p,s,k in [([[1]],[2,5],[0,0],1),([[2]],[2,2],[0,0],1),([[1,0,2]],[2,3],[0,0],2),([[1,2,3]],[2,3],[0,0],2),([[1,2],[3,4]],[2,4],[0,0],4),([[1,2],[2,2]],[2,2],[0,0],2),([[1,0],[2,3]],[2,3],[0,0],3),([[1,5,2],[1,1,1]],[2,5],[1,1],2),([[1,2,0],[1,3,4]],[2,4],[0,0],3),([[5,1],[2,3]],[2,5],[0,0],1),([[1,1,1],[2,0,3],[4,1,5]],[2,5],[0,0],5),([[1,9],[8,7]],[7,9],[1,1],3),([[1,2,3],[4,5,6]],[3,5],[0,0],2),([[1,0,5],[1,1,1],[2,3,4]],[2,5],[0,0],4)]],RANKED,[RANKED.replace('items.sort()','items.sort(reverse=True)'),RANKED.replace('grid[nr][nc]>0','grid[nr][nc]>=0')],['Sorts every ranking criterion in descending order.','Walks through wall cells and reaches items that should be blocked.'],ranked_o,rranked,L('Breadth-first search supplies shortest distances; the remaining tie-breakers can be sorted afterward.','Traverse only positive cells from start, recording each in-range item as (distance,price,row,column).','Sort recorded tuples and return the first k coordinate pairs.','BFS distances are minimal, and tuple order exactly matches all four ranking rules.'),'O(rows*cols log(rows*cols))','O(rows*cols)',6),
2147:entry('corridor_division_ways',[('corridor','str')],'int',['strings','combinatorics','dynamic programming'],['corridor contains seats S and plants P.','Place dividers so every nonempty section contains exactly two seats.','Return the number of divider sets modulo 1000000007, or zero when impossible.'],[(['SSPPSPS'],'After the first seat pair, three boundaries before the next pair yield three valid divisions.'),(['PPSPSP'],'Only two seats exist, so the undivided corridor is the single valid division.')],[[s] for s in ['S','SS','PPP','SPPS','SSSS','SPSP','SSPPSPS','PSSP','SSPPSS','SPPSPSPS','SSPPPPSS','SSSSSS','PPSPSP','SSPSSPSS']],CORRIDOR,[CORRIDOR.replace('len(seats)%2','len(seats)%3'),CORRIDOR.replace('seats[index]-seats[index-1]','seats[index]-seats[index-1]+1')],['Checks seat divisibility by three instead of requiring an even count.','Adds one nonexistent divider position between consecutive seat pairs.'],corridor_o,rcorridor,L('Once seats are paired from left to right, each gap between pairs independently chooses one divider boundary.','Record seat indices; reject zero or odd seat counts, then multiply the plant-gap boundary counts.','For pair boundary index i=2,4,... multiply seats[i]-seats[i-1].','Every section must use consecutive seat pairs, and each chosen boundary in the intervening gap produces one unique valid partition.'),'O(n)','O(number of seats)',8),
2148:entry('count_strictly_between_elements',[('nums','list[int]')],'int',['arrays','counting'],['nums is nonempty and may contain duplicates.','Count occurrences having some strictly smaller value and some strictly greater value elsewhere.','Return the number of qualifying occurrences.'],[([[11,7,2,15]],'Seven and eleven lie strictly between the minimum two and maximum fifteen.'),([[-3,3,3,90]],'Both occurrences of three qualify, so the answer is two.')],[[x] for x in [[1],[1,2],[1,2,3],[3,2,1],[1,1,2],[1,2,2,3],[0,0,0],[-1,0,1],[5,4,5],[2,3,4,3,2],[10,-10,0,0],[1,5,2,5,1],[7,8,9,10],[3,1,4,1,5]]],ELEMENTS,[ELEMENTS.replace('smallest<value<largest','smallest<=value<=largest'),ELEMENTS.replace('min(nums),max(nums)','nums[0],nums[-1]')],['Includes minimum and maximum occurrences by using non-strict comparisons.','Assumes the input endpoints are already its extrema.'],elements_o,relements,L('An element has both witnesses exactly when it is strictly between the global minimum and maximum.','Find the two extrema once, then count occurrences satisfying min<value<max.','Return sum(smallest<value<largest for value in nums).','A smaller and greater witness exist for every interior value, while either extreme necessarily lacks one side.'),'O(n)','O(1)',3),
2149:entry('alternate_array_signs',[('nums','list[int]')],'list[int]',['arrays','stable partition','two pointers'],['nums has even length, equally many positive and negative values, and no zeros.','Output signs alternate beginning positive while preserving relative order within each sign.','Return the uniquely determined rearranged array.'],[([[3,1,-2,-5,2,-4]],'Stable positive order 3,1,2 interleaves with negative order -2,-5,-4.'),([[-1,1]],'The positive value moves first, producing [1,-1].')],[[x] for x in [[1,-1],[-1,1],[1,2,-1,-2],[-1,-2,1,2],[5,-5,4,-4],[1,-3,2,-4,5,-6],[-1,2,-3,4],[10,20,-1,-2],[-9,1,-8,2,-7,3],[3,-1,-2,4],[7,8,9,-3,-2,-1],[-5,-4,6,7],[1,-1,2,-2,3,-3],[100,-1,50,-2]]],SIGNS,[SIGNS.replace('zip(positive,negative)','zip(negative,positive)'),SIGNS.replace('positive=[value for value in nums if value>0]','positive=sorted(value for value in nums if value>0)')],['Begins with a negative and reverses the required sign positions.','Sorts positive values and breaks their original relative order.'],signs_o,rsigns,L('The output is the stable interleaving of the positive subsequence and negative subsequence.','Collect each sign in original order, then append one positive and one negative repeatedly.','For pos,neg in zip(positive,negative), extend [pos,neg].','Equal sign counts fill every output position, and stable extraction plus interleaving enforces both order and alternation.'),'O(n)','O(n)',5)
}
