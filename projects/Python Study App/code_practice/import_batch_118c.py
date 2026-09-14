"""Third reviewed group of workbook batch 118."""
from .import_batch_055 import entry

def days_o(a):
 security,time=a
 return [i for i in range(time,len(security)-time) if all(security[j]>=security[j+1] for j in range(i-time,i)) and all(security[j]<=security[j+1] for j in range(i,i+time))]
def bombs_o(a):
 bombs=a[0];best=0
 for start in range(len(bombs)):
  seen={start};changed=True
  while changed:
   changed=False
   for i in list(seen):
    x,y,r=bombs[i]
    for j,(u,v,_) in enumerate(bombs):
     if j not in seen and (x-u)**2+(y-v)**2<=r*r:seen.add(j);changed=True
  best=max(best,len(seen))
 return best
def rods_o(a):
 rings=a[0];return sum(all(color+str(rod) in rings for color in 'RGB') for rod in range(10))
def ranges_o(a):
 nums=a[0];return sum(max(nums[i:j])-min(nums[i:j]) for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def refill_o(a):
 plants,ca,cb=a;left=0;right=len(plants)-1;wa=ca;wb=cb;answer=0
 while left<=right:
  if left==right:
   answer+=max(wa,wb)<plants[left];break
  if wa<plants[left]:wa=ca;answer+=1
  wa-=plants[left];left+=1
  if wb<plants[right]:wb=cb;answer+=1
  wb-=plants[right];right-=1
 return answer
def rdays(r):
 values=[r.randint(0,20) for _ in range(r.randint(1,30))];return [values,r.randint(0,15)]
def rbombs(r):return [[[r.randint(-10,10),r.randint(-10,10),r.randint(0,12)] for _ in range(r.randint(1,9))]]
def rrods(r):return [''.join(r.choice('RGB')+str(r.randint(0,9)) for _ in range(r.randint(1,25)))]
def rranges(r):return [[r.randint(-20,20) for _ in range(r.randint(1,20))]]
def rrefill(r):
 ca,cb=r.randint(1,12),r.randint(1,12);limit=min(ca,cb);return [[r.randint(1,limit) for _ in range(r.randint(1,20))],ca,cb]

DAYS='''\
def good_bank_days(security,time):
    n=len(security);before=[0]*n;after=[0]*n
    for i in range(1,n):
        if security[i]<=security[i-1]:before[i]=before[i-1]+1
    for i in range(n-2,-1,-1):
        if security[i]<=security[i+1]:after[i]=after[i+1]+1
    return [i for i in range(n) if before[i]>=time and after[i]>=time]
'''
BOMBS='''\
def maximum_bomb_detonation(bombs):
    graph=[[] for _ in bombs]
    for i,(x,y,radius) in enumerate(bombs):
        for j,(u,v,_) in enumerate(bombs):
            if i!=j and (x-u)**2+(y-v)**2<=radius**2:graph[i].append(j)
    answer=0
    for start in range(len(bombs)):
        seen={start};stack=[start]
        while stack:
            node=stack.pop()
            for neighbor in graph[node]:
                if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
        answer=max(answer,len(seen))
    return answer
'''
RODS='''\
def rods_with_all_colors(rings):
    masks=[0]*10;bits={'R':1,'G':2,'B':4}
    for index in range(0,len(rings),2):masks[int(rings[index+1])]|=bits[rings[index]]
    return masks.count(7)
'''
RANGES='''\
def sum_subarray_ranges(nums):
    answer=0
    for left in range(len(nums)):
        smallest=largest=nums[left]
        for right in range(left+1,len(nums)):
            smallest=min(smallest,nums[right]);largest=max(largest,nums[right]);answer+=largest-smallest
    return answer
'''
REFILL='''\
def minimum_two_person_refills(plants,capacity_a,capacity_b):
    left,right=0,len(plants)-1;water_a,water_b=capacity_a,capacity_b;answer=0
    while left<right:
        if water_a<plants[left]:water_a=capacity_a;answer+=1
        water_a-=plants[left];left+=1
        if water_b<plants[right]:water_b=capacity_b;answer+=1
        water_b-=plants[right];right-=1
    if left==right and max(water_a,water_b)<plants[left]:answer+=1
    return answer
'''
def L(*x):return list(x)
BATCH={
2100:entry('good_bank_days',[('security','list[int]'),('time','int')],'list[int]',['arrays','dynamic programming','prefix counts'],['A day is good when the preceding time transitions are nonincreasing and the following time transitions are nondecreasing.','Day indices must have time available days on both sides.','Return all good indices in increasing order.'],[([[5,3,3,3,5,6,2],2],'Days two and three each have two nonincreasing steps before and two nondecreasing steps after.'),([[1,1,1,1,1],0],'With no required neighboring days, every index qualifies.')],[[s,t] for s,t in [([1],1),([1,2,3],1),([3,2,1],1),([3,2,2,3],1),([3,2,2,3],2),([1,1,1],1),([5,4,3,4,5],2),([5,3,3,3,5,6,2],1),([1,2,1,2,1],1),([9,8,7,6,7,8,9],3),([1,2],0),([2,1,2],1),([4,4,3,3,4,4],2),([10,9,8],5)]],DAYS,[DAYS.replace('security[i]<=security[i-1]','security[i]<security[i-1]'),DAYS.replace('after[i]>=time','after[i]>time')],['Requires strict decreases and rejects equal guard counts.','Requires one extra nondecreasing day after the candidate.'],days_o,rdays,L('Precompute how many consecutive qualifying transitions end and begin at every day.','Scan left-to-right for nonincreasing run lengths and right-to-left for nondecreasing run lengths.','Index i qualifies when before[i]>=time and after[i]>=time.','Those two run lengths are exactly the required inequalities on each side, and the threshold also excludes boundary-short indices.'),'O(n)','O(n)',5),
2101:entry('maximum_bomb_detonation',[('bombs','list[list[int]]')],'int',['graphs','depth first search','geometry'],['Each bomb is [x,y,radius]; triggering is directed because radii may differ.','A detonated bomb recursively triggers every center within or on its circular range.','Return the largest cascade size from one starting bomb.'],[([[[2,1,3],[6,1,4]]],'The second bomb reaches the first, so starting at the second detonates both.'),([[[1,1,5],[10,10,5]]],'Neither center lies in the other range, so the largest cascade has size one.')],[[b] for b in [[[0,0,0]],[[0,0,1],[1,0,1]],[[0,0,1],[2,0,2]],[[0,0,2],[2,0,1]],[[0,0,5],[3,4,1]],[[0,0,4],[3,4,1]],[[0,0,2],[2,0,2],[4,0,2]],[[0,0,10],[1,1,1],[20,20,1]],[[1,2,3],[1,2,3]],[[0,0,3],[2,0,1],[4,0,5]],[[0,0,1],[0,1,1],[0,2,1]],[[5,5,0],[5,5,0]],[[0,0,100],[50,50,1],[51,50,1]],[[0,0,2],[-2,0,2],[2,0,2]]]],BOMBS,[BOMBS.replace('<=radius**2','<radius**2'),BOMBS.replace('graph[i].append(j)','graph[j].append(i)')],['Excludes bombs whose centers lie exactly on the blast boundary.','Reverses every directed trigger edge and computes the wrong cascades.'],bombs_o,rbombs,L('Convert each geometric reach relation into a directed graph edge.','Compare squared distance with squared source radius, then run a reachability search from every bomb.','Add i->j when dx*dx+dy*dy<=r_i*r_i; track the largest visited set.','Graph reachability precisely matches recursive triggering, and trying every possible first bomb finds the maximum cascade.'),'O(n^3)','O(n^2)',5),
2103:entry('rods_with_all_colors',[('rings','str')],'int',['strings','bit masks'],['rings consists of color-digit pairs; colors are R, G, or B and rods are zero through nine.','Multiple rings of the same color on one rod count only once.','Return the number of rods carrying all three colors.'],[(['B0B6G0R6R0R6G9'],'Only rod zero has red, green, and blue rings.'),(['B0R0G0R9R0B0G0'],'Rod zero still counts once despite repeated colors.')],[[s] for s in ['R0','R0G0','R0G0B0','R0G1B0','R9G9B9','R0G0B0R1G1B1','B2G2R2B2','R0G1B2','R1R1G1B1','G5B5R5','B0G0R1G1B1','R3G3B4B3','R0G0B0R9G9B9','B7R7G8G7']],RODS,[RODS.replace("'B':4","'B':2"),RODS.replace('masks.count(7)','masks.count(6)')],['Uses the same bit for blue and green, so no rod reaches mask seven.','Counts rods missing red by testing mask six.'],rods_o,rrods,L('A three-bit mask records which colors have appeared on each rod.','Assign one bit to R, G, and B and OR it into the indexed rod mask.','After all pairs, count masks equal to binary 111.','OR is idempotent for duplicate colors, and mask seven occurs exactly when every color bit is present.'),'O(length)','O(1)',3),
2104:entry('sum_subarray_ranges',[('nums','list[int]')],'int',['arrays','enumeration'],['nums is nonempty and may contain negative or repeated values.','The range of a subarray is its maximum minus its minimum.','Return the sum of ranges over every nonempty contiguous subarray.'],[([[1,2,3]],'The length-two ranges are one and one, and the length-three range is two, totaling four.'),([[1,3,3]],'The ranges are zero for singletons, two for [1,3] and [1,3,3], and zero for [3,3], totaling four.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[1,2,1],[3,1,2],[1,2,3,4],[-1,-2,-3],[0,5,-5],[2,2,2,3],[4,1,4,1],[10,-10],[5,3,8,2],[1,3,2,4,0]]],RANGES,[RANGES.replace('largest-smallest','largest+smallest'),RANGES.replace('range(left+1,len(nums))','range(left+2,len(nums))')],['Adds extrema instead of subtracting the minimum from the maximum.','Skips every length-two subarray.'],ranges_o,rranges,L('Fixing the left endpoint lets each extension update its extrema in constant time.','For every left endpoint, carry the smallest and largest values while moving right.','After including nums[right], add largest-smallest.','Each subarray is visited exactly once at its endpoints, and the maintained extrema equal that subarray’s range.'),'O(n^2)','O(1)',5),
2105:entry('minimum_two_person_refills',[('plants','list[int]'),('capacity_a','int'),('capacity_b','int')],'int',['arrays','two pointers','simulation'],['Alice waters from the left with capacity_a and Bob from the right with capacity_b; every plant need fits both cans.','They refill only when their current water cannot cover their next plant.','At a shared middle plant, the person with more remaining water waters; ties go to Alice. Return total refills.'],[([[2,2,3,3],5,5],'Alice refills before plant one? Processing from both ends requires one refill in total.'),([[2,2,3,3],3,4],'Each person refills once before their second plant, totaling two.')],[[p,a,b] for p,a,b in [([1],1,1),([2],1,2),([2],1,1),([1,1],1,1),([2,2],2,2),([2,2],3,2),([1,2,1],2,2),([3,1,3],3,3),([1,1,1,1],2,2),([4,1,2],4,3),([2,3,2,3,2],5,5),([5,5,5],5,5),([1,4,1,4],5,4),([2,1,2,1,2],3,4)]],REFILL,[REFILL.replace('water_a<plants[left]','water_a<=plants[left]'),REFILL.replace('max(water_a,water_b)<plants[left]','min(water_a,water_b)<plants[left]')],['Refills unnecessarily when Alice has exactly enough water.','At the middle plant, tests the weaker can instead of the stronger available can.'],refill_o,rrefill,L('The watering order is fixed from both ends, so simulate both remaining capacities with converging pointers.','Before each side waters, refill only if its remainder is insufficient; handle a final shared plant with max remainder.','Advance left and right together; for left==right add one refill only when max(water_a,water_b)<need.','The state exactly matches each person’s can after their assigned plants, and the middle rule chooses the only potentially refill-free can.'),'O(n)','O(1)',5)
}
BATCH[2101]['boundaries'][-1]=[[[-2,0,2],[2,0,2],[0,0,0]]]
