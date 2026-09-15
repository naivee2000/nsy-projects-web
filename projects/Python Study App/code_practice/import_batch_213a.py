"""Region averages, linear restoration, pattern matching, and palindrome allocation."""
from collections import Counter
from itertools import combinations

from .import_batch_055 import entry


def region_oracle(args):
    image, threshold = args; rows, columns = len(image), len(image[0])
    memberships = [[[] for _ in range(columns)] for _ in range(rows)]
    for top in range(rows - 2):
        for left in range(columns - 2):
            cells = [(row, column) for row in range(top, top + 3) for column in range(left, left + 3)]
            valid = all(abs(image[row][column] - image[row + dr][column + dc]) <= threshold
                        for row, column in cells for dr, dc in ((1, 0), (0, 1))
                        if row + dr < top + 3 and column + dc < left + 3)
            if valid:
                average = sum(image[row][column] for row, column in cells) // 9
                for row, column in cells:
                    memberships[row][column].append(average)
    return [[sum(values) // len(values) if values else image[row][column]
             for column, values in enumerate(memberships[row])] for row in range(rows)]


def random_region(rng):
    rows, columns = rng.randint(3, 6), rng.randint(3, 6)
    return [[[rng.randint(0, 30) for _ in range(columns)] for _ in range(rows)], rng.randint(0, 12)]


def revert_oracle(args):
    word, width = args
    for seconds in range(1, (len(word) + width - 1) // width + 1):
        removed = seconds * width
        if removed >= len(word) or word[removed:] == word[:len(word) - removed]:
            return seconds


def random_revert(rng):
    word = ''.join(rng.choice('abcd') for _ in range(rng.randint(1, 40)))
    return [word, rng.randint(1, len(word))]


def pattern_oracle(args):
    nums, pattern = args; answer = 0
    for start in range(len(nums) - len(pattern)):
        observed = [(nums[index + 1] > nums[index]) - (nums[index + 1] < nums[index])
                    for index in range(start, start + len(pattern))]
        answer += observed == pattern
    return answer


def random_pattern(rng):
    size = rng.randint(2, 30); width = rng.randint(1, size - 1)
    return [[rng.randint(1, 12) for _ in range(size)], [rng.choice((-1, 0, 1)) for _ in range(width)]]


def palindromes_oracle(args):
    words = args[0]; counts = Counter(''.join(words)); available_pairs = sum(value // 2 for value in counts.values()); answer = 0
    for chosen_count in range(1, len(words) + 1):
        if any(sum(len(words[index]) // 2 for index in chosen) <= available_pairs
               for chosen in combinations(range(len(words)), chosen_count)):
            answer = chosen_count
    return answer


def random_palindromes(rng):
    return [[''.join(rng.choice('abcdef') for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(1, 9))]]


REGION = '''def region_average_grid(image,threshold):
    rows=len(image);columns=len(image[0]);totals=[[0]*columns for _ in range(rows)];counts=[[0]*columns for _ in range(rows)]
    for top in range(rows-2):
        for left in range(columns-2):
            valid=True
            for row in range(top,top+3):
                for column in range(left,left+2):valid&=abs(image[row][column]-image[row][column+1])<=threshold
            for row in range(top,top+2):
                for column in range(left,left+3):valid&=abs(image[row][column]-image[row+1][column])<=threshold
            if valid:
                average=sum(image[row][column] for row in range(top,top+3) for column in range(left,left+3))//9
                for row in range(top,top+3):
                    for column in range(left,left+3):totals[row][column]+=average;counts[row][column]+=1
    return [[totals[row][column]//counts[row][column] if counts[row][column] else image[row][column] for column in range(columns)] for row in range(rows)]
'''


REVERT_FAST = '''def minimum_word_revert_time_large(word,k):
    size=len(word);z=[0]*size;left=right=0
    for index in range(1,size):
        if index<right:z[index]=min(right-index,z[index-left])
        while index+z[index]<size and word[z[index]]==word[index+z[index]]:z[index]+=1
        if index+z[index]>right:left,right=index,index+z[index]
    for removed in range(k,size,k):
        if z[removed]>=size-removed:return removed//k
    return (size+k-1)//k
'''


PATTERN_SIMPLE = '''def count_matching_comparison_subarrays(nums,pattern):
    answer=0
    for start in range(len(nums)-len(pattern)):
        answer+=all(((nums[start+index+1]>nums[start+index])-(nums[start+index+1]<nums[start+index]))==value for index,value in enumerate(pattern))
    return answer
'''


PATTERN_FAST = '''def count_matching_comparison_subarrays_large(nums,pattern):
    text=[(right>left)-(right<left) for left,right in zip(nums,nums[1:])]
    prefix=[0]*len(pattern)
    for index in range(1,len(pattern)):
        length=prefix[index-1]
        while length and pattern[index]!=pattern[length]:length=prefix[length-1]
        if pattern[index]==pattern[length]:length+=1
        prefix[index]=length
    answer=length=0
    for value in text:
        while length and value!=pattern[length]:length=prefix[length-1]
        if value==pattern[length]:length+=1
        if length==len(pattern):answer+=1;length=prefix[length-1]
    return answer
'''


PALINDROMES = '''def maximum_palindromes_after_swaps(words):
    counts=Counter(''.join(words));pairs=sum(value//2 for value in counts.values());answer=0
    for word in sorted(words,key=len):
        needed=len(word)//2
        if needed>pairs:break
        pairs-=needed;answer+=1
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


PATTERN_CASES = [[n,p] for n,p in [([1,2],[1]),([2,1],[-1]),([2,2],[0]),([1,2,3],[1,1]),([3,2,1],[-1,-1]),([1,1,1],[0,0]),([1,2,1],[1,-1]),([1,4,4,1,3,5,5,3],[1,0,-1]),([1,3,2,4,3],[1,-1]),([5,4,4,5],[-1,0,1]),([1,2,2,3,3,2],[1,0]),([9,7,8,8,6],[-1,1,0,-1]),([1,2,1,2,1,2],[1,-1,1]),([3,3,2,2,1,1],[0,-1,0])]]


BATCH = {
3030: entry('region_average_grid',[('image','list[list[int]]'),('threshold','int')],'list[list[int]]',['matrices','enumeration','averaging'],['image is a rectangular grid at least 3×3 with intensities from zero through 255; threshold is nonnegative.','A valid 3×3 region has every horizontal and vertical adjacent difference at most threshold.','Each pixel receives the floor of the average of its regions’ already-floored averages, or keeps its original value if it belongs to none.'],[([[[5,6,7,10],[8,9,10,10],[11,12,13,10]],3],'Both overlapping 3×3 regions are valid and each floors to nine, so every covered pixel becomes nine.'),([[[10,20,30],[15,25,35],[20,30,40],[25,35,45]],12],'The two vertical regions average twenty-five and thirty; shared rows floor their average to twenty-seven.')],[[g,t] for g,t in [([[1,1,1],[1,1,1],[1,1,1]],0),([[1,2,3],[4,5,6],[7,8,9]],1),([[1,2,3],[4,5,6],[7,8,9]],3),([[0,0,0],[0,9,0],[0,0,0]],9),([[0,0,0],[0,9,0],[0,0,0]],8),([[5,6,7],[8,9,10],[11,12,13]],1),([[5,6,7],[8,9,10],[11,12,13]],3),([[1,1,1,10],[1,1,1,10],[1,1,1,10]],0),([[2,4,6,8],[2,4,6,8],[2,4,6,8]],2),([[1,2,1],[2,1,2],[1,2,1]],1),([[255,255,255],[255,255,255],[255,255,255]],0),([[0,10,20],[10,20,30],[20,30,40],[30,40,50]],10),([[3,3,9,9],[3,3,9,9],[3,3,9,9],[3,3,9,9]],6),([[1,5,1,5],[5,1,5,1],[1,5,1,5]],4)]],REGION,[REGION.replace('for row in range(top,top+2):','for row in range(top,top):'),REGION.replace('))//9','))/9')],['Checks horizontal neighbors only and can accept a region with an invalid vertical edge.','Averages raw fractional region means instead of flooring each region before combining memberships.'],region_oracle,random_region,lesson('Region validity depends on twelve internal adjacency edges, and overlapping regions contribute independently.','Enumerate each 3×3 top-left corner, validate its six horizontal and six vertical edges, then accumulate its floored mean into nine cells.','Maintain per-pixel sum and count of valid-region means; divide at the end or retain the source pixel when count is zero.','Every possible region has one top-left corner, and accumulating its already-rounded contribution implements the specified two-stage flooring exactly.'),'O(rows*columns)','O(rows*columns)',5),
3031: entry('minimum_word_revert_time_large',[('word','str'),('k','int')],'int',['Z algorithm','strings','prefix matching'],['word is a nonempty lowercase string with length up to one million and 1≤k≤length.','Each second removes k leading characters and appends any k characters.','Return the minimum positive restoration time using linear-time prefix matching.'],[(['abacaba',3],'At two seconds, the forced suffix a matches the equally long original prefix; appended characters can restore the remainder.'),(['abacaba',4],'After one removal, suffix aba equals prefix aba, so one second is sufficient.')],[[w,k] for w,k in [('a',1),('aa',1),('ab',1),('aaaa',2),('abab',2),('abcabc',3),('abcabc',2),('abcbabcd',2),('aaaaa',2),('abcdef',4),('abaaba',2),('xyzxyzx',3),('leetcode',3),('aabaacaabaa',4)]],REVERT_FAST,[REVERT_FAST.replace('>=size-removed','>size-removed'),REVERT_FAST.replace('z=[0]*size','z=[size]+[0]*(size-1)').replace('range(k,size,k)','range(0,size,k)')],['Requires an overlap longer than the entire remaining suffix, so it never accepts a valid boundary.','Uses the alternate Z[0]=n convention and mistakenly tests offset zero, returning the forbidden time zero.'],revert_oracle,random_revert,lesson('A Z value gives the prefix-match length beginning at every possible removed offset.','Build the Z array once, then inspect only positive multiples of k.','Return removed/k at the first offset with Z[removed]≥n-removed; otherwise return ceil(n/k).','That inequality exactly states that every still-forced suffix character equals its original prefix position, while arbitrary appended characters fill the rest.'),'O(n)','O(n)',8),
3034: entry('count_matching_comparison_subarrays',[('nums','list[int]'),('pattern','list[int]')],'int',['arrays','enumeration','comparisons'],['nums has at least two positive integers; pattern is nonempty, shorter than nums, and contains only -1, 0, and 1.','Each pattern value specifies decrease, equality, or increase between adjacent values.','Count length-|pattern|+1 subarrays whose full comparison sequence matches.'],[([[1,2,3,4,5,6],[1,1]],'Each of the four length-three windows has two strict increases.'),([[1,4,4,1,3,5,5,3],[1,0,-1]],'Windows [1,4,4,1] and [3,5,5,3] match increase, equality, decrease.')],PATTERN_CASES,PATTERN_SIMPLE,[PATTERN_SIMPLE.replace('==value','!=-value'),PATTERN_SIMPLE.replace('range(len(nums)-len(pattern))','range(len(nums)-len(pattern)-1)')],['Uses the opposite sign convention for increases and decreases.','Omits the final legal starting position.'],pattern_oracle,random_pattern,lesson('Replace each adjacent pair by its sign: one, zero, or negative one.','For every legal start, compare its next m adjacent signs with the pattern.','Normalize each comparison using (right>left)-(right<left) and require all m entries to equal pattern.','A window’s values satisfy the definition exactly when its unique adjacent-sign sequence equals the requested sequence.'),'O(nm)','O(1)',5),
3035: entry('maximum_palindromes_after_swaps',[('words','list[str]')],'int',['greedy','counting','strings'],['words is a nonempty list of nonempty lowercase strings.','Characters may be swapped arbitrarily within or between strings, but every string length stays fixed.','Return the maximum number of strings that can simultaneously be palindromes.'],[([['abbb','ba','aa']],'The characters can be redistributed as bbbb, aa, and aa, making all three strings palindromes.'),([['abc','ab']],'The same pool can form aca and bb, so both target lengths can be palindromic.')],[[w] for w in [['a'],['ab'],['aa'],['ab','cd'],['a','b','c'],['abc','def'],['aa','bb','cc'],['abc','a','b'],['cd','ef','a'],['abcd','efgh','ij'],['aabb','ccdd','ee'],['abcde','f','g'],['aaa','bbb','ccc','ddd'],['ab','abc','abcd','abcde']]],PALINDROMES,[PALINDROMES.replace('sorted(words,key=len)','words'),PALINDROMES.replace('len(word)//2','(len(word)+1)//2')],['Processes input order rather than cheapest palindrome lengths first.','Charges a character pair for the center of every odd-length palindrome.'],palindromes_oracle,random_palindromes,lesson('Only mirrored character pairs are scarce; odd centers can use any leftover single character.','Count all available equal-character pairs and satisfy strings in ascending required-pair count.','pairs=sum(freq//2); for lengths sorted ascending, spend length//2 pairs while affordable.','Shorter requirements never reduce how many later targets can fit, so the exchange argument makes ascending pair cost optimal.'),'O(total characters+n log n)','O(26+n)',5),
3036: entry('count_matching_comparison_subarrays_large',[('nums','list[int]'),('pattern','list[int]')],'int',['KMP','arrays','string matching'],['nums may contain up to one million positive integers; pattern is nonempty and shorter than nums.','Convert adjacent comparisons to -1, 0, or 1 and count every overlapping occurrence of pattern.','Return the count in O(n+m) time.'],[([[1,2,3,4,5,6],[1,1]],'The comparison text is five ones, containing the length-two pattern at four overlapping starts.'),([[1,4,4,1,3,5,5,3],[1,0,-1]],'KMP finds the requested comparison sequence at starts zero and four.')],PATTERN_CASES,PATTERN_FAST,[PATTERN_FAST.replace('length=prefix[length-1]','length=0'),PATTERN_FAST.replace('(right>left)-(right<left)','(right<left)-(right>left)')],['Resets fully after every mismatch or match and misses overlapping pattern occurrences.','Reverses the sign convention for increases and decreases.'],pattern_oracle,random_pattern,lesson('The problem is ordinary pattern matching after mapping adjacent numbers to comparison signs.','Build a KMP prefix table for pattern and scan the sign sequence without materializing substrings.','Advance or fall back by prefix links; on a full match increment and fall back to allow overlaps.','KMP’s state is the longest pattern prefix matching the processed suffix, so every and only full comparison-pattern occurrence is counted in linear time.'),'O(n+m)','O(n+m)',8),
}
