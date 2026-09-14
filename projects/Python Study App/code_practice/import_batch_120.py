"""First reviewed group of workbook batch 120."""
from itertools import permutations
from .import_batch_055 import entry

def swaps_o(a):
 nums=a[0];ones=sum(nums)
 if ones==0:return 0
 return min(ones-sum(nums[(start+i)%len(nums)] for i in range(ones)) for start in range(len(nums)))
def words_o(a):
 starts,targets=a;start_sets={frozenset(word) for word in starts};return sum(any(frozenset(set(word)-{char}) in start_sets for char in word) for word in targets)
def bloom_o(a):
 plant,grow=a;best=10**9
 for order in permutations(range(len(plant))):
  elapsed=answer=0
  for i in order:elapsed+=plant[i];answer=max(answer,elapsed+grow[i])
  best=min(best,answer)
 return best
def water_o(a):
 buckets,loss=a;efficiency=(100-loss)/100;low=0.0;high=max(buckets)
 for _ in range(100):
  middle=(low+high)/2;surplus=sum(max(x-middle,0) for x in buckets)*efficiency;deficit=sum(max(middle-x,0) for x in buckets)
  if surplus>=deficit:low=middle
  else:high=middle
 return low
def divide_o(a):
 s,k,fill=a;answer=[]
 for i in range(0,len(s),k):answer.append((s[i:i+k]+fill*k)[:k])
 return answer
def rswaps(r):return [[r.randint(0,1) for _ in range(r.randint(1,25))]]
def rwords(r):
 alphabet='abcdef';starts=[''.join(r.sample(alphabet,r.randint(1,4))) for _ in range(r.randint(1,8))];targets=[''.join(r.sample(alphabet,r.randint(1,5))) for _ in range(r.randint(1,8))];return [starts,targets]
def rbloom(r):
 n=r.randint(1,7);return [[r.randint(1,8) for _ in range(n)],[r.randint(1,8) for _ in range(n)]]
def rwater(r):return [[r.randint(0,30) for _ in range(r.randint(1,10))],r.randint(0,99)]
def rdivide(r):
 s=''.join(r.choice('abcdef') for _ in range(r.randint(1,25)));return [s,r.randint(1,8),r.choice('xyz')]

SWAPS='''\
def minimum_circular_one_swaps(nums):
    width=sum(nums)
    if width==0:return 0
    current=sum(nums[:width]);best=current
    for right in range(width,len(nums)+width):
        current+=nums[right%len(nums)]-nums[(right-width)%len(nums)];best=max(best,current)
    return width-best
'''
WORDS='''\
def count_add_letter_words(start_words,target_words):
    masks=set()
    for word in start_words:masks.add(sum(1<<(ord(char)-97) for char in word))
    answer=0
    for word in target_words:
        mask=sum(1<<(ord(char)-97) for char in word)
        if any(mask^(1<<(ord(char)-97)) in masks for char in word):answer+=1
    return answer
'''
BLOOM='''\
def earliest_full_bloom(plant_time,grow_time):
    elapsed=answer=0
    for grow,plant in sorted(zip(grow_time,plant_time),reverse=True):
        elapsed+=plant;answer=max(answer,elapsed+grow)
    return answer
'''
WATER='''\
def maximum_equal_water_level(buckets,loss):
    efficiency=(100-loss)/100;low,high=0.0,float(max(buckets))
    for _ in range(80):
        middle=(low+high)/2;surplus=sum(max(value-middle,0) for value in buckets)*efficiency;need=sum(max(middle-value,0) for value in buckets)
        if surplus>=need:low=middle
        else:high=middle
    return low
'''
DIVIDE='''\
def divide_filled_groups(s,k,fill):
    return [s[index:index+k].ljust(k,fill) for index in range(0,len(s),k)]
'''
def L(*x):return list(x)
BATCH={
2134:entry('minimum_circular_one_swaps',[('nums','list[int]')],'int',['arrays','sliding windows'],['nums is a nonempty circular binary array.','A swap exchanges any two positions; group every one into one circularly contiguous block.','Return the minimum swaps.'],[([[0,1,0,1,1,0,0]],'A length-three circular window contains two ones, so one zero must be swapped out.'),([[1,1,0,0,1]],'The last, first, and second positions already form a circular all-one block.')],[[x] for x in [[0],[1],[0,0],[1,1],[1,0],[0,1,0],[1,0,1],[1,0,0,1],[0,1,1,0],[1,1,1,0,0],[0,0,0,0],[1,0,1,0,1],[0,1,0,0,1,1],[1,0,0,0,1,0,1]]],SWAPS,[SWAPS.replace('width=sum(nums)','width=len(nums)'),SWAPS.replace('range(width,len(nums)+width)','range(width,len(nums))')],['Uses the entire array as the target window instead of the number of ones.','Ignores windows that wrap across the circular boundary.'],swaps_o,rswaps,L('A target block has length equal to the total number of ones; zeros inside it are exactly the swaps needed.','Find the circular window of that length containing the most ones.','Slide across nums modulo n and return width-maximum_ones.','Each outside one can swap with one inside zero, so minimizing zeros over all possible circular blocks is necessary and sufficient.'),'O(n)','O(1)',5),
2135:entry('count_add_letter_words',[('start_words','list[str]'),('target_words','list[str]')],'int',['strings','bit masks','sets'],['Letters within every word are distinct lowercase characters.','A target qualifies when removing exactly one of its letters yields the letter set of a start word; rearrangement is allowed.','Count qualifying target occurrences.'],[([['ant','act','tack'],['tack','act','acti']],'tack comes from act plus k and acti from act plus i, so two targets qualify.'),([['ab','a'],['abc','abcd','ba']],'abc can come from ab; the other targets cannot be formed by one addition.')],[[s,t] for s,t in [(['a'],['ab']),(['a'],['a']),(['ab'],['abc']),(['ab'],['ac']),(['ab','cd'],['abc','cde']),(['xyz'],['wxyz']),(['a','b'],['ab']),(['abc'],['abcd','abce']),(['ab'],['cab','dab']),(['ace'],['abcd']),(['ab','bc'],['abc']),(['x'],['xy','xz']),(['abc','def'],['abcf','defg']),(['a'],['ba','ca','da'])]],WORDS,[WORDS.replace('mask^','mask|'),WORDS.replace('for char in word','for char in word[:-1]',1)],['Adds a bit instead of removing the tested target letter.','Tests every target letter except the last one and misses valid removals there.'],words_o,rwords,L('Distinct letters allow each word to be represented by a 26-bit set mask.','Store all start masks; for each target, remove each one-bit in turn and test membership.','Count target once if any target_mask XOR letter_bit belongs to the start set.','Removing one target letter exactly reverses the allowed append-and-rearrange operation, and masks ignore irrelevant order.'),'O(total characters)','O(start words)',5),
2136:entry('earliest_full_bloom',[('plant_time','list[int]'),('grow_time','list[int]')],'int',['arrays','greedy','sorting'],['The arrays are equally sized with positive durations.','Only one seed can be planted at a time; growth occurs in parallel after planting completes.','Return the earliest day when every seed has bloomed.'],[([[1,4,3],[2,3,1]],'Planting in grow-time order three, two, one yields all blooms by day nine.'),([[1,2,3,2],[2,1,2,1]],'Prioritizing the two longest grow times produces full bloom on day nine.')],[[p,g] for p,g in [([1],[1]),([5],[2]),([1,1],[1,1]),([1,2],[5,1]),([1,2],[1,5]),([3,1,2],[1,3,2]),([5,4,3],[3,4,5]),([1,1,1],[10,1,1]),([2,2,2],[3,2,1]),([4,1,4,1],[2,8,1,7]),([1,3,2],[3,2,1]),([10,1],[1,10]),([2,5,1],[6,1,4]),([3,3,1,1],[2,9,8,1])]],BLOOM,[BLOOM.replace('reverse=True','reverse=False'),BLOOM.replace('elapsed+=plant','elapsed+=grow')],['Plants shortest grow-time seeds first and delays urgent long growth.','Adds grow time to the planting schedule instead of plant time.'],bloom_o,rbloom,L('If two adjacent seeds have grow times a<b, planting b first cannot delay the later of their bloom days.','Sort seeds by descending grow time, accumulate planting time, and track completion plus grow time.','For each (grow,plant), elapsed+=plant; answer=max(answer,elapsed+grow).','Repeated adjacent exchanges place longer growth first without worsening the objective, proving the greedy order optimal.'),'O(n log n)','O(n)',8),
2137:entry('maximum_equal_water_level',[('buckets','list[int]'),('loss','int')],'float',['binary search','continuous optimization'],['Bucket amounts are nonnegative and loss is an integer percentage from zero through ninety-nine.','Transferred surplus retains (100-loss) percent; find the greatest common attainable level.','Answers within 1e-5 absolute error are accepted.'],[([[1,2,7],80],'At level two, bucket seven donates five units and one retained unit fills bucket one.'),([[2,4,6],0],'Without loss, total water twelve divides evenly to level four.')],[[b,l] for b,l in [([1],0),([5],99),([0,10],0),([0,10],50),([1,2,7],0),([1,2,7],80),([2,4,6],25),([0,0,0],50),([10,10],90),([1,9,9],50),([3,8,12,20],10),([0,1],99),([100,0,0],75),([5,15,25],33)]],WATER,[WATER.replace('efficiency=(100-loss)/100','efficiency=loss/100'),WATER.replace('surplus>=need','surplus>need')],['Treats the lost percentage as the retained transfer percentage.','Uses strict feasibility and biases exact attainable levels downward.'],water_o,rwater,L('Feasibility is monotone: lowering a target reduces deficits and increases available surplus.','For a candidate level, multiply donated excess by retention efficiency and compare with total deficit.','Binary-search [0,max] and keep middle when retained surplus>=need.','The inequality is necessary and sufficient because water is freely transferable among buckets subject only to the uniform loss.'),'O(n log(precision))','O(1)',5),
2138:entry('divide_filled_groups',[('s','str'),('k','int'),('fill','str')],'list[str]',['strings','simulation'],['s is nonempty, k is positive, and fill is one character.','Split s consecutively into groups of exactly k characters.','Pad only the final short group with fill until its length is k.'],[(['abcdefghi',3,'x'],'The string divides evenly into abc, def, and ghi with no padding.'),(['abcdefghij',3,'x'],'The final j is padded twice, producing jxx.')],[[s,k,f] for s,k,f in [('a',1,'x'),('a',2,'x'),('ab',3,'z'),('abc',3,'x'),('abcd',2,'x'),('abcde',2,'q'),('hello',4,'x'),('python',10,'_'),('aaaaa',3,'b'),('1234567',3,'0'),('xy',1,'z'),('algorithm',4,'!'),('code',5,'c'),('abcdefgh',3,'x')]],DIVIDE,[DIVIDE.replace('.ljust(k,fill)','.rjust(k,fill)'),DIVIDE.replace('range(0,len(s),k)','range(0,len(s)-k,k)')],['Pads the final group on the left instead of the right.','Stops before the final group and omits it.'],divide_o,rdivide,L('Fixed-step slicing naturally preserves order and isolates only the possibly short final chunk.','Take s[index:index+k] for indices 0,k,2k,... and right-pad each slice to k.','Return each slice.ljust(k,fill).','All nonfinal slices already have size k; only the last receives exactly the missing number of fill characters.'),'O(length)','O(length)',3)
}
BATCH[2137]['comparator']='float'
BATCH[2137]['wrong'][1]=WATER.replace('range(80)','range(10)')
BATCH[2137]['wrong_reasons'][1]='Stops binary search after ten iterations and cannot meet the required 1e-5 accuracy.'
