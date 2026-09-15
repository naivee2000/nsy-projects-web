"""Bitwise partitions, empty rectangles, endpoint sums, and word restoration."""
from itertools import combinations

from .import_batch_055 import entry


def minimum_or_oracle(args):
    nums, limit = args; answer = None
    for cuts in range(1 << (len(nums) - 1)):
        segments = cuts.bit_count() + 1
        if len(nums) - segments > limit:
            continue
        result = 0; running = nums[0]
        for index in range(len(nums) - 1):
            if cuts >> index & 1:
                result |= running; running = nums[index + 1]
            else:
                running &= nums[index + 1]
        result |= running
        answer = result if answer is None else min(answer, result)
    return answer


def random_minimum_or(rng):
    size = rng.randint(1, 10)
    return [[rng.randint(0, 255) for _ in range(size)], rng.randint(0, size - 1)]


def people_oracle(args):
    points = args[0]; answer = 0
    for alice, bob in combinations(points, 2):
        for upper, lower in ((alice, bob), (bob, alice)):
            if upper[0] > lower[0] or upper[1] < lower[1]:
                continue
            blocked = any(point != upper and point != lower
                          and upper[0] <= point[0] <= lower[0]
                          and lower[1] <= point[1] <= upper[1] for point in points)
            answer += not blocked
    return answer


def random_people(rng):
    universe = [(x, y) for x in range(-5, 6) for y in range(-5, 6)]
    selected = rng.sample(universe, rng.randint(2, 10))
    return [[[x, y] for x, y in selected]]


def good_sum_oracle(args):
    nums, difference = args; answer = None
    for left in range(len(nums)):
        total = 0
        for right in range(left, len(nums)):
            total += nums[right]
            if abs(nums[left] - nums[right]) == difference:
                answer = total if answer is None else max(answer, total)
    return 0 if answer is None else answer


def random_good_sum(rng):
    return [[rng.randint(-15, 15) for _ in range(rng.randint(2, 22))], rng.randint(1, 12)]


def revert_oracle(args):
    word, width = args; seconds = 1
    while seconds * width < len(word):
        removed = seconds * width
        if word[removed:] == word[:len(word) - removed]:
            return seconds
        seconds += 1
    return seconds


def random_revert(rng):
    word = ''.join(rng.choice('abcd') for _ in range(rng.randint(1, 28)))
    return [word, rng.randint(1, len(word))]


MINIMUM_OR = '''def minimum_or_after_and_merges(nums,k):
    answer=forbidden=0
    for bit in range(29,-1,-1):
        candidate=forbidden|(1<<bit);segments=0;running=candidate
        for value in nums:
            running&=value
            if running==0:segments+=1;running=candidate
        if len(nums)-segments<=k:forbidden=candidate
        else:answer|=1<<bit
    return answer
'''


PEOPLE = '''def count_empty_upper_left_pairs(points):
    points=sorted(points,key=lambda point:(point[0],-point[1]));answer=0
    for index,(_,upper_y) in enumerate(points):
        highest_below=float('-inf')
        for _,lower_y in points[index+1:]:
            if highest_below<lower_y<=upper_y:
                highest_below=lower_y;answer+=1
    return answer
'''


GOOD_SUM = '''def maximum_endpoint_difference_subarray_sum(nums,k):
    prefix=0;minimum_prefix={};answer=None
    for value in nums:
        minimum_prefix[value]=min(minimum_prefix.get(value,float('inf')),prefix)
        prefix+=value
        for endpoint in (value-k,value+k):
            if endpoint in minimum_prefix:
                candidate=prefix-minimum_prefix[endpoint]
                answer=candidate if answer is None else max(answer,candidate)
    return 0 if answer is None else answer
'''


REVERT = '''def minimum_word_revert_time(word,k):
    for removed in range(k,len(word),k):
        if word[removed:]==word[:-removed]:return removed//k
    return (len(word)+k-1)//k
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


PEOPLE_CASES = [[[list(point) for point in points]] for points in [
    [(0,0),(1,0)],[(0,1),(1,0)],[(0,0),(1,1)],[(0,2),(1,1),(2,0)],
    [(0,2),(1,0),(2,1)],[(0,2),(0,1),(0,0)],[(0,0),(1,0),(2,0)],
    [(1,3),(1,1),(3,1)],[(0,3),(1,2),(2,1),(3,0)],
    [(0,3),(1,1),(2,2),(3,0)],[(2,5),(4,4),(6,2)],
    [(-2,2),(-1,0),(0,1),(2,-1)],[(0,5),(2,5),(2,3),(4,3)],
    [(5,1),(1,5),(3,3),(2,2),(4,4)]]]


BATCH = {
3022: entry('minimum_or_after_and_merges',[('nums','list[int]'),('k','int')],'int',['bit manipulation','greedy','arrays'],['nums is nonempty with values below 2^30, and 0≤k<length.','One operation replaces two adjacent values by their bitwise AND; use at most k operations.','Return the minimum possible bitwise OR of the remaining segment values.'],[([[3,5,3,2,7],2],'Merging the first pair and the final pair can leave [1,3,2], whose OR is three, the minimum.'),([[7,3,15,14,2,8],4],'Four merges can leave segment AND values two and zero, whose OR is two.')],[[n,k] for n,k in [([0],0),([7],0),([1,2],0),([1,2],1),([7,7],1),([3,5,3],1),([15,7,3],2),([8,4,2,1],3),([1,3,7,15],2),([10,7,10,3,9,14,9,4],1),([0,1,2,3],2),([31,30,28,24],2),([5,10,12,3,6],3),([255,127,63,31,15],4)]],MINIMUM_OR,[MINIMUM_OR.replace('len(nums)-segments<=k','len(nums)-segments<k'),MINIMUM_OR.replace('running=candidate\n        if len(nums)','running=0\n        if len(nums)')],['Requires fewer than k merges and rejects solutions using exactly the allowed number.','Resets the next segment mask to zero, making every following element appear to clear all forbidden bits.'],minimum_or_oracle,random_minimum_or,lesson('Choosing whether an answer bit can be zero is a partition-feasibility question under a mask of forbidden bits.','Build forbidden bits high-to-low; greedily form the maximum number of segments whose AND clears every forbidden bit.','For each candidate mask, scan segment ANDs and cut whenever masked AND becomes zero; accept when n-segments≤k.','Extra merges can join cleared segments without restoring forbidden bits, and the maximum greedy segment count minimizes required merges, so bitwise feasibility is exact.'),'O(30n)','O(1)',8),
3025: entry('count_empty_upper_left_pairs',[('points','list[list[int]]')],'int',['geometry','sorting','enumeration'],['points contains at least two distinct integer coordinates.','Alice at A must satisfy A.x≤B.x and A.y≥B.y for Bob, allowing a zero-width or zero-height fence.','Count ordered role pairs whose closed rectangle contains no third point.'],[([[[1,1],[2,2],[3,3]]],'Every left point is below each right point, so no Alice/Bob orientation is valid.'),([[[6,2],[4,4],[2,6]]],'The two adjacent descending pairs are empty; the outer rectangle contains the middle point.')],PEOPLE_CASES,PEOPLE,[PEOPLE.replace('(point[0],-point[1])','(point[0],point[1])'),PEOPLE.replace('highest_below<lower_y','highest_below<=lower_y')],['Sorts equal-x points bottom-first, causing incorrect vertical fence visibility.','Allows a second point at the same lower boundary height even though the first lies on the new fence.'],people_oracle,random_people,lesson('After sorting x ascending and y descending, Bob candidates for one Alice are valid exactly when they set a new highest y not exceeding Alice.','Scan later points and count record-high y values bounded by Alice’s y.','Sort (x,-y); for each i keep max_y=-∞ and count y when max_y<y≤alice_y, then update max_y.','Any intervening y at least Bob’s lies inside the closed rectangle and blocks it; record highs are precisely the unblocked candidates.'),'O(n^2)','O(n)',5),
3026: entry('maximum_endpoint_difference_subarray_sum',[('nums','list[int]'),('k','int')],'int',['prefix sums','hash maps','arrays'],['nums has at least two signed integers and k is positive.','A subarray is good when the absolute difference between its first and last values is exactly k.','Return the maximum good-subarray sum, including negative maxima, or zero if none exists.'],[([[1,2,3,4,5,6],1],'Among adjacent endpoint pairs differing by one, [5,6] has the largest sum eleven.'),([[-1,3,2,4,5],3],'The good subarray [2,4,5] has sum eleven, exceeding the other valid choice.')],[[n,k] for n,k in [([1,1],1),([1,2],1),([2,1],1),([-1,-2,-3,-4],2),([5,-10,6],1),([1,-5,2,3],2),([3,-2,4,-1,5],2),([10,-20,9],1),([0,5,0],5),([4,1,7,2],3),([-5,0,5],10),([2,2,4,2],2),([8,-1,-1,5],3),([1,10,-5,9,2],8)]],GOOD_SUM,[GOOD_SUM.replace('(value-k,value+k)','(value-k,)'),GOOD_SUM.replace('min(minimum_prefix.get(value,float(\'inf\')),prefix)','max(minimum_prefix.get(value,float(\'-inf\')),prefix)')],['Checks only endpoints where the first value is k smaller, missing the opposite orientation.','Stores the largest earlier prefix instead of the smallest, losing higher-sum subarrays.'],good_sum_oracle,random_good_sum,lesson('For a subarray ending at value v, its first value must be v-k or v+k, and the smallest earlier prefix maximizes the sum.','Track the minimum prefix immediately before every possible first value.','Before adding v, minimize prefix_by_value[v]; add v; test prefix-prefix_by_value[v±k].','Every good subarray is considered at its right endpoint, and choosing the minimum compatible starting prefix yields the maximum sum for that endpoint pair value.'),'O(n)','O(n)',5),
3027: entry('count_empty_upper_left_pairs_large',[('points','list[list[int]]')],'int',['geometry','sorting','enumeration'],['points contains up to 1,000 distinct signed coordinates.','Alice at A must satisfy A.x≤B.x and A.y≥B.y; boundary points also block the fence.','Count valid role pairs in O(n²) time.'],[([[[1,1],[2,2],[3,3]]],'No point is upper-left of a point to its right, so the answer is zero.'),([[[6,2],[4,4],[2,6]]],'Only the two consecutive descending pairs avoid enclosing the third point.')],PEOPLE_CASES,PEOPLE.replace('count_empty_upper_left_pairs','count_empty_upper_left_pairs_large'),[PEOPLE.replace('count_empty_upper_left_pairs','count_empty_upper_left_pairs_large').replace('(point[0],-point[1])','(point[0],point[1])'),PEOPLE.replace('count_empty_upper_left_pairs','count_empty_upper_left_pairs_large').replace('lower_y<=upper_y','lower_y<upper_y')],['Uses the wrong tie order for equal x coordinates.','Rejects valid horizontal fences where Alice and Bob have equal y.'],people_oracle,random_people,lesson('Sorted x order reduces rectangle emptiness to visibility among later y coordinates.','Sort equal x by descending y, then count bounded record-high later y values for every Alice.','For each sorted point, scan right; when max_seen_y<y≤alice_y count the pair and raise max_seen_y.','A non-record candidate has a prior point on or inside its fence, while every bounded record candidate has no such blocker.'),'O(n^2)','O(n)',8),
3029: entry('minimum_word_revert_time',[('word','str'),('k','int')],'int',['strings','prefix matching','simulation'],['word is a nonempty lowercase string and 1≤k≤length.','Each second removes the first k current characters and appends any k chosen characters.','Return the minimum positive seconds after which the original word can be restored.'],[(['abacaba',3],'After two removals, suffix a matches the original prefix a; the remaining six characters can be appended to restore the word.'),(['abacaba',4],'After one removal, suffix aba equals the original prefix aba, so the appended four characters can finish restoration immediately.')],[[w,k] for w,k in [('a',1),('aa',1),('ab',1),('aaaa',2),('abab',2),('abcabc',3),('abcabc',2),('abcbabcd',2),('aaaaa',2),('abcdef',4),('abaaba',2),('xyzxyzx',3),('leetcode',3),('aabaacaabaa',4)]],REVERT,[REVERT.replace('word[removed:]==word[:-removed]','word[removed:]==word[removed:]'),REVERT.replace('(len(word)+k-1)//k','len(word)//k')],['Compares the remaining suffix with itself, incorrectly accepting the first second.','Uses floor division when no overlap works, undercounting the final partial removal.'],revert_oracle,random_revert,lesson('After t removals, only the original suffix beginning at t*k is forced to remain; appended characters can fill everything else.','Check whether that forced suffix equals the original prefix of the same length at each multiple of k.','For removed=k,2k,...<n, return removed/k on word[removed:]==word[:-removed]; otherwise return ceil(n/k).','The equality is necessary for untouched characters and sufficient because all removed positions may be replaced arbitrarily; once all originals are removed restoration is always possible.'),'O(n^2/k)','O(n)',5),
}
