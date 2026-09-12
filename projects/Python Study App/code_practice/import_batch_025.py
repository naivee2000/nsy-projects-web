"""Selected linked nodes, palindrome construction, BST proximity, and numeric DP."""
from collections import Counter, deque
from itertools import permutations, product
from math import isqrt

from .import_batch_003 import entry
from .import_batch_024 import flatten_tree, right_chain, tree_positions


def delete_node_oracle(args):
    payload = args[0]
    return payload["values"][:payload["index"]] + payload["values"][payload["index"] + 1:]


def palindrome_possible_oracle(args):
    return sum(count % 2 for count in Counter(args[0]).values()) <= 1


def palindrome_permutations_oracle(args):
    counts = Counter(args[0])
    odd = [character for character, count in counts.items() if count % 2]
    if len(odd) > 1:
        return []
    half = "".join(character * (counts[character] // 2) for character in sorted(counts))
    center = odd[0] if odd else ""
    return sorted({"".join(order) + center + "".join(reversed(order))
                   for order in permutations(half)})


def bst_values(values):
    return list(tree_positions(values).values())


def closest_value_oracle(args):
    values, target = args
    return min(bst_values(values), key=lambda value: (abs(value - target), value))


def closest_values_oracle(args):
    values, target, count = args
    return sorted(bst_values(values), key=lambda value: (abs(value - target), value))[:count]


SMALL = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def number_words_oracle(args):
    number = args[0]
    if number == 0:
        return "Zero"

    def say(value):
        if value < 20:
            return SMALL[value]
        if value < 100:
            return TENS[value // 10] + ((" " + SMALL[value % 10]) if value % 10 else "")
        if value < 1_000:
            return SMALL[value // 100] + " Hundred" + ((" " + say(value % 100)) if value % 100 else "")
        for unit, word in ((1_000_000_000, "Billion"), (1_000_000, "Million"), (1_000, "Thousand")):
            if value >= unit:
                return say(value // unit) + " " + word + ((" " + say(value % unit)) if value % unit else "")
        raise AssertionError("unreachable")

    return say(number)


def h_index_oracle(args):
    citations = args[0]
    return max(h for h in range(len(citations) + 1)
               if sum(citation >= h for citation in citations) >= h)


def paint_fence_oracle(args):
    posts, colors = args
    if posts == 1:
        return colors
    previous_two, previous_one = colors, colors * colors
    for _ in range(3, posts + 1):
        previous_two, previous_one = previous_one, (previous_one + previous_two) * (colors - 1)
    return previous_one


def perfect_squares_oracle(args):
    value = args[0]
    if isqrt(value) ** 2 == value:
        return 1
    reduced = value
    while reduced % 4 == 0:
        reduced //= 4
    if reduced % 8 == 7:
        return 4
    for first in range(1, isqrt(value) + 1):
        remaining = value - first * first
        if isqrt(remaining) ** 2 == remaining:
            return 2
    return 3


def random_delete_node(rng):
    values = [rng.randint(-1000, 1000) for _ in range(rng.randint(2, 25))]
    return [{"values": values, "index": rng.randrange(len(values) - 1)}]


def random_palindrome_text(rng, maximum=18):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, maximum)))]


def random_palindrome_permutations(rng):
    return random_palindrome_text(rng, 8)


def random_bst(rng, minimum=1, maximum=30):
    values = rng.sample(range(-1000, 1001), rng.randint(minimum, maximum))
    mapping = {}
    for value in values:
        path = ()
        while path in mapping:
            path += (0 if value < mapping[path] else 1,)
        mapping[path] = value
    return flatten_tree(mapping), values


def random_closest(rng):
    tree, _ = random_bst(rng)
    return [tree, rng.randint(-1200, 1200) + rng.choice((.1, .25, .75, .9))]


def random_closest_many(rng):
    tree, values = random_bst(rng)
    return [tree, rng.randint(-1200, 1200) + rng.choice((.1, .25, .75, .9)),
            rng.randint(1, len(values))]


def random_number_words(rng):
    return [rng.randint(0, 2**31 - 1)]


def random_h_index(rng):
    return [[rng.randint(0, 50) for _ in range(rng.randint(1, 30))]]


def random_sorted_h_index(rng):
    return [sorted(rng.randint(0, 50) for _ in range(rng.randint(1, 30)))]


def random_paint_fence(rng):
    while True:
        args = [rng.randint(1, 8), rng.randint(1, 5)]
        if paint_fence_oracle(args) <= 2**31 - 1:
            return args


def random_perfect_squares(rng):
    return [rng.randint(1, 500)]


DELETE_NODE = '''\
def delete_node(node):
    node.val = node.next.val
    node.next = node.next.next
'''


PALINDROME_POSSIBLE = '''\
def can_permute_palindrome(s):
    odd = set()
    for character in s:
        if character in odd:
            odd.remove(character)
        else:
            odd.add(character)
    return len(odd) <= 1
'''


PALINDROME_PERMUTATIONS = '''\
def generate_palindromes(s):
    counts = Counter(s)
    odd = [character for character, count in counts.items() if count % 2]
    if len(odd) > 1:
        return []
    center = odd[0] if odd else ""
    characters = sorted(counts)
    half_length = len(s) // 2
    answer = []
    path = []
    def build():
        if len(path) == half_length:
            left = "".join(path)
            answer.append(left + center + left[::-1])
            return
        for character in characters:
            if counts[character] >= 2:
                counts[character] -= 2
                path.append(character)
                build()
                path.pop()
                counts[character] += 2
    build()
    return answer
'''


CLOSEST_VALUE = '''\
def closest_bst_value(root, target):
    closest = root.val
    current = root
    while current:
        if (abs(current.val - target), current.val) < (abs(closest - target), closest):
            closest = current.val
        current = current.left if target < current.val else current.right
    return closest
'''


CLOSEST_VALUES = '''\
def closest_bst_values(root, target, k):
    predecessors = []
    successors = []
    current = root
    while current:
        if current.val <= target:
            predecessors.append(current)
            current = current.right
        else:
            successors.append(current)
            current = current.left

    def take_predecessor():
        node = predecessors.pop()
        value = node.val
        node = node.left
        while node:
            predecessors.append(node)
            node = node.right
        return value

    def take_successor():
        node = successors.pop()
        value = node.val
        node = node.right
        while node:
            successors.append(node)
            node = node.left
        return value

    answer = []
    for _ in range(k):
        if not successors or (predecessors and target - predecessors[-1].val <= successors[-1].val - target):
            answer.append(take_predecessor())
        else:
            answer.append(take_successor())
    return answer
'''


NUMBER_WORDS = '''\
def integer_to_english_words(num):
    if num == 0:
        return "Zero"
    below_twenty = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                      "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                      "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    def chunk(value):
        words = []
        if value >= 100:
            words.extend((below_twenty[value // 100], "Hundred"))
            value %= 100
        if value >= 20:
            words.append(tens[value // 10])
            value %= 10
        if value:
            words.append(below_twenty[value])
        return words
    words = []
    for size, name in ((1_000_000_000, "Billion"), (1_000_000, "Million"), (1_000, "Thousand"), (1, "")):
        value, num = divmod(num, size)
        if value:
            words.extend(chunk(value))
            if name:
                words.append(name)
    return " ".join(words)
'''


H_INDEX = '''\
def h_index(citations):
    size = len(citations)
    buckets = [0] * (size + 1)
    for citation in citations:
        buckets[min(citation, size)] += 1
    papers = 0
    for candidate in range(size, -1, -1):
        papers += buckets[candidate]
        if papers >= candidate:
            return candidate
'''


H_INDEX_SORTED = '''\
def h_index_sorted(citations):
    size = len(citations)
    left, right = 0, size
    while left < right:
        middle = (left + right) // 2
        if citations[middle] >= size - middle:
            right = middle
        else:
            left = middle + 1
    return size - left
'''


PAINT_FENCE = '''\
def paint_fence_ways(n, k):
    if n == 1:
        return k
    two_back, one_back = k, k * k
    for _ in range(3, n + 1):
        two_back, one_back = one_back, (one_back + two_back) * (k - 1)
    return one_back
'''


PERFECT_SQUARES = '''\
def minimum_perfect_squares(n):
    best = list(range(n + 1))
    for value in range(1, n + 1):
        root = 1
        while root * root <= value:
            best[value] = min(best[value], best[value - root * root] + 1)
            root += 1
    return best[n]
'''


long_delete_values = list(range(100_000))
large_h = [1000] * 5000
large_sorted_h = [0] * 99_000 + [1000] * 1000
palindrome_stress = "aaaabbbbccccdddd"


BATCH = {
    237: entry("delete_node", [("node", "ListNode")], "None", ["linked-lists", "in-place"],
        ["The source linked list contains 2–100000 nodes with integer values from -1000 through 1000. The selected node is identified by its zero-based position and is guaranteed not to be the tail.", "Your function receives only the actual selected ListNode. Delete its original value in place so the full list loses one node and preserves the order of every other value. Do not allocate replacement nodes."],
        [([{"values":[4,5,1,9],"index":1}], "The selected node holds 5. Copying its successor value 1 into it and bypassing that successor leaves the full list 4→1→9."), ([{"values":[4,5,1,9],"index":2}], "The selected node holds 1 and its successor is the tail 9, so the full list becomes 4→5→9.")],
        [[{"values":values,"index":index}] for values,index in (([1,2],0),([1,2,3],0),([1,2,3],1),([7,7],0),([1,1,1],1),([-1,0,1],0),([-1,0,1],1),([9,8,7,6],2),([5,4,3,2,1],0),([5,4,3,2,1],3),([0,0,1,0],1),([1000,-1000,5],1))],
        DELETE_NODE, [DELETE_NODE.replace("node.val = node.next.val\n", ""), DELETE_NODE.replace("node.next = node.next.next", "pass")],
        ["Bypasses the successor without copying its value, deleting the wrong list value.", "Copies the successor value but leaves the successor linked, so the list length does not decrease."], delete_node_oracle, random_delete_node,
        ["You cannot reach the node before the selected node, so ordinary predecessor deletion is unavailable.", "Make the selected node imitate its successor, then remove that successor from the chain.", "Assign node.val = node.next.val, then assign node.next = node.next.next.", "The non-tail guarantee makes node.next available. The selected object remains in the list while its original successor is the one unlinked."],
        "A singly linked node cannot find its predecessor. Instead, overwrite the selected node's value with its successor's value and bypass that successor. From the full list's perspective, the selected original value disappears and all other values retain their order. The judge supplies the actual selected object, observes the original head, and verifies the precise remaining node identities: the selected node stays, its successor leaves, and no other original node or value changes. The independent oracle removes the selected value from a plain list by index.", "O(1)", "O(1)", difficulty=3,
        stress=[([{"values":long_delete_values,"index":50_000}], long_delete_values[:50_000] + long_delete_values[50_001:])]),
    266: entry("can_permute_palindrome", [("s", "str")], "bool", ["strings", "hash-maps", "parity"],
        ["s contains 1–5000 lowercase English letters.", "Return whether some rearrangement of all characters can be a palindrome. Every character occurrence must be used."],
        [(["code"], "The counts of c, o, d, and e are all odd, so no single center can absorb them."), (["aab"], "Rearranging the characters as aba gives a palindrome; only b has odd frequency.")],
        [[s] for s in ("a","aa","ab","abc","aabb","aabbc","aaa","aaab","abcba","aabbccdd","aaaaabbbbb","zzxyyxzz")],
        PALINDROME_POSSIBLE, ['def can_permute_palindrome(s):\n    return all(count % 2 == 0 for count in Counter(s).values())\n', 'def can_permute_palindrome(s):\n    return s == s[::-1]\n'],
        ["Rejects every odd count, even though one odd character may occupy the center.", "Checks only the current order and misses strings whose characters can be rearranged into a palindrome."], palindrome_possible_oracle, random_palindrome_text,
        ["Palindrome positions outside the center occur in mirrored pairs.", "Therefore every character count must be even except possibly one center character.", "Toggle each character in an odd-count set while scanning; accept when its final size is at most one.", "A parity set stores only whether each count is currently odd, so it avoids retaining full counts."],
        "Every non-center palindrome character is paired with an equal character at the mirrored position. An even-length palindrome permits no odd frequency; an odd-length palindrome permits exactly one. Toggling membership in a set tracks count parity in one pass. The independent oracle counts every character and checks the number of odd totals.", "O(n)", "O(1) for the 26-letter alphabet", difficulty=3,
        stress=[(["a" * 4999 + "b"], False)]),
    267: entry("generate_palindromes", [("s", "str")], "list[str]", ["strings", "backtracking", "recursion"],
        ["s contains 1–16 lowercase English letters.", "Return every unique palindromic permutation that uses all characters, in any order. Return an empty list when none exists."],
        [(["aabb"], "The distinct half arrangements ab and ba mirror into abba and baab."), (["abc"], "Three characters have odd counts, so no complete palindromic permutation exists.")],
        [[s] for s in ("a","aa","ab","aaa","aab","abb","aabbc","aaaabb","aabbcc","aaaa","aaaabbbb","aabbccd")],
        PALINDROME_PERMUTATIONS, [PALINDROME_PERMUTATIONS.replace('answer.append(left + center + left[::-1])', 'answer.append(left)'), PALINDROME_PERMUTATIONS.replace('center = odd[0] if odd else ""', 'center = ""')],
        ["Returns only each chosen half instead of mirroring it into a full palindrome.", "Drops the required center character for every odd-length palindrome."], palindrome_permutations_oracle, random_palindrome_permutations,
        ["First apply the odd-frequency rule from Palindrome Permutation.", "Choose only the left half; the right half is forced as its reverse.", "Backtrack over characters with at least two remaining copies, consume two, recurse, then restore them.", "Choosing by character count rather than occurrence index prevents duplicate answers when letters repeat."],
        "At most one odd-frequency letter becomes the fixed center. Every other count contributes half its copies to the left side. Backtracking chooses a character pair at each depth; mirroring the completed half creates one full palindrome. Counts make identical occurrences indistinguishable, so each unique half is generated once. The independent oracle enumerates all half permutations and deduplicates them with a set.", "O(P·n) for P returned palindromes", "O(n) recursion excluding output", difficulty=5,
        stress=[([palindrome_stress], palindrome_permutations_oracle([palindrome_stress]))]),
    270: entry("closest_bst_value", [("root", "TreeNode"), ("target", "float")], "int", ["trees", "binary-search", "binary-search-trees"],
        ["root contains 1–10000 TreeNode objects with unique integer values from -10^9 through 10^9 and satisfies strict BST ordering. target is between -10^9 and 10^9.", "Return the tree value with the smallest absolute distance from target. When two values tie, return the smaller one."],
        [([[4,2,5,1,3],3.714286], "Four is about 0.286 away, closer than 3 at about 0.714."), ([[2,1,3],2.5], "Values 2 and 3 are equally distant from 2.5, so the smaller tied value 2 is required.")],
        [[tree,target] for tree,target in (([1],1.2),([1],-10.0),([2,1],1.1),([2,1],1.5),([2,1,3],2.9),([5,3,8,2,4,7,9],6.6),([0,-2,3,-4,-1,2,5],-1.5),([10,5,15,2,7,12,20],11.0),([10,5,15,2,7,12,20],100.0),([10,5,15,2,7,12,20],-100.0),([4,2,6,1,3,5,7],5.5),([8,4,12,2,6,10,14],9.49))],
        CLOSEST_VALUE, ['def closest_bst_value(root, target):\n    return round(target)\n', CLOSEST_VALUE.replace('(abs(current.val - target), current.val) < (abs(closest - target), closest)', 'abs(current.val - target) < abs(closest - target)')],
        ["Rounds the numeric target even when that integer is absent from the tree.", "Keeps the first value on a distance tie, which can return the larger tied value."], closest_value_oracle, random_closest,
        ["BST ordering lets you discard one whole side after examining a node.", "Track the best value seen while following the target-directed search path.", "Compare candidates by (absolute distance, value), then move left when target is smaller and right otherwise.", "The second tuple field implements the smaller-value tie rule without a separate equality branch."],
        "Every value that can improve the answer lies on the ordinary search path toward target. At each node, compare distance first and value second, then use BST ordering to choose the only subtree that can contain a closer value. The independent oracle flattens every compact tree value and takes the global minimum by that same stated pair, catching path and tie mistakes.", "O(h)", "O(1)", difficulty=3,
        stress=[([right_chain(10_000),8765.4],8765)]),
    272: entry("closest_bst_values", [("root", "TreeNode"), ("target", "float"), ("k", "int")], "list[int]", ["trees", "binary-search", "stacks", "binary-search-trees"],
        ["root contains 1–10000 TreeNode objects with unique integer values from -10^9 through 10^9 and satisfies strict BST ordering. target is between -10^9 and 10^9; 1≤k≤the node count.", "Return exactly the k closest values in any order. Rank distance ties by the smaller value."],
        [([[4,2,5,1,3],3.714286,2], "Values 4 and 3 have the two smallest distances from the target."), ([[2,1,3],2.5,1], "Two and 3 tie, so the smaller value 2 occupies the single available result position.")],
        [[tree,target,k] for tree,target,k in (([1],1.0,1),([2,1],1.4,2),([2,1,3],2.5,2),([5,3,8,2,4,7,9],6.6,3),([0,-2,3,-4,-1,2,5],-1.5,4),([10,5,15,2,7,12,20],11.0,1),([10,5,15,2,7,12,20],11.0,7),([4,2,6,1,3,5,7],5.5,3),([8,4,12,2,6,10,14],9.49,4),([3,1,5,None,2,4,6],3.0,2),([100,50,150,25,75,125,175],0.0,2),([100,50,150,25,75,125,175],1000.0,3))],
        CLOSEST_VALUES, ['def closest_bst_values(root, target, k):\n    values = []\n    stack = [root]\n    while stack:\n        node = stack.pop(); values.append(node.val)\n        if node.left: stack.append(node.left)\n        if node.right: stack.append(node.right)\n    return sorted(values)[:k]\n', CLOSEST_VALUES.replace('target - predecessors[-1].val <= successors[-1].val - target', 'target - predecessors[-1].val >= successors[-1].val - target')],
        ["Returns the k numerically smallest values rather than the values nearest target.", "Chooses the farther stack at each step because the distance comparison is reversed."], closest_values_oracle, random_closest_many,
        ["Split the BST around target into predecessor and successor traversal frontiers.", "One stack yields decreasing values at or below target; the other yields increasing values above target.", "Initialize both root paths. Repeatedly compare the two stack tops, pop the closer side, and push the appropriate opposite-child spine.", "Taking the predecessor on equal distance enforces the smaller-value tie rule. Each selected node advances only one frontier."],
        "Two iterative inorder frontiers avoid scanning the whole tree. The predecessor stack contains the path to the largest unused value at or below target; after popping, its left child's right spine supplies the next one. The successor stack is symmetric. Comparing their top distances produces one answer per step, with predecessor winning ties. Initialization takes O(h), and k pops take O(k+h) total amortized traversal. The independent oracle globally sorts every node by distance and value.", "O(h+k)", "O(h)", difficulty=8,
        stress=[([right_chain(10_000),8765.4,50], closest_values_oracle([right_chain(10_000),8765.4,50]))]),
    273: entry("integer_to_english_words", [("num", "int")], "str", ["strings", "recursion", "math"],
        ["num is an integer from 0 through 2^31-1.", "Return its US English words with single spaces and title-case number words. Do not use 'and' or hyphens; zero is exactly 'Zero'."],
        [([123], "Split 123 into one hundred and the remainder twenty-three, yielding 'One Hundred Twenty Three' without the conjunction 'and'."), ([12345], "The thousand group is twelve and the final group is 345, yielding 'Twelve Thousand Three Hundred Forty Five'.")],
        [[n] for n in (0,1,10,19,20,21,99,100,101,110,1000,1001,1010,1100,1_000_000,1_000_001,1_010_010,1_000_000_000,2_147_483_647)],
        NUMBER_WORDS, [NUMBER_WORDS.replace('if num == 0:\n        return "Zero"', 'if num == 0:\n        return ""'), NUMBER_WORDS.replace('return " ".join(words)', 'return " and ".join(words)')],
        ["Returns an empty string instead of the required word Zero.", "Joins every token with 'and', violating the specified output grammar and spacing."], number_words_oracle, random_number_words,
        ["Process the number in three-digit groups because scale words change at thousand, million, and billion.", "Write a helper for one group: optional hundreds, then either a value below 20 or a tens word plus ones.", "From billion down through units, divide out each group; spell nonzero groups and append their scale name.", "Skip zero groups completely so no extra scale word or space appears. Handle zero before the loop."],
        "English number names repeat the same grammar within each three-digit group. A helper spells hundreds, teens, tens, and ones. The outer loop extracts billion, million, thousand, and unit groups from left to right, omitting empty groups and joining tokens once. The independent oracle recursively selects the largest applicable scale and spells the quotient and remainder, rather than iterating fixed chunks.", "O(log num)", "O(1) beyond output", difficulty=8),
    274: entry("h_index", [("citations", "list[int]")], "int", ["arrays", "counting-sort", "sorting"],
        ["citations contains 1–5000 integers from 0 through 1000.", "Return the largest h for which at least h papers each have at least h citations. Papers beyond those h may have any citation count."],
        [([[3,0,6,1,5]], "Three papers have at least 3 citations, while fewer than four papers have at least 4, so h=3."), ([[1,3,1]], "Only one paper has at least two citations, but all three conditions for h=1 are met, so h=1.")],
        [[values] for values in ([0],[1],[1000],[0,0],[1,1],[2,2],[0,1,2],[3,3,3],[4,4,0,0],[10,8,5,4,3],[0,0,4,4],[6,5,3,1,0],[2,1,2,1,2],[1000,0,0,0,0])],
        H_INDEX, ['def h_index(citations):\n    return sum(value > 0 for value in citations)\n', 'def h_index(citations):\n    values = sorted(citations, reverse=True)\n    return sum(value > index + 1 for index, value in enumerate(values))\n'],
        ["Counts every cited paper even when many do not reach the required rank.", "Uses a strict citation comparison and counts qualifying positions instead of finding the largest feasible prefix."], h_index_oracle, random_h_index,
        ["Citation values above the paper count are equivalent for h-index purposes.", "Bucket each citation at min(citation,n), then scan candidate h values downward.", "Accumulate the number of papers in buckets h through n; the first h with accumulated papers≥h is maximal.", "This avoids sorting and handles one enormous citation count without mistaking it for many papers."],
        "An h-index cannot exceed the number of papers, so every larger citation count can share one final bucket. Scanning buckets from n downward maintains exactly how many papers have at least the current candidate. The first feasible candidate is the maximum. The independent oracle directly tries every h and recounts qualifying papers.", "O(n)", "O(n)", difficulty=5,
        stress=[([large_h],1000)]),
    275: entry("h_index_sorted", [("citations", "list[int]")], "int", ["arrays", "binary-search"],
        ["citations contains 1–100000 integers from 0 through 1000 in nondecreasing order.", "Return the largest h for which at least h papers have at least h citations. Use logarithmic time."],
        [([[0,1,3,5,6]], "At index 2, three papers remain and citation 3 reaches that count; no earlier feasible index gives a larger h."), ([[0,0,0]], "No paper has even one citation, so the h-index is 0.")],
        [[values] for values in ([0],[1],[1000],[0,0],[1,1],[2,2],[0,1,2],[3,3,3],[0,0,4,4],[0,1,1,1,10],[0,0,1,5,6],[1,2,1000],[0,4,4,4,4],[0,0,0,1000])],
        H_INDEX_SORTED, [H_INDEX_SORTED.replace('>= size - middle', '> size - middle'), H_INDEX_SORTED.replace('return size - left', 'return left')],
        ["Uses strict greater-than and misses the defining equality boundary.", "Returns the boundary index instead of the number of papers in its suffix."], h_index_oracle, random_sorted_h_index,
        ["At index i, exactly n-i papers have citations at least citations[i].", "Search for the first index where citations[i]≥n-i; feasibility stays true to its right.", "Use a half-open [left,right) binary search. Move right to mid when feasible, otherwise move left past mid.", "After convergence, n-left is the maximum feasible suffix length; if no index works, left=n and the answer is zero."],
        "Sorted citations make the predicate citations[i]≥n-i monotone: once a suffix has enough citations per paper, every later shorter suffix also does. Binary search finds the first feasible index, and its suffix length is the h-index. The independent oracle ignores sortedness and directly checks every candidate against all citations.", "O(log n)", "O(1)", difficulty=5,
        stress=[([large_sorted_h],1000)]),
    276: entry("paint_fence_ways", [("n", "int"), ("k", "int")], "int", ["dynamic-programming", "combinatorics"],
        ["1≤n≤50 and 1≤k≤1000. The number of valid paintings fits a signed 32-bit integer.", "Each of n fence posts receives one of k colors. Return the number of assignments with no three consecutive posts sharing one color."],
        [([3,2], "There are 2^3=8 colorings of three posts; the two all-equal colorings are invalid, leaving 6."), ([1,3], "One post may use any of the three colors, so there are 3 valid paintings.")],
        [[n,k] for n,k in ((1,1),(2,1),(3,1),(4,1),(2,2),(4,2),(5,2),(2,3),(3,3),(4,3),(5,3),(3,10),(3,1000))],
        PAINT_FENCE, ['def paint_fence_ways(n, k):\n    return k * (k - 1) ** (n - 1)\n', 'def paint_fence_ways(n, k):\n    return k ** n\n'],
        ["Forbids equal adjacent colors, even though runs of exactly two are allowed.", "Counts assignments containing runs of three or more equal colors."], paint_fence_oracle, random_paint_fence,
        ["Classify a valid prefix by whether its last two colors are equal or different.", "Appending a different color to either state gives k-1 choices; appending the same color is allowed only after a different ending.", "The combined recurrence is ways[i]=(ways[i-1]+ways[i-2])·(k-1), with bases k and k².", "When k=1, only lengths one and two are valid; the recurrence naturally gives zero afterward."],
        "A valid painting ending with two equal colors must have had a different color immediately before that pair. Separating same-ending and different-ending states produces the combined recurrence (previous one plus previous two) times k-1. Two scalar totals are enough. The independent checker uses the same counting definition, while exhaustive regression enumerates every small color assignment to verify the recurrence separately.", "O(n)", "O(1)", difficulty=5,
        stress=[([50,1],0)]),
    279: entry("minimum_perfect_squares", [("n", "int")], "int", ["dynamic-programming", "math"],
        ["n is an integer from 1 through 10000.", "Return the minimum number of positive perfect squares whose sum is n. A square value may be reused."],
        [([12], "Twelve is 4+4+4, so three squares suffice; it cannot be expressed as one or two squares."), ([13], "Thirteen is 9+4, so the minimum is two squares.")],
        [[n] for n in (1,2,3,4,5,7,8,9,10,16,18,23,43,99,100,9999,10000)],
        PERFECT_SQUARES, ['def minimum_perfect_squares(n):\n    from math import isqrt\n    count = 0\n    while n:\n        square = isqrt(n) ** 2\n        n -= square\n        count += 1\n    return count\n', 'def minimum_perfect_squares(n):\n    from math import isqrt\n    return isqrt(n)\n'],
        ["Greedily subtracts the largest square; for 12 it uses 9+1+1+1 instead of 4+4+4.", "Returns the square-root magnitude rather than the minimum number of square summands."], perfect_squares_oracle, random_perfect_squares,
        ["Treat every smaller total as a reusable subproblem.", "For each value, try every square no larger than it and extend the best result for the remainder.", "Initialize best[x]=x using x copies of 1. Replace it with min(best[x-square]+1) over square roots.", "The table grows from 0 upward, so every remainder has already been solved when it is needed."],
        "Dynamic programming defines best[x] as the fewest squares summing to x. Every optimal representation ends with some square q², leaving an optimal representation of x-q². Trying every possible final square yields the minimum. The independent oracle uses the four-square theorem and a two-square search instead of the DP recurrence.", "O(n√n)", "O(n)", difficulty=5),
}


BATCH[237]["params"] = [("node", "ListNode", "listnode_ref")]
BATCH[237]["result_mode"] = "mutated_argument"
BATCH[237]["mutated_parameter"] = 0
BATCH[237]["node_policy"] = "delete_referenced_list_node"
BATCH[237]["sample_contract_adapter"] = {
    "source_sample": "Input head = [4,5,1,9], node = 5 → Output [4,1,9].",
    "arguments": [{"values": [4,5,1,9], "index": 1}],
    "expected": [4,1,9],
    "reason": "The callable receives only node; the source head is retained as judge context and node=5 is selected at index 1.",
}
for problem_id in (270, 272):
    BATCH[problem_id]["params"][0] = ("root", "TreeNode", "treenode")
BATCH[267]["comparator"] = "unordered"
BATCH[272]["comparator"] = "unordered"
BATCH[272]["prerequisites"] = ["binary-search", "trees"]
BATCH[273]["prerequisites"] = ["strings", "recursion"]
