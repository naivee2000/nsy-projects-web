"""Replacement slots completing batch 100 after three candidates reached their repair limit."""
from collections import Counter

from .import_batch_055 import entry


def frequency_oracle(args):
    nums=args[0];counts=Counter(nums)
    return sorted(nums,key=lambda value:(counts[value],-value))


def width_oracle(args):
    xs=sorted({point[0] for point in args[0]})
    return max(right-left for left,right in zip(xs,xs[1:]))


def formation_oracle(args):
    arr,pieces=args
    def search(index,remaining):
        if index==len(arr):return not remaining
        for position,piece in enumerate(remaining):
            if arr[index:index+len(piece)]==piece and search(index+len(piece),remaining[:position]+remaining[position+1:]):return True
        return False
    return search(0,pieces)


def random_frequency(rng):return [[rng.randint(-10,10) for _ in range(rng.randint(1,30))]]
def random_width(rng):
    count=rng.randint(2,30);return [[[rng.randint(0,50),rng.randint(0,50)] for _ in range(count)]]
def random_formation(rng):
    size=rng.randint(1,9);arr=rng.sample(range(-20,21),size);cuts=sorted(rng.sample(range(1,size),rng.randint(0,size-1)))
    pieces=[];start=0
    for end in cuts+[size]:pieces.append(arr[start:end]);start=end
    rng.shuffle(pieces)
    if rng.random()<.3:pieces[rng.randrange(len(pieces))]=pieces[rng.randrange(len(pieces))][::-1]
    return [arr,pieces]


FREQUENCY='''def sort_by_increasing_frequency(nums):
 counts=Counter(nums)
 return sorted(nums,key=lambda value:(counts[value],-value))
'''
WIDTH='''def widest_empty_vertical_area(points):
 xs=sorted(point[0] for point in points)
 return max(right-left for left,right in zip(xs,xs[1:]))
'''
FORMATION='''def can_form_array_by_pieces(arr, pieces):
 by_first={piece[0]:piece for piece in pieces};index=0
 while index<len(arr):
  piece=by_first.get(arr[index])
  if piece is None or arr[index:index+len(piece)]!=piece:return False
  index+=len(piece)
 return True
'''


def lesson(a,b,c,d):return [a,b,c,d]
def E(*args):return entry(*args)


BATCH={
1636:E('sort_by_increasing_frequency',[('nums','list[int]')],'list[int]',['arrays','sorting'],['1–100 integers from -100 through 100.','Sort by increasing value frequency; for equal frequencies, sort values in decreasing numeric order.'],[([[1,1,2,2,2,3]],'Three occurs once, one twice, and two three times, so their groups appear in that frequency order.'),([[2,3,1,3,2]],'All values except one occur twice; the tied groups place three before two.')],[[x] for x in [[1,1,2,2,2,3],[2,3,1,3,2],[-1,1,-6,4,5,-6,1,4,1],[1],[1,2],[2,1],[1,1],[3,3,2,2],[0,-1,0,-1,2],[5,4,3,2,1],[1,2,2,3,3,3],[-2,-2,-1],[-3,-2,-1,-1,-2,-3],[0,0,0,1]]],FREQUENCY,[FREQUENCY.replace('(counts[value],-value)','(counts[value],value)'),FREQUENCY.replace('counts[value]','-counts[value]')],['Breaks equal-frequency ties by increasing rather than decreasing value.','Places the most frequent values first.'],frequency_oracle,random_frequency,lesson('Frequency is the primary key and negative value encodes the descending tie rule.','Count every value, then sort individual entries by (count,-value).','Build a Counter and use the two-part key for Python’s sort.','Equal values share a key and remain grouped; tuple ordering applies the exact primary and secondary rules.'),'O(n log n)','O(n)',3),
1637:E('widest_empty_vertical_area',[('points','list[list[int]]')],'int',['geometry','sorting'],['At least two points with integer coordinates; several points may share an x-coordinate.','Return the greatest difference between adjacent distinct sorted x-coordinates. Points on the two boundary lines are allowed.'],[([[[8,7],[9,9],[7,4],[9,7]]],'Distinct x-coordinates are seven, eight, and nine, so the widest empty strip has width one.'),([[[3,1],[9,0],[1,0],[1,4],[5,3],[8,8]]],'The largest adjacent x gap is from three to five, with width two.')],[[p] for p in [[[8,7],[9,9],[7,4],[9,7]],[[3,1],[9,0],[1,0],[1,4],[5,3],[8,8]],[[0,0],[1,1]],[[0,0],[100,1]],[[1,1],[1,2],[2,3]],[[5,0],[3,0],[4,0]],[[0,0],[2,0],[10,0]],[[7,1],[3,2],[9,3]],[[1,1],[4,4],[4,2],[8,8]],[[10,0],[0,0],[5,0]],[[2,9],[3,8],[20,7]],[[6,1],[6,2],[9,3],[12,4]],[[0,1],[50,2],[51,3]],[[4,4],[14,4],[9,4]]]],WIDTH,[WIDTH.replace('sorted(point[0] for point in points)','sorted(point[1] for point in points)'),WIDTH.replace('right-left','right-left-1')],['Sorts y-coordinates instead of x-coordinates.','Subtracts one as if width counted integer columns rather than geometric distance.'],width_oracle,random_width,lesson('Only horizontal positions matter because the open area extends infinitely vertically.','Sort all x-coordinates and inspect adjacent gaps.','Extract x, sort, and maximize each next minus previous value.','Any strip wider than an adjacent sorted gap would contain another x-coordinate; every adjacent gap has an empty interior.'),'O(n log n)','O(n)',3),
1640:E('can_form_array_by_pieces',[('arr','list[int]'),('pieces','list[list[int]]')],'bool',['arrays','hash-maps'],['arr contains unique integers; every integer across pieces is unique and pieces are nonempty.','Reorder whole pieces to form arr exactly; values inside a piece may not be reordered.'],[([[15,88],[[88],[15]]],'Place piece 15 before piece 88 to reproduce the target array.'),([[49,18,16],[[16,18,49]]],'The only piece has the reverse internal order, which cannot be changed.')],[[*x] for x in [([15,88],[[88],[15]]),([49,18,16],[[16,18,49]]),([85],[[85]]),([91,4,64,78],[[78],[4,64],[91]]),([1,2,3],[[1,2],[3]]),([1,2,3],[[1,3,2]]),([1,2,3],[[1],[3,2]]),([1,2],[[2],[1]]),([1,2,3,4],[[3,4],[1,2]]),([1,2,3,4],[[1,3],[2,4]]),([-1,0,1],[[0,1],[-1]]),([5,6,7],[[5],[6],[7]]),([10,20,30],[[20,30],[10]]),([4,3,2,1],[[4,3],[2,1]]),([8,6,7,5],[[8],[6,7],[5]])]],FORMATION,[FORMATION.replace("arr[index:index+len(piece)]!=piece","sorted(arr[index:index+len(piece)])!=sorted(piece)"),FORMATION.replace('index+=len(piece)','index+=1')],['Allows values inside each piece to be reordered.','Advances only one target position after consuming a multi-value piece.'],formation_oracle,random_formation,lesson('Unique first values identify the only piece that could begin at each target position.','Map each piece by its first value and consume arr from left to right.','Look up arr[index], compare the entire piece with the target slice, and advance by its length.','Uniqueness removes branching; exact slice comparison enforces the preserved internal order.'),'O(total values)','O(number of pieces)',3),
}
