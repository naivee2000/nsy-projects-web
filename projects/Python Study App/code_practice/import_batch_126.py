"""First slice of workbook batch 126."""

from collections import Counter
from itertools import combinations

from .import_batch_055 import entry


def tiles_oracle(args):
    tiles, length = args
    white = {position for left, right in tiles for position in range(left, right + 1)}
    return max((sum(position in white for position in range(start, start + length))
                for start in range(min(white) - length, max(white) + 1)), default=0)


def random_tiles(rng):
    tiles = []
    position = rng.randint(0, 4)
    for _ in range(rng.randint(1, 8)):
        size = rng.randint(1, 6)
        tiles.append([position, position + size - 1])
        position += size + rng.randint(1, 5)
    return [tiles, rng.randint(1, 20)]


def variance_oracle(args):
    text = args[0]
    best = 0
    for left in range(len(text)):
        counts = Counter()
        for right in range(left, len(text)):
            counts[text[right]] += 1
            if len(counts) >= 2:
                best = max(best, max(counts.values()) - min(counts.values()))
    return best


def random_variance(rng):
    return ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 30)))]


def anagrams_oracle(args):
    result = []
    for word in args[0]:
        if not result or Counter(result[-1]) != Counter(word):
            result.append(word)
    return result


def random_anagrams(rng):
    return [["".join(rng.choice("abcd") for _ in range(rng.randint(1, 7))) for _ in range(rng.randint(1, 20))]]


def floors_oracle(args):
    bottom, top, special = args
    marked = set(special)
    best = current = 0
    for floor in range(bottom, top + 1):
        if floor in marked: current = 0
        else: current += 1; best = max(best, current)
    return best


def random_floors(rng):
    bottom = rng.randint(1, 30); top = rng.randint(bottom + 1, bottom + 30)
    special = rng.sample(range(bottom, top + 1), rng.randint(1, top - bottom + 1))
    return [bottom, top, special]


def and_oracle(args):
    values = args[0]
    best = 0
    for size in range(1, len(values) + 1):
        for group in combinations(values, size):
            result = group[0]
            for value in group[1:]: result &= value
            if result > 0: best = size
    return best


def random_and(rng):
    return [[rng.randint(1, 255) for _ in range(rng.randint(1, 11))]]


TILES = '''\
def maximum_white_tiles_covered(tiles,carpet_len):
    tiles=sorted(tiles);covered=left=answer=0
    for right,(start,end) in enumerate(tiles):
        covered+=end-start+1
        carpet_start=end-carpet_len+1
        while tiles[left][1]<carpet_start:
            covered-=tiles[left][1]-tiles[left][0]+1;left+=1
        uncovered=max(0,carpet_start-tiles[left][0])
        answer=max(answer,covered-uncovered)
    return answer
'''

VARIANCE = '''\
def largest_substring_variance(s):
    from collections import Counter
    totals=Counter(s);answer=0
    for major in totals:
        for minor in totals:
            if major==minor:continue
            major_count=minor_count=0;remaining_minor=totals[minor]
            for char in s:
                if char==major:major_count+=1
                if char==minor:minor_count+=1;remaining_minor-=1
                if minor_count:answer=max(answer,major_count-minor_count)
                if major_count<minor_count and remaining_minor:
                    major_count=minor_count=0
    return answer
'''

ANAGRAMS = '''\
def remove_adjacent_anagrams(words):
    result=[];previous=None
    for word in words:
        signature=tuple(sorted(word))
        if signature!=previous:result.append(word);previous=signature
    return result
'''

FLOORS = '''\
def maximum_non_special_floor_run(bottom,top,special):
    ordered=[bottom-1]+sorted(special)+[top+1]
    return max(right-left-1 for left,right in zip(ordered,ordered[1:]))
'''

AND = '''\
def largest_positive_and_combination(candidates):
    return max(sum(value>>bit&1 for value in candidates) for bit in range(max(candidates).bit_length()))
'''


BATCH = {
    2271: entry('maximum_white_tiles_covered',[('tiles','list[list[int]]'),('carpet_len','int')],'int',['arrays','sliding windows','sorting'],['Each inclusive interval [left,right] contains white tiles and intervals do not overlap.','A carpet covers carpet_len consecutive integer positions and may start anywhere.','Return the greatest number of white tiles covered, including partial boundary intervals.'],[([[[1,5],[10,11],[12,18],[20,25],[30,32]],10],'A best length-ten placement covers nine white positions across neighboring intervals.'),([[[10,11],[1,1]],2],'A length-two carpet can cover both tiles in interval [10,11].')],[[t,l] for t,l in [([[1,1]],1),([[1,1]],5),([[1,5],[10,11],[12,18],[20,25],[30,32]],10),([[10,11],[1,1]],2),([[1,3],[5,7]],4),([[1,10]],3),([[1,2],[4,5]],10),([[5,5],[7,9],[12,12]],5),([[0,4],[10,14]],6),([[2,6],[8,8]],3),([[1,1],[3,3],[5,5]],3),([[10,20],[30,40]],15),([[1,4],[6,10],[12,15]],8),([[100,101],[105,110]],6)]],TILES,[TILES.replace('end-carpet_len+1','end-carpet_len'),TILES.replace('covered-uncovered','covered')],['Uses a carpet one position longer because its inclusive start is off by one.','Counts the uncovered prefix of the partially intersected left interval.'],tiles_oracle,random_tiles,['Sort intervals and align a candidate carpet’s right edge with each interval end.','Maintain total white length of intervals intersecting that carpet and remove intervals wholly left of it.','Subtract only the uncovered prefix of the current leftmost interval before updating the answer.','Sliding endpoints visit every structurally optimal right alignment, and the correction gives the exact covered portion of the sole partial interval.'],'O(n log n)','O(n) for sorting',6),
    2272: entry('largest_substring_variance',[('s','str')],'int',['strings','dynamic programming','Kadane'],['For a substring and two distinct characters both present in it, variance is frequency(major)-frequency(minor).','Choose any ordered character pair and any nonempty contiguous substring.','Return the maximum variance, or zero when s has fewer than two distinct characters.'],[(['aababbb'],'In substring babbb, b occurs four times and a once, giving variance three.'),(['abcde'],'Every substring containing two characters has equal one-one counts, so the maximum is zero.')],[[x] for x in ['a','ab','aa','aababbb','abcde','abab','baaa','bbba','abcabc','mississippi','aaaaab','bbaabb','xyzzzzx','cabbaac']],VARIANCE,[VARIANCE.replace('if minor_count:','if True:'),VARIANCE.replace('and remaining_minor','')],['Allows a substring with no minor character, which is not a valid two-character variance.','Resets after the final minor occurrence and can discard the only valid suffix candidate.'],variance_oracle,random_variance,['Fix an ordered pair of major and minor characters and scan like a constrained Kadane algorithm.','Track their count difference, update only after seeing a minor, and reset a negative segment only when another minor remains.','Repeat for every ordered distinct pair and keep the greatest major_count-minor_count.','Every optimal substring has some ordered frequency pair; the reset discards only prefixes that cannot improve a future valid segment.'],'O(alphabet^2*n)','O(alphabet)',8),
    2273: entry('remove_adjacent_anagrams',[('words','list[str]')],'list[str]',['arrays','strings','sorting'],['Repeatedly delete a word when it is an anagram of the current preceding retained word.','Preserve the original spelling and order of retained words.','Two words are anagrams when their sorted character multisets match.'],[([['abba','baba','bbaa','cd','cd']],'The first three words share one signature and the last two another, leaving abba and cd.'),([['a','b','c']],'No adjacent words are anagrams, so all remain.')],[[x] for x in [['a'],['ab','ba'],['abba','baba','bbaa','cd','cd'],['a','b','c'],['abc','bca','cab'],['ab','ba','abc','cba'],['x','x','x'],['listen','silent','enlist','cat'],['aa','a'],['ab','bc','cb'],['z','zz','z'],['abc','def','fed','ghi'],['aab','aba','baa','abb'],['one','neo','eon','two']]],ANAGRAMS,[ANAGRAMS.replace('signature!=previous','signature==previous'),ANAGRAMS.replace('previous=signature','previous=word')],['Retains only adjacent anagrams rather than deleting them.','Stores the original word as the previous signature, so later anagram comparisons fail.'],anagrams_oracle,random_anagrams,['Canonicalize a word by sorting its characters.','Only compare with the signature of the last retained group, because all consecutive equal signatures collapse to their first word.','Append the word and update previous signature only when its signature differs.','Induction over the input maintains exactly the result after fully deleting anagram pairs in the processed prefix.'],'O(total characters log word length)','O(output)',3),
    2274: entry('maximum_non_special_floor_run',[('bottom','int'),('top','int'),('special','list[int]')],'int',['arrays','sorting'],['Rented floors are every integer from bottom through top inclusive.','Each distinct special floor breaks a consecutive non-special run.','Return the maximum number of consecutive non-special floors, allowing a run at either boundary.'],[([2,9,[4,6]],'The runs are floors 2-3, floor 5, and floors 7-9, so the maximum length is three.'),([1,3,[2]],'Either boundary run contains one non-special floor.')],[[b,t,s] for b,t,s in [(1,2,[1]),(1,2,[2]),(2,9,[4,6]),(1,3,[2]),(1,5,[1,5]),(10,20,[15]),(5,5,[5]),(1,10,[2,3,4]),(1,10,[7,8,9]),(3,8,[4,7]),(100,110,[101,105,109]),(1,4,[1,2,3,4]),(2,6,[3]),(7,12,[8,10])]],FLOORS,[FLOORS.replace('[bottom-1]','[bottom]'),FLOORS.replace('[top+1]','[top]')],['Omits the bottom boundary sentinel and undercounts the first run.','Omits the top boundary sentinel and undercounts the final run.'],floors_oracle,random_floors,['Sort the special floors and add virtual special sentinels just outside the rented range.','The non-special run between two adjacent special markers has length right-left-1.','Return the maximum gap across [bottom-1]+sorted(special)+[top+1].','Every ordinary floor belongs to exactly one gap between consecutive markers, including boundary gaps represented by the sentinels.'],'O(s log s)','O(s)',5),
    2275: entry('largest_positive_and_combination',[('candidates','list[int]')],'int',['arrays','bit manipulation','counting'],['Choose a nonempty subsequence of candidate values.','Its bitwise AND is positive exactly when all selected values share at least one set bit.','Return the largest possible number of selected elements.'],[([[16,17,71,62,12,24,14]],'Four candidates share a common set bit, and no bit appears in more values.'),([[8,8,8]],'All three values share the eight bit, so all can be selected.')],[[x] for x in [[1],[1,2],[3,3],[16,17,71,62,12,24,14],[8,8,8],[1,3,5,7],[2,4,8,16],[7,11,13],[0+1,1,1],[255,128,127],[5,10,15],[6,10,14,18],[32,48,64,80],[9,12,3,6]]],AND,[AND.replace('max(','min(',1),AND.replace('&1','==1')],['Returns the least-populated set bit instead of the most-populated one.','Compares the shifted value to one without masking, missing values with higher bits also set.'],and_oracle,random_and,['A positive AND needs at least one bit that is set in every chosen number.','For each bit position, count candidates containing that bit.','Return the maximum count over all relevant bit positions.','Any valid group contributes to one shared bit’s count, and choosing all values counted at one bit constructs a valid group of that size.'],'O(n*bits)','O(1)',6),
}
