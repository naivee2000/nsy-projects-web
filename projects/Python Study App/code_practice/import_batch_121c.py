"""Third slice of workbook batch 121."""

from collections import Counter
from functools import lru_cache

from .import_batch_055 import entry


def frequency_oracle(args):
    s = args[0]
    found = set()
    for left in range(len(s)):
        for right in range(left + 1, len(s) + 1):
            counts = Counter(s[left:right])
            if len(set(counts.values())) == 1:
                found.add(s[left:right])
    return len(found)


def random_frequency(rng):
    return ["".join(rng.choice("01234") for _ in range(rng.randint(1, 18)))]


def operations_oracle(args):
    first, second = args
    count = 0
    while first and second:
        if first >= second:
            first -= second
        else:
            second -= first
        count += 1
    return count


def random_operations(rng):
    return [rng.randint(0, 1000), rng.randint(0, 1000)]


def alternating_oracle(args):
    nums = args[0]
    values = set(nums)
    values.add(max(values, default=0) + 1)
    answer = len(nums)
    for even in values:
        for odd in values:
            if even != odd:
                answer = min(answer, sum(value != (even if index % 2 == 0 else odd) for index, value in enumerate(nums)))
    return answer


def random_alternating(rng):
    return [[rng.randint(1, 7) for _ in range(rng.randint(1, 25))]]


def beans_oracle(args):
    beans = args[0]
    return min(sum(value if value < target else value - target for value in beans) for target in {0, *beans})


def random_beans(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 20))]]


def and_oracle(args):
    nums, slots = args

    @lru_cache(None)
    def search(index, capacities):
        if index == len(nums):
            return 0
        best = 0
        for slot in range(slots):
            if capacities[slot] < 2:
                updated = list(capacities)
                updated[slot] += 1
                best = max(best, (nums[index] & (slot + 1)) + search(index + 1, tuple(updated)))
        return best

    return search(0, (0,) * slots)


def random_and(rng):
    slots = rng.randint(1, 4)
    return [[rng.randint(1, 15) for _ in range(rng.randint(1, 2 * slots))], slots]


FREQUENCY = '''\
def count_equal_frequency_substrings(s):
    root={};answer=0
    for left in range(len(s)):
        counts=[0]*10;node=root
        for right in range(left,len(s)):
            digit=ord(s[right])-48;counts[digit]+=1
            node=node.setdefault(digit,{})
            positive=[count for count in counts if count]
            if min(positive)==max(positive) and '_valid' not in node:
                node['_valid']={};answer+=1
    return answer
'''

OPERATIONS = '''\
def subtraction_operations_to_zero(num1,num2):
    operations=0
    while num1 and num2:
        if num1>=num2:
            operations+=num1//num2;num1%=num2
        else:
            operations+=num2//num1;num2%=num1
    return operations
'''

ALTERNATING = '''\
def minimum_alternating_changes(nums):
    if len(nums)<2:return 0
    from collections import Counter
    even=Counter(nums[::2]).most_common(2)+[(None,0),(None,0)]
    odd=Counter(nums[1::2]).most_common(2)+[(None,0),(None,0)]
    if even[0][0]!=odd[0][0]:kept=even[0][1]+odd[0][1]
    else:kept=max(even[0][1]+odd[1][1],even[1][1]+odd[0][1])
    return len(nums)-kept
'''

BEANS = '''\
def minimum_magic_bean_removal(beans):
    beans=sorted(beans);total=sum(beans);best=total
    for index,value in enumerate(beans):
        best=min(best,total-value*(len(beans)-index))
    return best
'''

AND_SUM = '''\
def maximum_slot_and_sum(nums,num_slots):
    from functools import lru_cache
    powers=[3**slot for slot in range(num_slots)]
    @lru_cache(None)
    def search(index,state):
        if index==len(nums):return 0
        best=0
        for slot,power in enumerate(powers,1):
            if state//power%3<2:
                best=max(best,(nums[index]&slot)+search(index+1,state+power))
        return best
    return search(0,0)
'''


BATCH = {
    2168: entry('count_equal_frequency_substrings',[('s','str')],'int',['strings','counting','tries'],['s contains decimal digits and substrings are contiguous and nonempty.','A substring qualifies when every digit present in it occurs the same number of times.','Count distinct substring contents, not distinct positions or frequency vectors.'],[(['1212'],'The distinct valid substrings are 1, 2, 12, 21, and 1212, so return 5.'),(['12321'],'Single digits, balanced multi-digit windows, and repeated-content deduplication produce nine distinct valid substrings.')],[[x] for x in ['0','00','01','10','11','012','1212','12321','0011','0101','1122','123123','000111','102201','012340']],FREQUENCY,[FREQUENCY.replace("node=node.setdefault(digit,{})","node=root.setdefault(counts[digit],{})"),FREQUENCY.replace('min(positive)==max(positive)','len(positive)==1')],['Uses only a frequency value as identity, merging different substring contents.','Accepts only substrings containing one distinct digit.'],frequency_oracle,random_frequency,['Equal frequencies can be checked from ten counters, but distinct content also needs exact identity.','Build a digit trie for all substrings; the path uniquely identifies content without copying every substring.','For each start extend rightward, update one count and one trie edge, and mark an unmarked node when all positive counts match.','Each distinct substring maps to exactly one trie node. The marker counts it once, and the counter condition is exactly the equal-frequency rule.'],'O(n^2)','O(n^2)',6),
    2169: entry('subtraction_operations_to_zero',[('num1','int'),('num2','int')],'int',['math','euclidean algorithm'],['Both inputs are nonnegative.','Each operation subtracts the smaller positive value from the larger, or num2 from num1 when equal.','Stop when either value reaches zero and return the number of individual subtractions.'],[([2,3],'The states are (2,3), (2,1), (1,1), and (0,1), requiring three operations.'),([10,10],'One subtraction changes the pair to (0,10), so return 1.')],[[a,b] for a,b in [(0,0),(0,5),(5,0),(1,1),(1,5),(5,1),(2,3),(3,2),(10,10),(8,3),(100,7),(21,13),(999,1),(48,18),(17,6)]],OPERATIONS,[OPERATIONS.replace('operations+=num1//num2','operations+=1'),OPERATIONS.replace('operations+=num2//num1','operations+=1')],['Counts one operation for a whole quotient-sized batch when num1 is larger.','Counts one operation for a whole quotient-sized batch when num2 is larger.'],operations_oracle,random_operations,['Repeated subtraction is the Euclidean algorithm with a count.','A quotient tells how many consecutive subtractions occur before the larger remainder becomes smaller.','While both are positive, add larger//smaller and replace the larger with its remainder.','Division groups exactly the same repeated subtractions without skipping the final subtraction that can produce zero.'],'O(log max(num1,num2))','O(1)',3),
    2170: entry('minimum_alternating_changes',[('nums','list[int]')],'int',['arrays','hash maps','greedy'],['All even indices must share one value and all odd indices must share another.','The chosen even and odd values must differ.','One operation may change any element to any positive integer.'],[([[3,1,3,2,4,3]],'Keeping 3 on even indices and 1 or 2 on odd indices requires three changes.'),([[1,2,2,2,2]],'Choose 1 for even positions and 2 for odd positions, changing the two later even values.')],[[x] for x in [[1],[1,1],[1,2],[1,2,1],[1,1,1],[1,2,2,2,2],[3,1,3,2,4,3],[1,2,1,2,1,2],[2,2,2,2],[1,2,3,4],[5,5,6,6,5,5],[1,3,1,3,2],[4,1,4,2,4,3],[7,6,7,6,5],[1,1,2,2,3,3]]],ALTERNATING,[ALTERNATING.replace("if even[0][0]!=odd[0][0]","if True"),ALTERNATING.replace('nums[1::2]','nums[::2]')],['Keeps both most-common values even when they are equal, violating alternation.','Counts the even positions twice and ignores odd-position frequencies.'],alternating_oracle,random_alternating,['Only the retained counts for one even value and one different odd value matter.','The optimal choice uses one of the two most common values on each parity.','Take both top frequencies when their values differ; otherwise try replacing either side with its runner-up.','If the top values conflict, any value below second place cannot improve the retained total compared with that side’s runner-up.'],'O(n)','O(n)',6),
    2171: entry('minimum_magic_bean_removal',[('beans','list[int]')],'int',['arrays','greedy','sorting'],['Each bag starts with a positive bean count.','After removals, every nonempty bag must contain the same target count; bags may be emptied.','Return the minimum total number of removed beans.'],[([[4,1,6,5]],'Keeping target four empties the one-bean bag and trims six and five, removing 4 beans total.'),([[2,10,3,2]],'Keeping target two removes six from the ten-bean bag and one from the three-bean bag, totaling 7.')],[[x] for x in [[1],[1,1],[1,2],[2,2,2],[1,2,3],[4,1,6,5],[2,10,3,2],[5,1,1,1],[10,10,1],[3,6,9,12],[100,1,50],[7,7,7,1],[1,2,2,2,20],[9,4,9,4,9],[2,3,5,7,11]]],BEANS,[BEANS.replace('len(beans)-index','index'),BEANS.replace('total-value*(len(beans)-index)','value*(len(beans)-index)')],['Keeps the wrong side of the sorted list when evaluating a target.','Returns the beans kept rather than the beans removed.'],beans_oracle,random_beans,['An optimal positive target equals the original count of some surviving bag.','Sort counts; for target beans[i], empty earlier bags and trim all later bags to that target.','Compute total - value*(n-index) for every sorted index and take the minimum.','Between existing counts, increasing the target only reduces removals until reaching the next count, so an optimum occurs at a listed value.'],'O(n log n)','O(n)',5),
    2172: entry('maximum_slot_and_sum',[('nums','list[int]'),('num_slots','int')],'int',['bit manipulation','bitmask dynamic programming'],['Slots are numbered 1 through num_slots and each holds at most two numbers.','Every number must be assigned to one slot.','Maximize the sum of nums[i] bitwise-AND its assigned slot number.'],[([[1,2,3,4,5,6],3],'A capacity-respecting assignment can collect AND contributions totaling 9, which is optimal.'),([[1,3,10,4,7,1],9],'With enough slots, selecting useful slot bits for each number produces the optimum 24.')],[[a,s] for a,s in [([1],1),([2],1),([1,2],1),([1,2],2),([1,2,3],2),([1,2,3,4],2),([1,2,3,4,5,6],3),([7,7],4),([8,4,2,1],4),([3,6,9],3),([15,15,15,15],2),([1,3,10,4,7,1],9),([5,2,8,6,3],3),([0,1,2,3],2)]],AND_SUM,[AND_SUM.replace('%3<2','%3<1'),AND_SUM.replace('nums[index]&slot','nums[index]|slot')],['Allows only one number per slot instead of two.','Uses bitwise OR instead of bitwise AND for each contribution.'],and_oracle,random_and,['Each slot occupancy has three states: zero, one, or two numbers.','Encode all occupancies as a base-three integer and memoize by number index and state.','Try every slot whose ternary digit is below two, add the AND contribution, and recurse after increasing that digit.','The recurrence enumerates every capacity-valid assignment exactly by its sequence of slot choices and selects the greatest total.'],'O(n*3^slots*slots)','O(n*3^slots)',8),
}
