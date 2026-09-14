"""First reviewed group of workbook batch 115."""
from collections import Counter,deque
from itertools import combinations
from .import_batch_055 import entry

def beauty_o(a):
 x=a[0];ans=0
 for i in range(1,len(x)-1):
  ans+=2 if max(x[:i])<x[i]<min(x[i+1:]) else int(x[i-1]<x[i]<x[i+1])
 return ans
def repeated_o(a):
 s,k=a;found={''}
 for length in range(1,len(s)//k+1):
  for ids in combinations(range(len(s)),length):
   t=''.join(s[i] for i in ids);target=t*k;at=0
   for c in s:
    if at<len(target) and c==target[at]:at+=1
   if at==len(target):found.add(t)
 return max(found,key=lambda t:(len(t),t))
def average_o(a):
 buildings=a[0];points=sorted({x for s,e,h in buildings for x in (s,e)});out=[]
 for left,right in zip(points,points[1:]):
  heights=[h for s,e,h in buildings if s<=left and right<=e]
  if not heights:continue
  avg=sum(heights)//len(heights)
  if out and out[-1][1]==left and out[-1][2]==avg:out[-1][1]=right
  else:out.append([left,right,avg])
 return out
def increase_o(a):
 x=a[0];return max((x[j]-x[i] for i in range(len(x)) for j in range(i+1,len(x)) if x[i]<x[j]),default=-1)
def grid_o(a):
 g=a[0];n=len(g[0]);answer=10**30
 for first_down in range(n):
  remaining=[g[0][:],g[1][:]]
  for c in range(first_down+1):remaining[0][c]=0
  for c in range(first_down,n):remaining[1][c]=0
  second=max(sum(remaining[0][:d+1])+sum(remaining[1][d:]) for d in range(n))
  answer=min(answer,second)
 return answer
def rbeauty(r):return [[r.randint(1,30) for _ in range(r.randint(3,30))]]
def rrepeated(r):
 k=r.randint(2,4);return [''.join(r.choice('abcd') for _ in range(r.randint(2,10))),k]
def raverage(r):
 buildings=[]
 for _ in range(r.randint(1,8)):
  s=r.randint(0,15);buildings.append([s,r.randint(s+1,20),r.randint(1,10)])
 return [buildings]
def rincrease(r):return [[r.randint(1,100) for _ in range(r.randint(2,30))]]
def rgrid(r):
 n=r.randint(1,12);return [[[r.randint(1,20) for _ in range(n)],[r.randint(1,20) for _ in range(n)]]]

BEAUTY='''\
def sum_of_array_beauties(nums):
    right=[0]*len(nums);smallest=float('inf')
    for i in range(len(nums)-1,-1,-1):smallest=min(smallest,nums[i]);right[i]=smallest
    largest=nums[0];answer=0
    for i in range(1,len(nums)-1):
        if largest<nums[i]<right[i+1]:answer+=2
        elif nums[i-1]<nums[i]<nums[i+1]:answer+=1
        largest=max(largest,nums[i])
    return answer
'''
REPEATED='''\
def longest_subsequence_repeated_k(s,k):
    allowed=[c for c,count in Counter(s).items() if count>=k]
    def valid(candidate):
        target=candidate*k;at=0
        for char in s:
            if at<len(target) and char==target[at]:at+=1
        return at==len(target)
    queue=deque(['']);answer=''
    while queue:
        prefix=queue.popleft()
        for char in sorted(allowed):
            candidate=prefix+char
            if valid(candidate):answer=max(answer,candidate,key=lambda x:(len(x),x));queue.append(candidate)
    return answer
'''
AVERAGE='''\
def average_building_segments(buildings):
    events={}
    for start,end,height in buildings:
        count,total=events.get(start,(0,0));events[start]=(count+1,total+height)
        count,total=events.get(end,(0,0));events[end]=(count-1,total-height)
    active=height_sum=0;previous=None;answer=[]
    for point in sorted(events):
        if previous is not None and active:
            average=height_sum//active
            if answer and answer[-1][1]==previous and answer[-1][2]==average:answer[-1][1]=point
            else:answer.append([previous,point,average])
        dc,dh=events[point];active+=dc;height_sum+=dh;previous=point
    return answer
'''
INCREASE='''\
def maximum_increasing_difference(nums):
    smallest=nums[0];answer=-1
    for value in nums[1:]:
        if value>smallest:answer=max(answer,value-smallest)
        smallest=min(smallest,value)
    return answer
'''
GRID='''\
def grid_game_second_score(grid):
    top=sum(grid[0]);bottom=0;answer=float('inf')
    for column in range(len(grid[0])):
        top-=grid[0][column]
        answer=min(answer,max(top,bottom))
        bottom+=grid[1][column]
    return answer
'''
def L(*x):return list(x)
BATCH={
2012:entry('sum_of_array_beauties',[('nums','list[int]')],'int',['arrays','prefix maxima','suffix minima'],['nums has 3 through 100000 positive integers.','An interior value earns two when it is greater than every earlier value and smaller than every later value.','Otherwise it earns one only when greater than its immediate predecessor and smaller than its immediate successor.'],[([[1,2,3]],'The middle value satisfies the global condition and contributes two.'),([[2,4,6,4]],'Four satisfies only the neighboring condition, while six satisfies neither, totaling one.')],[[x] for x in [[3,2,1],[1,2,3],[2,4,6,4],[1,3,2],[1,2,2],[5,1,2,3,6],[1,5,2,6,7],[7,6,5,4],[1,4,3,5,6],[2,1,3,4,5],[1,10,2,3,20],[4,5,1,2,3],[1,2,4,3,5],[10,20,30,25,40]]],BEAUTY,[BEAUTY.replace('right[i+1]','right[i]'),BEAUTY.replace('largest=max(largest,nums[i])','largest=nums[i]')],['Includes the current value in the suffix minimum, making the strict global test impossible.','Tracks only the previous value instead of the maximum of the whole prefix.'],beauty_o,rbeauty,L('The two-point condition needs the greatest prior and smallest later values.','Precompute suffix minima and scan while maintaining a prefix maximum; fall back to neighbor comparison.','If left_max<x<right_min add two, elif prev<x<next add one.','The maintained extrema encode both universal inequalities exactly, and the ordered fallback implements the mutually exclusive one-point rule.'),'O(n)','O(n)',5),
2014:entry('longest_subsequence_repeated_k',[('s','str'),('k','int')],'str',['backtracking','breadth-first-search','subsequences'],['2 <= k <= 2000 and 2 <= len(s) < min(2001,8*k).','Candidate t qualifies when t repeated k times is a subsequence of s.','Return the longest qualifying t, breaking ties by lexicographically largest; return empty if none.'],[(['letsleetcode',2],'Both let and ete have maximum length three; let is lexicographically larger.'),(['bb',2],'The one-letter string b repeated twice is the source string.')],[[s,k] for s,k in [('ab',2),('bb',2),('letsleetcode',2),('aaaa',2),('abab',2),('abcabc',2),('zzzaaa',3),('aabbcc',2),('baba',2),('abcdef',3),('aaabbb',3),('abcabca',2),('cccccccc',4),('xyzxyzxyz',3)]],REPEATED,[REPEATED.replace("key=lambda x:(len(x),x)","key=len"),REPEATED.replace('candidate*k','candidate*(k-1)')],['Keeps the first maximum-length candidate and ignores the lexicographically larger tie rule.','Checks only k-1 repetitions and accepts candidates that do not repeat k times.'],repeated_o,rrepeated,L('A character can appear in an answer only if its source frequency is at least k; the answer length is below eight.','Breadth-first generate qualifying candidates from frequency-eligible characters, checking repeated-subsequence feasibility.','For each valid prefix append each eligible character; keep valid extensions and maximize by (length,text).','Every answer’s prefixes also repeat k times, so pruned BFS still reaches every feasible candidate; the comparison enforces both required priorities.'),'O(candidates*n)','O(candidates)',8),
2015:entry('average_building_segments',[('buildings','list[list[int]]')],'list[list[int]]',['sweep line','prefix sums','sorting'],['buildings has up to 100000 [start,end,height] triples describing half-open intervals.','For each covered region use integer division of total active height by active building count.','Omit uncovered regions and merge adjacent regions with equal average height.'],[([[[1,4,2],[3,9,4]]],'The averages are two on [1,3), three on [3,4), and four on [4,9).'),([[[1,3,2],[2,5,3],[2,8,3]]],'Adjacent elementary intervals with equal averages merge into [1,3,2] and [3,8,3].')],[[b] for b in [[[1,2,1]],[[1,4,2],[3,9,4]],[[1,3,2],[2,5,3],[2,8,3]],[[1,2,1],[5,6,1]],[[0,10,5],[2,8,3]],[[1,5,2],[5,8,2]],[[1,5,2],[3,10,4]],[[2,4,7],[2,4,3]],[[1,3,1],[2,4,2],[3,5,3]],[[0,1,5],[1,2,6]],[[0,5,1],[1,4,2],[2,3,3]],[[10,20,100]],[[1,10,4],[2,3,8]],[[0,2,3],[4,6,3],[8,10,3]]]],AVERAGE,[AVERAGE.replace('height_sum//active','height_sum'),AVERAGE.replace("and answer[-1][2]==average",'')],['Returns total active height rather than its integer average.','Merges all adjacent covered segments even when their averages differ.'],average_o,raverage,L('Only building endpoints can change the active count or total height.','Sweep sorted endpoints with count and height deltas; emit the preceding interval from the old active state.','At each point emit [previous,point,total//count] when covered, then apply deltas; merge equal adjacent averages.','The active set is constant between consecutive endpoints, so every emitted average is exact and merging preserves the minimum-segment representation.'),'O(n log n)','O(n)',6),
2016:entry('maximum_increasing_difference',[('nums','list[int]')],'int',['arrays','greedy'],['nums has 2 through 1000 positive integers.','Choose i<j with nums[i]<nums[j] and maximize nums[j]-nums[i].','Return -1 if no qualifying pair exists.'],[([[7,1,5,4]],'Using one before five gives the maximum valid difference four.'),([[9,4,3,2]],'The array never increases after an earlier value, so return negative one.')],[[x] for x in [[1,2],[2,1],[1,1],[7,1,5,4],[9,4,3,2],[1,5,2,10],[5,1,2,3],[3,2,1,4],[10,20,5,30],[1,1000000000],[4,3,2,5,1],[2,8,1,7],[6,6,7],[9,1,8,2,7]]],INCREASE,[INCREASE.replace('smallest=min(smallest,value)','smallest=value'),INCREASE.replace('answer=-1','answer=0')],['Uses only the immediately previous value instead of the minimum earlier value.','Returns zero rather than -1 when no strictly increasing pair exists.'],increase_o,rincrease,L('For each later endpoint, the best earlier partner is the smallest value seen so far.','Scan once, updating the answer before incorporating the current value into the prefix minimum.','If x>minimum maximize x-minimum; then minimum=min(minimum,x).','The prefix invariant supplies the largest possible difference ending at each index, and maximizing those covers every valid pair.'),'O(n)','O(1)',3),
2017:entry('grid_game_second_score',[('grid','list[list[int]]')],'int',['matrices','prefix sums','game theory'],['grid has two rows and 1 through 50000 columns of positive points.','Each robot moves right then down once; the first robot zeros its path and minimizes the second robot’s optimal score.','Return the second robot’s score under optimal play.'],[([[[2,5,4],[1,5,1]]],'The best first path limits the second robot to four points.'),([[[3,3,1],[8,5,2]]],'Balancing the remaining upper-right and lower-left regions yields four.')],[[g] for g in [[[1],[1]],[[2,5,4],[1,5,1]],[[3,3,1],[8,5,2]],[[1,3,1,15],[1,3,3,1]],[[1,1],[1,1]],[[10,1],[1,10]],[[1,2,3],[3,2,1]],[[5,5,5],[1,1,1]],[[1,1,1],[5,5,5]],[[4,1,9,2],[3,8,1,7]],[[100],[200]],[[2,9,1],[8,1,7]],[[1,10,1,10],[10,1,10,1]],[[6,2,8,3,5],[1,9,2,7,4]]]],GRID,[GRID.replace('top-=grid[0][column]','top+=grid[0][column]'),GRID.replace('bottom+=grid[1][column]','bottom+=grid[0][column]')],['Adds the first robot’s top cell instead of removing it from the remaining upper-right sum.','Accumulates the top row instead of the remaining lower-left points.'],grid_o,rgrid,L('Choosing where the first robot moves down leaves only two regions for the second: top cells to the right or bottom cells to the left.','Sweep the down column while maintaining those two sums and minimize their maximum.','Remove current top; candidate=max(top_right,bottom_left); then add current bottom.','The second robot can collect one of the two remaining regions, so its optimum is their maximum; checking every first down-column gives the minimax result.'),'O(n)','O(1)',6)
}
