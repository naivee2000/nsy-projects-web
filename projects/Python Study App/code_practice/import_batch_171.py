"""Color adjacency, perfect-tree costs, passenger ages, matrix rounds, and OR batch 171."""

from itertools import product

from .import_batch_055 import entry


def colors_oracle(args):
    n,queries=args;values=[0]*n;answer=[]
    for index,color in queries:
        values[index]=color
        answer.append(sum(values[i]!=0 and values[i]==values[i+1] for i in range(n-1)))
    return answer


def random_colors(rng):
    n=rng.randint(1,20)
    return [n,[[rng.randrange(n),rng.randint(1,6)] for _ in range(rng.randint(1,30))]]


def tree_cost_oracle(args):
    n,cost=args;bound=sum(cost)+1
    def solve(index):
        if 2*index>n:return {total:total-cost[index-1] for total in range(cost[index-1],bound+1)}
        left,right=solve(2*index),solve(2*index+1);result={}
        for child_total in set(left)&set(right):
            base=left[child_total]+right[child_total]
            for increment in range(bound-(cost[index-1]+child_total)+1):
                total=cost[index-1]+child_total+increment
                result[total]=min(result.get(total,10**9),base+increment)
        return result
    return min(solve(1).values())


def random_tree_cost(rng):
    n=rng.choice((1,3,7))
    return [n,[rng.randint(1,6) for _ in range(n)]]


def seniors_oracle(args):
    return sum(60<int(detail[11])*10+int(detail[12]) for detail in args[0])


def random_seniors(rng):
    details=[]
    for _ in range(rng.randint(1,20)):
        age=rng.randint(0,99);details.append(''.join(str(rng.randrange(10)) for _ in range(10))+rng.choice('MF')+f'{age:02d}'+f'{rng.randint(0,99):02d}')
    return [details]


def matrix_oracle(args):
    rows=[row.copy() for row in args[0]];score=0
    while rows[0]:
        selected=[]
        for row in rows:
            largest=max(row);row.remove(largest);selected.append(largest)
        score+=max(selected)
    return score


def random_matrix(rng):
    rows,columns=rng.randint(1,8),rng.randint(1,8)
    return [[[rng.randint(1,100) for _ in range(columns)] for _ in range(rows)]]


def maximum_oracle(args):
    nums,k=args;best=0
    def assign(index,remaining,values):
        nonlocal best
        if index==len(nums)-1:
            result=0
            for value,shift in zip(nums,values+[remaining]):result|=value<<shift
            best=max(best,result);return
        for shift in range(remaining+1):assign(index+1,remaining-shift,values+[shift])
    assign(0,k,[]);return best


def random_or(rng):return [[rng.randint(0,100) for _ in range(rng.randint(1,7))],rng.randint(0,6)]


COLORS="""\
def adjacent_equal_colors(n,queries):
    colors=[0]*n;answer=[];pairs=0
    for index,color in queries:
        for neighbor in (index-1,index+1):
            if 0<=neighbor<n and colors[index]!=0 and colors[neighbor]==colors[index]:pairs-=1
        colors[index]=color
        for neighbor in (index-1,index+1):
            if 0<=neighbor<n and colors[neighbor]==color:pairs+=1
        answer.append(pairs)
    return answer
"""

TREE_COST="""\
def minimum_equal_path_increments(n,cost):
    cost=cost.copy();answer=0
    for node in range(n//2,0,-1):
        left=cost[2*node-1];right=cost[2*node]
        answer+=abs(left-right);cost[node-1]+=max(left,right)
    return answer
"""

SENIORS="""\
def count_senior_passengers(details):
    return sum(int(detail[11:13])>60 for detail in details)
"""

MATRIX="""\
def matrix_round_score(nums):
    rows=[sorted(row) for row in nums]
    return sum(max(row[column] for row in rows) for column in range(len(rows[0])))
"""

MAXIMUM_OR="""\
def maximum_or_after_doublings(nums,k):
    suffix=[0]*(len(nums)+1)
    for index in range(len(nums)-1,-1,-1):suffix[index]=suffix[index+1]|nums[index]
    prefix=answer=0
    for index,value in enumerate(nums):
        answer=max(answer,prefix|(value<<k)|suffix[index+1]);prefix|=value
    return answer
"""


BATCH={
2672:entry('adjacent_equal_colors',[('n','int'),('queries','list[list[int]]')],'list[int]',['arrays','simulation'],
 ['Begin with n uncolored positions represented by zero.','Each query [index,color] replaces that position with a positive color.','After every query, return the number of adjacent pairs having the same nonzero color.'],
 [([4,[[0,2],[1,2],[3,1],[1,1],[2,1]]],'The equal-adjacency counts after the five replacements are 0, 1, 1, 0, and 2.'),([1,[[0,1],[0,2]]],'A one-position array has no adjacent pair after either query.')],
 [[n,q] for n,q in [(1,[[0,1]]),(2,[[0,1],[1,1]]),(2,[[0,1],[1,2]]),(3,[[1,3],[0,3],[2,3]]),(3,[[0,1],[1,1],[1,2]]),(4,[[0,2],[1,2],[3,1],[1,1],[2,1]]),(5,[[2,1],[1,1],[3,1],[2,2]]),(4,[[0,1],[3,1],[1,1],[2,1]]),(6,[[1,2],[2,2],[3,2],[4,2]]),(3,[[0,1],[1,1],[2,1],[1,1]]),(5,[[4,3],[3,3],[2,3],[1,3],[0,3]]),(4,[[1,1],[2,1],[1,2],[2,2]]),(2,[[0,5],[1,5],[0,6]]),(7,[[3,1],[2,1],[4,1],[3,2]])]],
 COLORS,[COLORS.replace('colors[index]!=0 and ','',1),COLORS.replace('pairs-=1','pairs+=1')],
 ['Treats two initial zero colors as a removable colored pair.','Adds obsolete matching pairs instead of removing them before recoloring.'],colors_oracle,random_colors,
 ['Only pairs touching the updated index can change.','Before recoloring, subtract its matches with nonzero neighbors.','Assign the new color, add its new neighbor matches, and append the running total.','All untouched pairs preserve status, and the two local passes remove exactly the old contributions before adding exactly the new ones.'],'O(n+queries)','O(n)',5),
2673:entry('minimum_equal_path_increments',[('n','int'),('cost','list[int]')],'int',['trees','dynamic programming','greedy'],
 ['Nodes one through n form a perfect binary tree in heap order and cost[i-1] is node i’s positive cost.','You may increment any node cost by one per operation.','Return the minimum operations making every root-to-leaf path sum equal.'],
 [([7,[1,5,2,2,3,3,1]],'Balancing sibling subtrees bottom-up requires six total increments.'),([3,[5,3,3]],'Both root-to-leaf paths already cost eight, so no increment is needed.')],
 [[n,c] for n,c in [(1,[1]),(3,[1,1,1]),(3,[1,2,3]),(3,[5,3,3]),(7,[1,5,2,2,3,3,1]),(7,[1,1,1,1,1,1,1]),(7,[5,1,1,1,2,3,4]),(7,[2,4,6,8,10,12,14]),(7,[10,1,9,1,1,1,1]),(3,[100,1,100]),(7,[3,2,4,8,1,5,9]),(7,[1,10,1,1,1,10,1]),(7,[7,6,5,4,3,2,1]),(3,[2,8,4])]],
 TREE_COST,[TREE_COST.replace('abs(left-right)','left-right'),TREE_COST.replace('max(left,right)','min(left,right)')],
 ['Adds a signed imbalance, allowing negative operation counts.','Propagates the cheaper child path upward instead of the balanced maximum.'],tree_cost_oracle,random_tree_cost,
 ['Process internal nodes from the deepest level upward.','Sibling subtrees must end with equal path cost, so raise the cheaper side by their absolute difference.','Add the larger balanced child path cost into the parent before continuing upward.','Each sibling imbalance must be paid somewhere exclusively in its cheaper subtree; paying it immediately is sufficient and leaves the exact common cost needed by the parent.'],'O(n)','O(n)',5),
2678:entry('count_senior_passengers',[('details','list[str]')],'int',['arrays','strings'],
 ['Each fixed-length detail string stores a ten-digit phone number, one gender character, a two-digit age, and a two-digit seat number.','The age occupies zero-based positions eleven and twelve.','Return the number of passengers strictly older than sixty.'],
 [([['7868190130M7522','5303914400F9211','9273338290F4010']],'The first two ages are 75 and 92, so two passengers are over sixty.'),([['1313579440F2036','2921522980M5644']],'Ages twenty and fifty-six produce zero senior passengers.')],
 [[d] for d in [['0000000000M0000'],['0000000000F6001'],['0000000000M6102'],['1234567890F9900'],['1111111111M5901','2222222222F6102'],['1111111111M6010','2222222222F6020'],['9999999999F7001','8888888888M8002','7777777777F5003'],['1231231231M0101'],['0000000000F6500','0000000001M6501'],['1234567890M6205','0987654321F6006'],['3141592653F7309'],['2718281828M0904','1618033988F9108'],['5555555555M6000','4444444444F6100','3333333333M6200'],['1010101010F9999']]],
 SENIORS,[SENIORS.replace('>60','>=60'),SENIORS.replace('[11:13]','[12:13]')],
 ['Counts exactly sixty-year-old passengers as seniors.','Uses only the ones digit of each age.'],seniors_oracle,random_seniors,
 ['Use the fixed field positions rather than parsing the other fields.','Slice characters eleven through twelve inclusive.','Convert the two digits to an integer and count values greater than sixty.','Every record has the same layout, so the slice isolates exactly its age and the strict comparison matches the definition.'],'O(passengers)','O(1)',3),
2679:entry('matrix_round_score',[('nums','list[list[int]]')],'int',['matrices','sorting','simulation'],
 ['Every row has the same positive length.','In each round remove the largest remaining number from every row, then add the largest removed number to the score.','Return the score after all columns’ worth of rounds.'],
 [([[[7,2,1],[6,4,2],[6,5,3],[3,2,1]]],'Round maxima seven, five, and three sum to fifteen.'),([[[1],[2],[3]]],'The only round removes all values and contributes the largest, three.')],
 [[m] for m in [[[1]],[[1],[2]],[[1,2]],[[2,1]],[[1,2],[3,4]],[[4,3],[2,1]],[[1,1],[1,1]],[[7,2,1],[6,4,2],[6,5,3],[3,2,1]],[[5,10],[8,7]],[[1,9,3],[4,2,8]],[[100,1],[50,60],[70,20]],[[3,3,1],[2,2,4]],[[1,2,3,4],[4,3,2,1]],[[9],[1],[5],[7]]]],
 MATRIX,[MATRIX.replace('sorted(row)','row.copy()'),MATRIX.replace('max(row[column] for row in rows)','min(row[column] for row in rows)')],
 ['Aligns values by their original columns instead of by each row’s removal order.','Adds the smallest selected row value each round.'],matrix_oracle,random_matrix,
 ['Sort each row ascending.','At a fixed sorted column, those values are exactly the elements removed in the same round when maxima are removed repeatedly.','Add the maximum across rows for each column.','Sorting only reorders each row’s removal sequence, and every round contribution is therefore represented by one aligned column maximum.'],'O(rows*columns log columns)','O(rows*columns)',5),
2680:entry('maximum_or_after_doublings',[('nums','list[int]'),('k','int')],'int',['arrays','bit manipulation','prefix sums'],
 ['One operation doubles one array element, and you may perform at most k operations total.','Return the maximum possible bitwise OR of all array values afterward.','Applying all k doublings to one chosen value is sufficient to consider for an optimum.'],
 [([[12,9],1],'Shifting twelve once gives twenty-four, and 24 OR 9 equals thirty.'),([[8,1,2],2],'Shifting eight twice gives thirty-two; OR with one and two gives thirty-five.')],
 [[a,k] for a,k in [([0],0),([1],0),([1],1),([1],5),([1,2],1),([12,9],1),([8,1,2],2),([1,2,4],3),([7,7],2),([0,5,0],4),([10,3,5],0),([15,1],3),([2,8,16,1],2),([100,50,25],5)]],
 MAXIMUM_OR,[MAXIMUM_OR.replace('value<<k','value<<(k-1)'),MAXIMUM_OR.replace('prefix|=value','prefix=value')],
 ['Applies only k-1 doublings to the selected value.','Forgets earlier prefix values instead of accumulating their OR.'],maximum_oracle,random_or,
 ['Precompute suffix OR values and maintain a prefix OR while scanning candidate shifted elements.','For candidate i, combine prefix OR, nums[i] shifted left k bits, and the suffix after i.','Take the maximum across every candidate index.','Doublings only shift bits left; concentrating them avoids splitting away the highest attainable bit, and prefix/suffix OR includes every unshifted element exactly once.'],'O(n)','O(n)',5),
}
