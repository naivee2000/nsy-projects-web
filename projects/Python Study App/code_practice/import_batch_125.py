"""First slice of workbook batch 125."""

from .import_batch_055 import entry


def intersection_oracle(args):
    rows = args[0]
    return sorted(value for value in rows[0] if all(value in row for row in rows[1:]))


def random_intersection(rng):
    return [[rng.sample(range(1, 25), rng.randint(1, 10)) for _ in range(rng.randint(1, 7))]]


def lattice_oracle(args):
    circles = args[0]
    minimum = min(x - radius for x, _, radius in circles), min(y - radius for _, y, radius in circles)
    maximum = max(x + radius for x, _, radius in circles), max(y + radius for _, y, radius in circles)
    return sum(any((x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2 for cx, cy, radius in circles)
               for x in range(minimum[0], maximum[0] + 1) for y in range(minimum[1], maximum[1] + 1))


def random_lattice(rng):
    return [[[rng.randint(0, 12), rng.randint(0, 12), rng.randint(1, 5)] for _ in range(rng.randint(1, 5))]]


def rectangles_oracle(args):
    rectangles, points = args
    return [sum(width >= x and height >= y for width, height in rectangles) for x, y in points]


def random_rectangles(rng):
    return [[[rng.randint(1, 20), rng.randint(1, 20)] for _ in range(rng.randint(1, 12))],
            [[rng.randint(1, 20), rng.randint(1, 20)] for _ in range(rng.randint(1, 10))]]


def flowers_oracle(args):
    flowers, people = args
    return [sum(start <= person <= end for start, end in flowers) for person in people]


def random_flowers(rng):
    flowers = []
    for _ in range(rng.randint(1, 15)):
        start = rng.randint(1, 30)
        flowers.append([start, rng.randint(start, 40)])
    return [flowers, [rng.randint(1, 40) for _ in range(rng.randint(1, 12))]]


def prefixes_oracle(args):
    words, text = args
    return sum(text[:len(word)] == word for word in words)


def random_prefixes(rng):
    return [["".join(rng.choice("abc") for _ in range(rng.randint(1, 7))) for _ in range(rng.randint(1, 15))],
            "".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))]


INTERSECTION = '''\
def intersection_of_all_arrays(nums):
    common=set(nums[0])
    for row in nums[1:]:common.intersection_update(row)
    return sorted(common)
'''

LATTICE = '''\
def count_lattice_points_in_circles(circles):
    points=set()
    for center_x,center_y,radius in circles:
        for x in range(center_x-radius,center_x+radius+1):
            for y in range(center_y-radius,center_y+radius+1):
                if (x-center_x)**2+(y-center_y)**2<=radius**2:points.add((x,y))
    return len(points)
'''

RECTANGLES = '''\
def rectangles_containing_points(rectangles,points):
    from bisect import bisect_left
    by_height=[[] for _ in range(101)]
    for width,height in rectangles:by_height[height].append(width)
    for widths in by_height:widths.sort()
    answer=[]
    for x,y in points:
        answer.append(sum(len(by_height[height])-bisect_left(by_height[height],x) for height in range(y,101)))
    return answer
'''

FLOWERS = '''\
def flowers_in_bloom(flowers,people):
    from bisect import bisect_left,bisect_right
    starts=sorted(start for start,_ in flowers);ends=sorted(end for _,end in flowers)
    return [bisect_right(starts,time)-bisect_left(ends,time) for time in people]
'''

PREFIXES = '''\
def count_word_prefixes(words,s):
    return sum(s.startswith(word) for word in words)
'''


BATCH = {
    2248: entry('intersection_of_all_arrays',[('nums','list[list[int]]')],'list[int]',['arrays','hash sets','sorting'],['Every inner array contains distinct positive integers.','Return values present in every inner array.','The result must be sorted in increasing order and contain no duplicates.'],[([[[3,1,2,4,5],[1,2,3,4],[3,4,5,6]]],'Only three and four occur in all three arrays.'),([[[1,2,3],[4,5,6]]],'The two arrays share no value, so return an empty list.')],[[x] for x in [[[1]],[[1],[1]],[[1],[2]],[[3,1,2,4,5],[1,2,3,4],[3,4,5,6]],[[1,2,3],[4,5,6]],[[1,2],[2,1]],[[5,4,3],[3,4],[4,3,2]],[[10,20,30],[20,30],[30,20,40]],[[1,2,3,4]],[[7,8],[8,9],[8,10]],[[1,5,9],[1,5],[1,2,5]],[[2,4,6],[1,2,3],[2,8]],[[100],[100,200],[50,100]],[[1,3,5],[2,4,6],[1,2]]]],INTERSECTION,[INTERSECTION.replace('intersection_update','update'),INTERSECTION.replace('sorted(common)','list(common)')],['Builds a union instead of retaining only common values.','Returns arbitrary set iteration order rather than required increasing order.'],intersection_oracle,random_intersection,['Start with the set of values in the first array.','Intersect it with each later array so only values seen everywhere remain.','Sort the final common set before returning it.','A value survives every intersection exactly when it belongs to every row; sorting satisfies the output contract.'],'O(total values + r log r)','O(distinct values)',3),
    2249: entry('count_lattice_points_in_circles',[('circles','list[list[int]]')],'int',['geometry','hash sets','enumeration'],['Each circle is [center_x,center_y,radius] with integer values and positive radius.','A lattice point has integer coordinates and counts when its squared distance is at most radius squared.','Points covered by multiple circles count only once.'],[([[[2,2,1]]],'The center and its four axis-adjacent points are inside the radius-one circle, giving five.'),([[[2,2,2],[3,4,1]]],'Enumerating both disks and deduplicating their overlap gives sixteen lattice points.')],[[c] for c in [[[0,0,1]],[[2,2,1]],[[2,2,2],[3,4,1]],[[1,1,2]],[[5,5,1],[5,5,1]],[[0,0,2]],[[3,1,1],[1,3,1]],[[10,10,3]],[[1,1,1],[3,1,1]],[[2,3,2],[4,3,2]],[[0,5,1]],[[6,0,2]],[[4,4,1],[4,6,1],[6,4,1]],[[8,8,4]]]],LATTICE,[LATTICE.replace('<=radius**2','<radius**2'),LATTICE.replace('points.add((x,y))','points.add((x-center_x,y-center_y))')],['Excludes lattice points lying exactly on a circle boundary.','Stores coordinates relative to each center, merging unrelated absolute points across circles.'],lattice_oracle,random_lattice,['Enumerate the integer bounding square of each circle.','Use squared distance to test inclusion without floating-point arithmetic, and insert accepted coordinates into a set.','For each x and y from center-radius through center+radius, add the point when dx²+dy²<=r².','The bounding square contains every possible covered lattice point, the inequality is exact, and the set deduplicates overlaps.'],'O(sum radius^2)','O(unique covered points)',5),
    2250: entry('rectangles_containing_points',[('rectangles','list[list[int]]'),('points','list[list[int]]')],'list[int]',['arrays','binary search','sorting'],['Each rectangle [width,height] spans from the origin through those inclusive coordinates.','A rectangle contains [x,y] exactly when width>=x and height>=y.','Return one count per query point in the original point order.'],[([[[1,2],[2,3],[2,5]],[[2,1],[1,4]]],'Two rectangles contain point [2,1], while only the height-five rectangle contains [1,4].'),([[[1,1],[2,2],[3,3]],[[1,3],[1,1]]],'One rectangle reaches height three, and all three contain [1,1].')],[[r,p] for r,p in [([[1,1]],[[1,1]]),([[1,1]],[[2,1]]),([[1,2],[2,3],[2,5]],[[2,1],[1,4]]),([[1,1],[2,2],[3,3]],[[1,3],[1,1]]),([[5,5]],[[5,5],[5,6],[6,5]]),([[2,1],[2,2]],[[2,1]]),([[10,1],[1,10]],[[1,1],[5,5]]),([[3,3],[3,4],[4,3]],[[3,3]]),([[100,100]],[[1,100]]),([[4,2],[6,2],[5,5]],[[5,2],[5,3]]),([[1,5],[2,4],[3,3]],[[2,4]]),([[8,8],[9,7]],[[8,7],[9,8]]),([[2,10],[10,2]],[[2,2]]),([[7,1],[7,2],[7,3]],[[7,2]])]],RECTANGLES,[RECTANGLES.replace('bisect_left','bisect_right'),RECTANGLES.replace('range(y,101)','range(y+1,101)')],['Requires width to be strictly greater than the point x-coordinate.','Requires rectangle height to be strictly greater and omits equality at y.'],rectangles_oracle,random_rectangles,['Group rectangle widths by their integer heights and sort each group.','For a point [x,y], only height buckets y and above qualify; binary-search the first width at least x in each.','Sum len(bucket)-bisect_left(bucket,x) for all qualifying heights.','The height loop enforces height>=y and the binary-search suffix enforces width>=x, so every containing rectangle is counted once.'],'O(R log R + P*H log R)','O(R+H)',6),
    2251: entry('flowers_in_bloom',[('flowers','list[list[int]]'),('people','list[int]')],'list[int]',['arrays','binary search','sorting'],['Each bloom interval [start,end] is inclusive at both endpoints.','For each arrival time, count intervals satisfying start<=time<=end.','Return counts in the same order as the people input, including repeated arrival times.'],[([[[1,6],[3,7],[9,12],[4,13]],[2,3,7,11]],'The four arrival times see one, two, two, and two flowers respectively.'),([[[1,10],[3,3]],[3,3,11]],'At time three both flowers bloom, while time eleven sees none.')],[[f,p] for f,p in [([[1,1]],[1]),([[1,1]],[0,2]),([[1,6],[3,7],[9,12],[4,13]],[2,3,7,11]),([[1,10],[3,3]],[3,3,11]),([[5,5],[5,6]],[5,6]),([[1,2],[2,3]],[2]),([[10,20]],[1,10,20,21]),([[1,100],[50,60]],[49,50,60,61]),([[2,4],[2,4],[2,4]],[2,3,4]),([[1,3],[5,7]],[4,5]),([[3,9],[1,3],[9,12]],[3,9]),([[1,5],[2,6],[3,7]],[1,4,7]),([[8,8]],[8,8]),([[4,10],[6,6]],[6,10])]],FLOWERS,[FLOWERS.replace('bisect_left(ends,time)','bisect_right(ends,time)'),FLOWERS.replace('bisect_right(starts,time)','bisect_left(starts,time)')],['Subtracts flowers ending exactly at the arrival time even though endpoints are inclusive.','Omits flowers starting exactly at the arrival time.'],flowers_oracle,random_flowers,['At time t, blooming flowers equal those that have started minus those that ended before t.','Sort all starts and ends independently and use binary-search insertion positions.','Compute bisect_right(starts,t)-bisect_left(ends,t) for every arrival.','The first count includes starts at t, while the subtracted count excludes ends at t, exactly matching inclusive intervals.'],'O((F+P) log F)','O(F)',8),
    2255: entry('count_word_prefixes',[('words','list[str]'),('s','str')],'int',['arrays','strings'],['Count each word occurrence separately when it is a prefix of s.','A prefix must match from the first character and may equal the whole string.','All words and s are nonempty lowercase strings.'],[([['a','b','c','ab','bc','abc'],'abc'],'The prefixes a, ab, and abc match, so the count is three.'),([['a','a'],'a'],'Both occurrences of a count independently, giving two.')],[[w,s] for w,s in [(['a'],'a'),(['a'],'b'),(['a','b','c','ab','bc','abc'],'abc'),(['a','a'],'a'),(['abc'],'ab'),(['ab'],'abc'),(['abc'],'abc'),(['x','xy','xyz'],'xyzz'),(['cat','car','c'],'carpet'),(['b','ba'],'abc'),(['hello','he','h'],'hello'),(['z','zz'],'z'),(['abc','abcd','abce'],'abcdef'),(['one','on','o','two'],'one')]],PREFIXES,[PREFIXES.replace('s.startswith(word)','word.startswith(s)'),PREFIXES.replace('sum(','int(any(').replace(' for word in words)', ' for word in words))')],['Reverses the prefix relationship and tests whether each word starts with s.','Returns only whether any prefix exists instead of counting every matching occurrence.'],prefixes_oracle,random_prefixes,['Test each word independently against the beginning of s.','Python startswith implements the required anchored substring comparison.','Sum s.startswith(word) for every word in the list.','Each true predicate contributes one for exactly one listed occurrence, including duplicates and whole-string matches.'],'O(total word characters)','O(1)',3),
}

BATCH[2248]['wrong'][1] = INTERSECTION.replace('sorted(common)', 'sorted(common,reverse=True)')
BATCH[2248]['wrong_reasons'][1] = 'Sorts the common values in descending rather than required increasing order.'
