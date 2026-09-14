"""Third reviewed group of workbook batch 108."""
from .import_batch_055 import entry
def room_o(a):
 rooms,queries=a;answer=[]
 for preferred,minimum in queries:
  eligible=[room for room,size in rooms if size>=minimum];answer.append(min(eligible,key=lambda room:(abs(room-preferred),room)) if eligible else -1)
 return answer
def interval_o(a):
 intervals,queries=a;return [min((right-left+1 for left,right in intervals if left<=query<=right),default=-1) for query in queries]
def distinct_o(a):
 nums,k=a;return [len(set(nums[index:index+k])) for index in range(len(nums)-k+1)]
def population_o(a):
 logs=a[0];years=range(min(birth for birth,_ in logs),max(death for _,death in logs));return max(years,key=lambda year:(sum(birth<=year<death for birth,death in logs),-year))
def distance_o(a):
 first,second=a;return max((right-left for left in range(len(first)) for right in range(left,len(second)) if first[left]<=second[right]),default=0)
def rroom(r):
 count=r.randint(1,10);ids=r.sample(range(1,40),count);return [[[room,r.randint(1,20)] for room in ids],[[r.randint(1,40),r.randint(1,22)] for _ in range(r.randint(1,10))]]
def rinterval(r):
 intervals=[]
 for _ in range(r.randint(1,10)):
  left=r.randint(0,20);intervals.append([left,r.randint(left,left+15)])
 return [intervals,[r.randint(0,35) for _ in range(r.randint(1,10))]]
def rdistinct(r):
 nums=[r.randint(-5,5) for _ in range(r.randint(1,20))];return [nums,r.randint(1,len(nums))]
def rpopulation(r):
 logs=[]
 for _ in range(r.randint(1,12)):
  birth=r.randint(1950,2049);logs.append([birth,r.randint(birth+1,2050)])
 return [logs]
def rdistance(r):
 first=sorted([r.randint(0,30) for _ in range(r.randint(1,12))],reverse=True);second=sorted([r.randint(0,30) for _ in range(r.randint(len(first),15))],reverse=True);return [first,second]
ROOM='''def closest_eligible_rooms(rooms, queries):
 from bisect import bisect_left,bisect_right
 room_ids=sorted(room for room,_ in rooms);positions={room:index+1 for index,room in enumerate(room_ids)};tree=[0]*(len(room_ids)+1);active=0
 def add(index):
  while index<len(tree):tree[index]+=1;index+=index&-index
 def prefix(index):
  total=0
  while index:total+=tree[index];index-=index&-index
  return total
 def kth(order):
  index=0;step=1<<(len(tree).bit_length()-1)
  while step:
   nxt=index+step
   if nxt<len(tree) and tree[nxt]<order:index=nxt;order-=tree[nxt]
   step//=2
  return room_ids[index]
 ordered_rooms=sorted(rooms,key=lambda item:-item[1]);order=sorted(range(len(queries)),key=lambda i:-queries[i][1]);answer=[-1]*len(queries);cursor=0
 for query_index in order:
  preferred,minimum=queries[query_index]
  while cursor<len(ordered_rooms) and ordered_rooms[cursor][1]>=minimum:add(positions[ordered_rooms[cursor][0]]);active+=1;cursor+=1
  if not active:continue
  before=prefix(bisect_left(room_ids,preferred));through=prefix(bisect_right(room_ids,preferred));candidates=[]
  if before:candidates.append(kth(before))
  if through<active:candidates.append(kth(through+1))
  if through>before:candidates.append(preferred)
  answer[query_index]=min(candidates,key=lambda room:(abs(room-preferred),room))
 return answer
'''
INTERVAL='''def minimum_covering_intervals(intervals, queries):
 import heapq
 ordered=sorted(intervals);indexed=sorted((query,index) for index,query in enumerate(queries));heap=[];answer=[-1]*len(queries);cursor=0
 for query,index in indexed:
  while cursor<len(ordered) and ordered[cursor][0]<=query:
   left,right=ordered[cursor];heapq.heappush(heap,(right-left+1,right));cursor+=1
  while heap and heap[0][1]<query:heapq.heappop(heap)
  if heap:answer[index]=heap[0][0]
 return answer
'''
DISTINCT='''def distinct_counts_in_windows(nums, k):
 counts={};answer=[]
 for index,value in enumerate(nums):
  counts[value]=counts.get(value,0)+1
  if index>=k:
   old=nums[index-k];counts[old]-=1
   if counts[old]==0:del counts[old]
  if index>=k-1:answer.append(len(counts))
 return answer
'''
POPULATION='''def earliest_maximum_population_year(logs):
 changes=[0]*101
 for birth,death in logs:changes[birth-1950]+=1;changes[death-1950]-=1
 population=best=0;answer=1950
 for offset,change in enumerate(changes):
  population+=change
  if population>best:best=population;answer=1950+offset
 return answer
'''
DISTANCE='''def maximum_valid_pair_distance(nums1, nums2):
 left=0;answer=0
 for right,value in enumerate(nums2):
  while left<len(nums1) and nums1[left]>value:left+=1
  if left<len(nums1) and left<=right:answer=max(answer,right-left)
 return answer
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1847:E('closest_eligible_rooms',[('rooms','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['arrays','binary-search','sorting','fenwick-trees'],['Room IDs are unique; each query is [preferred_id,minimum_size].','Choose an eligible room minimizing absolute ID difference, breaking ties by smaller ID; return -1 if none.'],[([[[2,2],[1,2],[3,2]],[[3,1],[3,3],[5,2]]],'The answers are room three, no room, and room three.'),([[[1,4],[2,3],[3,5]],[[2,4],[2,6]]],'Rooms one and three tie for the first query, so smaller room one wins; the second has no eligible room.')],[[*x] for x in [([[1,1]],[[1,1]]),([[1,1]],[[2,2]]),([[2,2],[1,2],[3,2]],[[3,1],[3,3],[5,2]]),([[1,4],[2,3],[3,5]],[[2,4],[2,6]]),([[10,5],[20,5]],[[15,5]]),([[1,10],[100,1]],[[50,2]]),([[4,3],[8,7],[12,5]],[[9,5]]),([[5,2],[7,4]],[[6,3]]),([[2,9],[9,2],[6,6]],[[7,6],[1,10]]),([[3,1],[1,3]],[[2,1]]),([[20,20]],[[1,1],[30,21]]),([[1,2],[4,2],[7,2]],[[5,2]]),([[8,3],[2,9]],[[7,3]]),([[11,4],[15,4]],[[13,4]])]],ROOM,[ROOM.replace('key=lambda room:(abs(room-preferred),room)','key=lambda room:(abs(room-preferred),-room)'),ROOM.replace('>=minimum','>minimum')],['Breaks equal-distance ties toward the larger room ID.', 'Rejects rooms whose size exactly equals the requirement.'],room_o,rroom,H('Process queries from largest minimum size downward and activate rooms as they become eligible.','Coordinate-compress room IDs and store active positions in a Fenwick tree.','For each preferred ID, obtain the active predecessor and successor by prefix counts and order-statistic lookup.','Only the nearest active ID on each side can win; offline activation enforces size eligibility and the final tuple comparison enforces distance and tie rules.'),'O((rooms+queries) log rooms)','O(rooms+queries)',8),
1851:E('minimum_covering_intervals',[('intervals','list[list[int]]'),('queries','list[int]')],'list[int]',['arrays','sorting','heaps','sweep-line'],['Intervals and containment are inclusive; interval size is right-left+1.','For each query return the smallest containing interval size, or -1 if none.'],[([[[1,4],[2,4],[3,6],[4,4]],[2,3,4,5]],'The minimum sizes are three, three, one, and four.'),([[[2,3],[2,5],[1,8],[20,25]],[2,19,5,22]],'The queries receive sizes two, -1, four, and six.')],[[*x] for x in [([[1,1]],[1]),([[1,1]],[2]),([[1,4],[2,4],[3,6],[4,4]],[2,3,4,5]),([[2,3],[2,5],[1,8],[20,25]],[2,19,5,22]),([[0,10],[5,5]],[5]),([[3,7]],[3,7]),([[1,2],[4,5]],[3]),([[1,100],[20,30]],[25]),([[5,9],[1,6]],[6]),([[2,2],[2,3]],[2]),([[10,20],[15,15]],[15]),([[1,3],[2,2]],[1,2,3]),([[0,0],[0,5]],[0]),([[7,8],[8,9]],[8])]],INTERVAL,[INTERVAL.replace('right-left+1','right-left'),INTERVAL.replace('ordered[cursor][0]<=query','ordered[cursor][0]<query')],['Uses endpoint difference instead of inclusive interval size.', 'Excludes intervals beginning exactly at the query.'],interval_o,rinterval,H('Sweep queries from left to right while adding intervals that have begun.','Use a heap ordered by interval size and discard heap tops that ended before the query.','The remaining heap top is the smallest active containing interval.','Every interval is inserted once when its left endpoint becomes eligible; expired intervals cannot answer later queries, so the heap minimum is exactly optimal.'),'O((intervals+queries) log intervals)','O(intervals+queries)',8),
1852:E('distinct_counts_in_windows',[('nums','list[int]'),('k','int')],'list[int]',['arrays','hash-maps','sliding-window'],['k is between one and nums length.','Return the number of distinct values in every contiguous window of length k.'],[([[1,2,3,2,2,1,3],3],'The five windows contain 3,2,2,2,3 distinct values.'),([[1,1,1,1],2],'Every length-two window contains only value one.')],[[*x] for x in [([1],1),([1,2],1),([1,2],2),([1,2,3,2,2,1,3],3),([1,1,1,1],2),([1,2,1,3],2),([1,2,3],3),([3,2,1],1),([0,0,1],2),([-1,1,-1],2),([5,4,5,4,3],3),([2,2,3,3],4),([1,2,2,1],3),([9,8,7,9],2)]],DISTINCT,[DISTINCT.replace('index>=k','index>k'),DISTINCT.replace('if counts[old]==0','if counts[old]<0')],['Removes the outgoing value one step late.', 'Keeps zero-count values in the distinct map.'],distinct_o,rdistinct,H('Maintain counts for exactly the current window.', 'Add the incoming value and remove the value k positions behind.', 'Delete a key when its count reaches zero; append the map size after the first full window.', 'The map contains precisely values with positive multiplicity in each window, so its size is the required distinct count.'),'O(n)','O(k)',5),
1854:E('earliest_maximum_population_year',[('logs','list[list[int]]')],'int',['arrays','prefix-sums','counting'],['A person contributes in every year from birth inclusive to death exclusive.','Return the earliest year attaining maximum population.'],[([[[1993,1999],[2000,2010]]],'The population is one in several years, and earliest 1993 wins.'),([[[1950,1961],[1960,1971],[1970,1981]]],'The first overlap peak occurs in 1960.')],[[x] for x in [[[1993,1999],[2000,2010]],[[1950,1961],[1960,1971],[1970,1981]],[[1950,1951]],[[2000,2050]],[[1990,2000],[1990,2000]],[[1950,2000],[1960,1970]],[[2000,2001],[2001,2002]],[[1980,1990],[1985,1995]],[[2049,2050]],[[1950,2050]],[[1970,1980],[1980,1990]],[[1965,1975],[1970,1980],[1975,1985]],[[1999,2002],[2000,2001]],[[1955,1960],[1956,1959]]]],POPULATION,[POPULATION.replace('changes[death-1950]-=1','changes[death-1950+1]-=1'),POPULATION.replace('population>best','population>=best')],['Counts people during their death year.', 'Replaces an earlier tied year with a later one.'],population_o,rpopulation,H('Birth adds one starting that year; death removes one starting that year.', 'Store those changes and scan their prefix sum.', 'Update the answer only when population strictly exceeds the previous maximum.', 'The prefix sum equals each year’s active half-open intervals, and strict improvement preserves the earliest year on ties.'),'O(logs+years)','O(years)',3),
1855:E('maximum_valid_pair_distance',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','two-pointers','binary-search'],['Both arrays are non-increasing.','A valid pair has i<=j and nums1[i]<=nums2[j]; maximize j-i, returning zero if no positive distance exists.'],[([[55,30,5,4,2],[100,20,10,10,5]],'Pair i=2,j=4 has distance two, which is maximum.'),([[2,2,2],[10,10,1]],'The farthest valid pair uses i=0,j=1 for distance one.')],[[*x] for x in [([1],[1]),([2],[1]),([55,30,5,4,2],[100,20,10,10,5]),([2,2,2],[10,10,1]),([30,29,19,5],[25,25,25,25,25]),([5,4],[6,5,4]),([10,9],[8,7]),([3,3,3],[3,3,3]),([9,7,5],[10,8,6,4]),([1,1],[2,2,2]),([8,4,2],[9,3,2]),([100,1],[100,100]),([6,5,4],[7,6,5,4]),([4,2],[3,3,3])]],DISTANCE,[DISTANCE.replace('nums1[left]>value','nums1[left]>=value'),DISTANCE.replace('right-left','left-right')],['Rejects equal values even though the inequality is inclusive.', 'Computes the distance with reversed subtraction.'],distance_o,rdistance,H('Monotonic order makes the smallest viable nums1 index move only forward.', 'Sweep nums2 by j while advancing i until nums1[i]<=nums2[j].','When i<=j, update the answer with j-i.', 'Once nums1[i] is too large for a decreasing nums2 value it remains unusable later; the earliest viable i gives the largest distance for each j.'),'O(n+m)','O(1)',5),
}
