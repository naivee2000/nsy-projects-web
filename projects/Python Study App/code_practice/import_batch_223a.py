"""Large rectangles, source SCCs, lock assignment, conversions, and split LCPs."""
from itertools import combinations, permutations

from .import_batch_055 import entry


def rectangle_oracle(args):
    xs, ys = args
    points = set(zip(xs, ys)); answer = -1
    for x1, x2 in combinations(sorted(set(xs)), 2):
        for y1, y2 in combinations(sorted(set(ys)), 2):
            corners = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
            if corners <= points and all(point in corners or not (x1 <= point[0] <= x2 and y1 <= point[1] <= y2)
                                         for point in points):
                answer = max(answer, (x2 - x1) * (y2 - y1))
    return answer


def random_rectangle(rng):
    points = rng.sample([(x, y) for x in range(7) for y in range(7)], rng.randint(1, 10))
    return [[point[0] for point in points], [point[1] for point in points]]


def reachable(graph, starts):
    seen = set(starts); stack = list(starts)
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor); stack.append(neighbor)
    return seen


def runes_oracle(args):
    n, crystals, flow_from, flow_to = args
    graph = [[] for _ in range(n)]
    for left, right in zip(flow_from, flow_to): graph[left].append(right)
    missing = sorted(set(range(n)) - reachable(graph, crystals))
    for count in range(len(missing) + 1):
        for added in combinations(missing, count):
            if len(reachable(graph, list(crystals) + list(added))) == n:
                return count


def random_runes(rng):
    n = rng.randint(2, 8)
    possible = [(a, b) for a in range(n) for b in range(n) if a != b]
    edges = rng.sample(possible, rng.randint(1, min(len(possible), 12)))
    crystals = rng.sample(range(n), rng.randint(1, n))
    return [n, crystals, [edge[0] for edge in edges], [edge[1] for edge in edges]]


def locks_oracle(args):
    strength = args[0]
    return min(sum((value + position) // (position + 1)
                   for position, value in enumerate(order))
               for order in permutations(strength))


def random_locks(rng):
    return [[rng.randint(1, 50) for _ in range(rng.randint(1, 7))]]


def conversion_values(initial, pairs, rates):
    graph = {}
    for (left, right), rate in zip(pairs, rates):
        graph.setdefault(left, []).append((right, rate))
        graph.setdefault(right, []).append((left, 1.0 / rate))
    values = {initial: 1.0}; queue = [initial]
    for currency in queue:
        for neighbor, rate in graph.get(currency, []):
            if neighbor not in values:
                values[neighbor] = values[currency] * rate; queue.append(neighbor)
    return values


def conversion_oracle(args):
    initial, pairs1, rates1, pairs2, rates2 = args
    first = conversion_values(initial, pairs1, rates1)
    second = conversion_values(initial, pairs2, rates2)
    return max((amount / second[currency] for currency, amount in first.items() if currency in second), default=1.0)


def random_conversion(rng):
    count = rng.randint(2, 7); names = [chr(65 + index) for index in range(count)]
    def make_tree():
        edges = []; rates = []
        for node in range(1, count):
            parent = rng.randrange(node); edges.append([names[parent], names[node]]); rates.append(float(rng.randint(1, 6)))
        rng.shuffle(edges)
        # Rebuild rates after shuffling so each edge still has an independent valid rate.
        rates = [float(rng.randint(1, 6)) for _ in edges]
        return edges, rates
    pairs1, rates1 = make_tree(); pairs2, rates2 = make_tree()
    return [names[0], pairs1, rates1, pairs2, rates2]


def splits_oracle(args):
    nums = args[0]; answer = 0
    for first in range(1, len(nums) - 1):
        for second in range(first + 1, len(nums)):
            one, two, three = nums[:first], nums[first:second], nums[second:]
            answer += (len(one) <= len(two) and two[:len(one)] == one) or (len(two) <= len(three) and three[:len(two)] == two)
    return answer


def random_splits(rng):
    return [[rng.randint(0, 5) for _ in range(rng.randint(3, 13))]]


RECTANGLE = '''def maximum_large_empty_rectangle_area(x_coord,y_coord):
    columns={}
    for x,y in zip(x_coord,y_coord):columns.setdefault(x,[]).append(y)
    ordered_y=sorted(set(y_coord));indices={value:index for index,value in enumerate(ordered_y)}
    size=1
    while size<len(ordered_y):size*=2
    tree=[-1]*(2*size)
    def update(position,value):
        position+=size;tree[position]=value;position//=2
        while position:
            tree[position]=max(tree[2*position],tree[2*position+1]);position//=2
    def query(left,right):
        left+=size;right+=size;answer=-1
        while left<=right:
            if left%2:answer=max(answer,tree[left]);left+=1
            if not right%2:answer=max(answer,tree[right]);right-=1
            left//=2;right//=2
        return answer
    last={};pair_last={};answer=-1
    for x in sorted(columns):
        values=sorted(columns[x])
        for low,high in zip(values,values[1:]):
            left=last.get(low,-1)
            if left>=0 and last.get(high)==left and pair_last.get((low,high))==left and query(indices[low],indices[high])==left:
                answer=max(answer,(x-left)*(high-low))
        for y in values:last[y]=x;update(indices[y],x)
        for low,high in zip(values,values[1:]):pair_last[(low,high)]=x
    return answer
'''

RUNES = '''def minimum_runes_to_add(n,crystals,flow_from,flow_to):
    graph=[[] for _ in range(n)];reverse=[[] for _ in range(n)]
    for left,right in zip(flow_from,flow_to):graph[left].append(right);reverse[right].append(left)
    powered=set(crystals);stack=list(crystals)
    while stack:
        node=stack.pop()
        for neighbor in graph[node]:
            if neighbor not in powered:powered.add(neighbor);stack.append(neighbor)
    unavailable=set(range(n))-powered;seen=set();order=[]
    for start in unavailable:
        if start in seen:continue
        seen.add(start);stack=[(start,0)]
        while stack:
            node,index=stack[-1]
            if index<len(graph[node]):
                neighbor=graph[node][index];stack[-1]=(node,index+1)
                if neighbor in unavailable and neighbor not in seen:seen.add(neighbor);stack.append((neighbor,0))
            else:order.append(node);stack.pop()
    component={};count=0
    for start in reversed(order):
        if start in component:continue
        component[start]=count;stack=[start]
        while stack:
            node=stack.pop()
            for neighbor in reverse[node]:
                if neighbor in unavailable and neighbor not in component:component[neighbor]=count;stack.append(neighbor)
        count+=1
    indegree=[0]*count
    for left,right in zip(flow_from,flow_to):
        if left in unavailable and right in unavailable and component[left]!=component[right]:indegree[component[right]]+=1
    return sum(value==0 for value in indegree)
'''

LOCKS = '''def minimum_lock_assignment_time(strength):
    n=len(strength);u=[0]*(n+1);v=[0]*(n+1);matched=[0]*(n+1);way=[0]*(n+1)
    for row in range(1,n+1):
        matched[0]=row;column=0;minimum=[10**30]*(n+1);used=[False]*(n+1)
        while True:
            used[column]=True;current=matched[column];delta=10**30;next_column=0
            for candidate in range(1,n+1):
                if not used[candidate]:
                    cost=(strength[current-1]+candidate-1)//candidate-u[current]-v[candidate]
                    if cost<minimum[candidate]:minimum[candidate]=cost;way[candidate]=column
                    if minimum[candidate]<delta:delta=minimum[candidate];next_column=candidate
            for candidate in range(n+1):
                if used[candidate]:u[matched[candidate]]+=delta;v[candidate]-=delta
                else:minimum[candidate]-=delta
            column=next_column
            if matched[column]==0:break
        while True:
            previous=way[column];matched[column]=matched[previous];column=previous
            if column==0:break
    return -v[0]
'''

CONVERSION = '''def maximum_two_day_currency(initial_currency,pairs1,rates1,pairs2,rates2):
    def values(pairs,rates):
        graph={}
        for (left,right),rate in zip(pairs,rates):
            graph.setdefault(left,[]).append((right,rate));graph.setdefault(right,[]).append((left,1.0/rate))
        result={initial_currency:1.0};stack=[initial_currency]
        while stack:
            currency=stack.pop()
            for neighbor,rate in graph.get(currency,[]):
                if neighbor not in result:result[neighbor]=result[currency]*rate;stack.append(neighbor)
        return result
    first=values(pairs1,rates1);second=values(pairs2,rates2)
    return max((amount/second[currency] for currency,amount in first.items() if currency in second),default=1.0)
'''

SPLITS = '''def count_beautiful_splits(nums):
    def z_values(values):
        z=[0]*len(values);left=right=0
        for index in range(1,len(values)):
            if index<=right:z[index]=min(right-index+1,z[index-left])
            while index+z[index]<len(values) and values[z[index]]==values[index+z[index]]:z[index]+=1
            if index+z[index]-1>right:left,right=index,index+z[index]-1
        return z
    n=len(nums);whole=z_values(nums);answer=0
    for first in range(1,n-1):
        suffix=z_values(nums[first:])
        for second in range(first+1,n):
            one=first<=second-first and whole[first]>=first
            length=second-first;two=length<=n-second and suffix[length]>=length
            answer+=one or two
    return answer
'''


def lesson(a,b,c,d): return [a,b,c,d]


RECT_CASES=[[xs,ys] for xs,ys in [
    ([1,1,3,3],[1,3,1,3]),([1,1,3,3,2],[1,3,1,3,2]),([0],[0]),
    ([0,0,2],[0,2,0]),([0,0,2,2],[0,2,0,2]),([0,0,3,3,0],[0,3,0,3,1]),
    ([0,0,3,3,1],[0,3,0,3,0]),([0,0,2,2,4,4],[0,2,0,2,0,2]),
    ([1,1,4,4,8],[2,5,2,5,9]),([0,0,5,5,2],[0,4,0,4,2]),
    ([2,2,7,7,9,9],[1,6,1,6,1,6]),([0,0,1,1,2,2],[0,2,0,2,0,2]),
    ([3,3,10,10,5],[4,9,4,9,10]),([0,0,4,4,2,2],[0,4,0,4,0,4])]]
RUNE_CASES=[[n,c,a,b] for n,c,a,b in [
    (6,[0],[0,1,2,3],[1,2,3,0]),(2,[0],[0],[1]),(2,[0],[1],[0]),
    (3,[0],[1],[2]),(3,[0],[0,1],[1,2]),(4,[0],[1,2,3],[2,3,1]),
    (5,[0],[1,2,3,4],[2,1,4,3]),(5,[0],[0,2,3],[1,3,4]),
    (6,[0,5],[1,2,3,4],[2,1,4,3]),(4,[0],[0,2],[1,3]),
    (7,[0],[1,2,3,4,5,6],[2,1,4,3,6,5]),(5,[0,1],[2,3],[3,4]),
    (3,[0,1,2],[0],[1]),(6,[0],[0,1,3,4],[1,2,4,5])]]
LOCK_CASES=[[[v for v in values]] for values in [
    [3,4,1],[1],[10],[1,1],[2,5,4],[10,10],[2,3],[5,9,2],[7,3,12,1],
    [100,1,50],[4,8,12,16],[9,2,6],[20,19,18,1],[6,6,6,6,6]]]
CONVERSION_CASES=[
    ['EUR',[['EUR','USD'],['USD','JPY']],[2.0,3.0],[['JPY','USD'],['USD','CHF'],['CHF','EUR']],[4.0,5.0,6.0]],
    ['A',[['A','B']],[2.0],[['A','B']],[2.0]],
    ['A',[['A','B']],[3.0],[['A','B']],[2.0]],
    ['USD',[['USD','EUR']],[2.0],[['EUR','USD']],[4.0]],
    ['A',[['A','B'],['B','C']],[2.0,3.0],[['A','C']],[2.0]],
    ['A',[['B','C']],[3.0],[['A','B']],[2.0]],
    ['A',[['A','B'],['A','C']],[2.0,4.0],[['A','B'],['A','C']],[4.0,2.0]],
    ['X',[['X','Y'],['Y','Z']],[5.0,2.0],[['X','Y'],['Y','Z']],[2.0,5.0]],
    ['A',[['A','B'],['B','C'],['C','D']],[2.0,2.0,2.0],[['A','D']],[1.0]],
    ['A',[['A','B']],[1.0],[['A','C']],[3.0]],
    ['A',[['A','B'],['B','C']],[1.5,2.0],[['A','C']],[1.5]],
    ['Q',[['Q','R'],['R','S']],[3.0,4.0],[['Q','S'],['S','R']],[2.0,2.0]],
    ['A',[['A','B'],['B','C']],[6.0,6.0],[['A','B'],['B','C']],[1.0,1.0]],
    ['M',[['M','N']],[2.5],[['M','N']],[5.0]]]
SPLIT_CASES=[[[v for v in values]] for values in [
    [1,1,2,1],[1,1,1],[1,2,3],[1,1,1,1],[1,2,1,2],[0,0,0,0,0],
    [1,2,1,2,1,2],[1,1,2,2,2],[3,3,3,4,3],[1,2,3,1,2,3],
    [5,4,5,4,5],[0,1,0,1,2,0,1],[2,2,3,2,2,3],[1,2,1,2,1,2,1]]]


BATCH={
3382:entry('maximum_large_empty_rectangle_area',[('x_coord','list[int]'),('y_coord','list[int]')],'int',['geometry','segment trees','sweep line'],['x_coord and y_coord describe up to 200,000 unique points with coordinates in 0..80,000,000.','A valid positive-area axis-aligned rectangle uses four points as corners and has no other point inside or on its border.','Return its largest area, or -1.'],[([[1,1,3,3],[1,3,1,3]],'The four points form an empty two-by-two rectangle with area four.'),([[1,1,3,3,2],[1,3,1,3,2]],'The center point invalidates the only rectangle, so return -1.')],RECT_CASES,RECTANGLE,[RECTANGLE.replace('pair_last.get((low,high))==left','True'),RECTANGLE.replace('and query(indices[low],indices[high])==left','and True')],['Ignores extra points on the earlier vertical border.','Ignores points inside the rectangle between its two boundary columns.'],rectangle_oracle,random_rectangle,lesson('A valid rectangle uses adjacent y-pairs in both boundary columns.','Sweep columns while a range-maximum tree records the latest x seen at every y.','For each adjacent pair, require the same prior adjacent pair and no later x anywhere across its closed y-range.','These checks exclude all four borders and the interior; every empty rectangle is discovered at its right boundary.'),'O(p log p)','O(p)',8),
3383:entry('minimum_runes_to_add',[('n','int'),('crystals','list[int]'),('flow_from','list[int]'),('flow_to','list[int]')],'int',['graphs','strongly connected components','depth-first search'],['2 <= n <= 100,000; crystals is nonempty; flow arrays describe up to 200,000 distinct directed edges.','A crystal powers every node reachable along existing directed runes.','Add the fewest directed runes so every node becomes powered.'],[([6,[0],[0,1,2,3],[1,2,3,0]],'The four-node cycle is powered; the two isolated points each need one new incoming rune.'),([4,[0],[0,1,2],[1,2,3]],'The existing chain carries power from the crystal to every focus point, so no rune is added.')],RUNE_CASES,RUNES,[RUNES.replace('return sum(value==0 for value in indegree)','return count'),RUNES.replace('unavailable=set(range(n))-powered','unavailable=set(range(n))')],['Counts every unreachable SCC instead of only source SCCs.','Ignores reachability already supplied by crystals.'],runes_oracle,random_runes,lesson('Contract each unreachable strongly connected component; one entry powers its entire component.','Only zero-indegree components in the unreachable condensation need new incoming runes.','Mark crystal reachability, compute SCCs on the remainder, count condensation components with no incoming edge.','Every source component needs an external entry, and one rune into each source reaches all downstream components.'),'O(n+e)','O(n+e)',8),
3385:entry('minimum_lock_assignment_time',[('strength','list[int]')],'int',['arrays','assignment','minimum cost matching'],['strength has 1–80 positive values up to one million.','The sword factor starts at one and increases by one after every broken lock; energy resets after each lock.','Assign locks to factor positions to minimize the sum of ceiling(strength/factor).'],[([[3,4,1]],'An optimal order breaks the locks in four total minutes.'),([[2,5,4]],'Assigning locks to factors one, two, and three optimally takes five minutes.')],LOCK_CASES,LOCKS,["""def minimum_lock_assignment_time(strength):
    return sum((value+position)//(position+1) for position,value in enumerate(sorted(strength)))
""","""def minimum_lock_assignment_time(strength):
    return sum((value+position)//(position+1) for position,value in enumerate(sorted(strength,reverse=True)))
"""],['Greedily assigns the weakest locks to the smallest factors.','Greedily assigns the strongest locks to the smallest factors; ceiling effects can make this suboptimal.'],locks_oracle,random_locks,lesson('Each lock must be matched to one distinct factor position.','Build the complete lock-position cost matrix and solve minimum-cost bipartite assignment.','Use the Hungarian augmenting procedure on costs ceil(strength[i]/position).','Perfect matchings correspond exactly to lock orders, so the minimum assignment cost is the minimum escape time.'),'O(n³)','O(n²)',8),
3387:entry('maximum_two_day_currency',[('initial_currency','str'),('pairs1','list[list[str]]'),('rates1','list[float]'),('pairs2','list[list[str]]'),('rates2','list[float]')],'float',['graphs','depth-first search','math'],['Each day has 1–10 consistent currency pairs with positive rates and reciprocal reverse conversions.','Start day one with one unit of initial_currency; carry one resulting currency into day two and finish in the initial currency.','Use any number of conversions per day and return the maximum final amount.'],[(['EUR',[['EUR','USD'],['USD','JPY']],[2.0,3.0],[['JPY','USD'],['USD','CHF'],['CHF','EUR']],[4.0,5.0,6.0]],'Six JPY after day one converts through day two at 120 EUR per JPY, yielding 720.'),(['A',[['A','B']],[2.0],[['A','B']],[2.0]],'The same rate both days offers no gain, so retain one unit.')],CONVERSION_CASES,CONVERSION,[CONVERSION.replace('amount/second[currency]','amount*second[currency]'),CONVERSION.replace("return max((amount/second[currency] for currency,amount in first.items() if currency in second),default=1.0)", 'return 1.0')],['Uses the day-two initial-to-currency rate instead of its reciprocal.','Never considers carrying a converted currency between days.'],conversion_oracle,random_conversion,lesson('Consistent conversion graphs assign one relative value to every currency reachable from the initial currency.','Compute initial-to-currency ratios for each day, then combine day one forward with day two backward.','Traverse both graphs with reciprocal edges; maximize day1[currency]/day2[currency] over common currencies.','Any same-day path has the stored consistent ratio, and every two-day plan is determined by its overnight currency.'),'O(pairs1+pairs2)','O(currencies)',5),
3388:entry('count_beautiful_splits',[('nums','list[int]')],'int',['arrays','string matching','dynamic programming'],['nums has 3–5,000 values in 0..50.','Split it into three nonempty consecutive parts.','Count splits where the first part prefixes the second or the second prefixes the third.'],[([[1,1,2,1]],'The two valid cut pairs satisfy one of the required prefix relationships.'),([[1,1,1]],'The only split has all singleton parts, so both prefix conditions hold and it counts once.')],SPLIT_CASES,SPLITS,[SPLITS.replace('answer+=one or two','answer+=one + two'),SPLITS.replace('length<=n-second','length<n-second')],['Double-counts splits satisfying both prefix conditions.','Rejects a second and third part of equal length even when identical.'],splits_oracle,random_splits,lesson('Both conditions are longest-common-prefix queries between fixed suffix starts.','Use Z-values for the whole array and separately for each suffix while retaining only linear memory.','Enumerate both cuts; test prefix lengths from the appropriate Z arrays and add their logical union.','Z-values give exact matching-prefix lengths, and every ordered pair of nonempty cuts is examined once.'),'O(n²)','O(n)',6),
}
BATCH[3387]['comparator']='float'
