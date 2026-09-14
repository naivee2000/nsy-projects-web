"""Third slice of workbook batch 125."""

from collections import deque

from .import_batch_055 import entry


def distinct_oracle(args):
    nums, limit, divisor = args
    found = set()
    for left in range(len(nums)):
        divisible = 0
        for right in range(left, len(nums)):
            divisible += nums[right] % divisor == 0
            if divisible <= limit:
                found.add(tuple(nums[left:right + 1]))
    return len(found)


def random_distinct(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(1, 15))], rng.randint(0, 5), rng.randint(1, 8)]


def appeal_oracle(args):
    text = args[0]
    return sum(len(set(text[left:right])) for left in range(len(text)) for right in range(left + 1, len(text) + 1))


def random_appeal(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 35)))]


def monotone_cost(values, increasing=True):
    choices = range(min(values), max(values) + 1)
    if not increasing:
        choices = reversed(list(choices))
    costs = [0] * len(list(range(min(values), max(values) + 1)))
    ordered = list(range(min(values), max(values) + 1))
    if not increasing:
        ordered.reverse()
    for value in values:
        next_costs = []
        best = 10**18
        for index, target in enumerate(ordered):
            best = min(best, costs[index])
            next_costs.append(best + abs(value - target))
        costs = next_costs
    return min(costs)


def conversion_oracle(args):
    nums = args[0]
    return min(monotone_cost(nums, True), monotone_cost(nums, False))


def random_conversion(rng):
    return [[rng.randint(0, 12) for _ in range(rng.randint(1, 10))]]


def good_oracle(args):
    text = args[0]
    matches = [text[index:index + 3] for index in range(len(text) - 2)
               if len(set(text[index:index + 3])) == 1]
    return max(matches, default="")


def random_good(rng):
    return ["".join(str(rng.randrange(10)) for _ in range(rng.randint(3, 30)))]


def tree_arrays(values):
    left = [None] * len(values); right = [None] * len(values)
    queue = deque([0]); index = 1
    while queue and index < len(values):
        parent = queue.popleft()
        if index < len(values) and values[index] is not None:
            left[parent] = index; queue.append(index)
        index += 1
        if index < len(values) and values[index] is not None:
            right[parent] = index; queue.append(index)
        index += 1
    return left, right


def average_tree_oracle(args):
    values = args[0]
    left, right = tree_arrays(values)
    answer = 0
    def visit(node):
        nonlocal answer
        if node is None:
            return 0, 0
        left_sum, left_count = visit(left[node]); right_sum, right_count = visit(right[node])
        total = left_sum + right_sum + values[node]; count = left_count + right_count + 1
        answer += values[node] == total // count
        return total, count
    visit(0)
    return answer


def random_average_tree(rng):
    length = rng.randint(1, 20)
    values = [rng.randint(0, 20)]
    available = 1
    while len(values) < length and available:
        value = rng.randint(0, 20) if rng.random() < .8 else None
        values.append(value)
        if value is not None:
            available += 1
        if len(values) % 2 == 1:
            available -= 1
    while values and values[-1] is None:
        values.pop()
    return [values]


DISTINCT = '''\
def count_distinct_limited_divisible_subarrays(nums,k,p):
    found=set()
    for left in range(len(nums)):
        divisible=0;current=[]
        for right in range(left,len(nums)):
            current.append(nums[right]);divisible+=nums[right]%p==0
            if divisible>k:break
            found.add(tuple(current))
    return len(found)
'''

APPEAL = '''\
def total_substring_appeal(s):
    last={};ending=answer=0
    for index,char in enumerate(s):
        ending+=index-last.get(char,-1)
        last[char]=index;answer+=ending
    return answer
'''

CONVERSION = '''\
def minimum_monotone_conversion_cost(nums):
    import heapq
    def increasing(values):
        heap=[];cost=0
        for value in values:
            heapq.heappush(heap,-value)
            if -heap[0]>value:
                cost+=-heapq.heappop(heap)-value
                heapq.heappush(heap,-value)
        return cost
    return min(increasing(nums),increasing(reversed(nums)))
'''

GOOD = '''\
def largest_three_equal_digit_substring(num):
    answer=''
    for index in range(len(num)-2):
        piece=num[index:index+3]
        if piece[0]==piece[1]==piece[2]:answer=max(answer,piece)
    return answer
'''

AVERAGE_TREE = '''\
def count_subtree_average_nodes(root):
    answer=0
    def visit(node):
        nonlocal answer
        if node is None:return 0,0
        left_sum,left_count=visit(node.left);right_sum,right_count=visit(node.right)
        total=left_sum+right_sum+node.val;count=left_count+right_count+1
        answer+=node.val==total//count
        return total,count
    visit(root)
    return answer
'''


BATCH = {
    2261: entry('count_distinct_limited_divisible_subarrays',[('nums','list[int]'),('k','int'),('p','int')],'int',['arrays','hash sets','enumeration'],['Consider every nonempty contiguous subarray.','A subarray is allowed when at most k of its elements are divisible by p.','Equal value sequences count once even when they occur at different positions.'],[([[2,3,3,2,2],2,2],'Eleven distinct value sequences contain at most two even elements.'),([[1,2,3,4],4,1],'Every element is divisible by one, but k permits all ten subarrays and their sequences are distinct.')],[[n,k,p] for n,k,p in [([1],0,2),([2],0,2),([2,3,3,2,2],2,2),([1,2,3,4],4,1),([1,1,1],0,2),([2,2,2],1,2),([1,2,1,2],1,2),([3,6,9],2,3),([5,7,11],0,2),([4,5,4],2,4),([1,2,3,1],0,5),([10,20,30],3,10),([2,3,5,7,2],1,2),([6,1,6,1],0,3)]],DISTINCT,[DISTINCT.replace('divisible>k','divisible>=k'),DISTINCT.replace('found.add(tuple(current))','found.add((left,right))')],['Rejects subarrays containing exactly k divisible elements.','Counts index ranges rather than deduplicating equal value sequences.'],distinct_oracle,random_distinct,['Enumerate a start index and extend its subarray until the divisible-element limit is exceeded.','Store each valid value sequence as an immutable tuple in a set.','For each left, append nums[right], update the divisible count, break above k, otherwise add tuple(current).','Every valid subarray is visited; invalid longer extensions cannot recover, and set identity implements the required value-based distinctness.'],'O(n^2)','O(n^3) stored elements worst case',6),
    2262: entry('total_substring_appeal',[('s','str')],'int',['strings','dynamic programming'],['A substring’s appeal is its number of distinct characters.','Count all nonempty contiguous substrings.','Return the sum of their appeals, counting the same text at different positions separately.'],[(['abbca'],'The appeals of all fifteen substrings sum to twenty-eight.'),(['code'],'All characters differ, so the total appeal is twenty.')],[[x] for x in ['a','aa','ab','abbca','code','aaaa','abcabc','aba','mississippi','leetcode','ababab','xyzzy','abcde','aabbaa']],APPEAL,[APPEAL.replace("last.get(char,-1)","last.get(char,0)"),APPEAL.replace('answer+=ending','answer+=len(last)')],['Treats an unseen character as last seen at zero and loses its first-position contribution.','Adds only the current prefix distinct count instead of appeal across all substrings ending here.'],appeal_oracle,random_appeal,['Track the total appeal of all substrings ending at the current index.','A character contributes to suffixes starting after its previous occurrence: index-last_index new contributions.','Update ending by that contribution, store the index, and add ending to the answer.','Each distinct character’s contribution is counted once in every substring from its last occurrence boundary through the current end.'],'O(n)','O(alphabet)',8),
    2263: entry('minimum_monotone_conversion_cost',[('nums','list[int]')],'int',['arrays','greedy','heaps'],['One operation increments or decrements one element by one.','The final array may be either non-decreasing or non-increasing.','Return the minimum total number of unit changes; values need not remain within the original range during operations.'],[([[3,2,4,5,0]],'The cheapest monotone adjustment uses four unit changes.'),([[2,2,3,1]],'Changing the final one to three costs two and makes the array non-decreasing.')],[[x] for x in [[1],[1,2],[2,1],[3,2,4,5,0],[2,2,3,1],[1,1,1],[3,1,2],[5,4,3,2],[1,3,2,4],[10,0,10],[0,10,0],[4,1,7,2],[2,5,3,6,1],[9,3,8,2,7]]],CONVERSION,[CONVERSION.replace('return min(increasing(nums),increasing(reversed(nums)))','return increasing(nums)'),CONVERSION.replace('cost+=-heapq.heappop(heap)-value','cost+=-heapq.heappop(heap)')],['Considers only non-decreasing targets and misses cheaper non-increasing adjustments.','Adds the removed value rather than only its difference from the current value.'],conversion_oracle,random_conversion,['Solve the non-decreasing direction with a max-heap, then solve non-increasing by reversing the input.','When the greatest prior adjusted value exceeds the current value, lower that maximum to the current value and add the difference.','Push each value; on a violation pop the heap maximum, add maximum-current, and push current again.','The heap maintains an optimal multiset of adjusted prefix values; replacing its largest violation is the minimum local repair and the standard isotonic L1 exchange argument makes it globally optimal.'],'O(n log n)','O(n)',8),
    2264: entry('largest_three_equal_digit_substring',[('num','str')],'str',['strings'],['Inspect every contiguous substring of length three.','A candidate is valid only when all three characters are the same digit.','Return the largest valid three-character string, preserving 000, or an empty string if none exists.'],[(['6777133339'],'The valid groups are 777 and 333, so 777 is larger.'),(['2300019'],'The only valid group is 000, which must be returned with all three zeros.')],[[x] for x in ['000','111','123','6777133339','2300019','9990','0999','101010','222333','55555','9876665','444123444','1000','121777121']],GOOD,[GOOD.replace('range(len(num)-2)','range(len(num)-3)'),GOOD.replace('max(answer,piece)','min(answer,piece)')],['Skips the final possible three-character window.','Chooses the smallest candidate and can incorrectly keep the empty initial value.'],good_oracle,random_good,['Scan every length-three window.','A chained equality identifies windows containing one repeated digit.','For each valid piece, update the lexicographically largest string.','All valid results have equal length, so string order matches digit value, and exhaustive windows ensure none is missed.'],'O(n)','O(1)',3),
    2265: entry('count_subtree_average_nodes',[('root','TreeNode')],'int',['trees','recursion','postorder traversal'],['For every node, its subtree includes the node and all descendants.','Compute floor(subtree value sum / subtree node count).','Count nodes whose own value equals that floored average.'],[([[4,8,5,0,1,None,6]],'Five nodes equal the floored average of their respective subtrees.'),([[1]],'A leaf is the only member of its subtree, so it always matches.')],[[x] for x in [[1],[0],[4,8,5,0,1,None,6],[1,2,3],[5,5,5],[10,0,20],[2,1,None],[2,None,1],[7,3,9,1,5,8,10],[1,0,2,0,0,2,2],[6,4,8,2,None,7,9],[3,1,5,None,2,4,6],[9,9,None,9],[5,1,9,None,3,7,11]]],AVERAGE_TREE,[AVERAGE_TREE.replace('total//count','total/count'),AVERAGE_TREE.replace('answer+=','answer-=')],['Uses an exact fractional average instead of flooring before comparison.','Subtracts matching nodes and returns a negative count.'],average_tree_oracle,random_average_tree,['Postorder traversal can return both subtree sum and subtree size.','Combine the two child pairs with the current node, then compare node.val with total//count.','Increment a shared answer on each match and return (total,count) to the parent.','Postorder computes exact aggregate data for every subtree once, so each node’s required predicate is evaluated exactly once.'],'O(n)','O(tree height)',6),
}

BATCH[2265]['params'][0] = ('root','TreeNode','treenode')
