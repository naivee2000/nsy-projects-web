"""Final reviewed group of workbook batch 111."""

from collections import deque

from .import_batch_055 import entry


MOD = 1_000_000_007


def palindrome_oracle(arguments):
    text = arguments[0]
    found = set()
    for left in range(len(text)):
        for middle in range(left + 1, len(text)):
            for right in range(middle + 1, len(text)):
                if text[left] == text[right]:
                    found.add(text[left] + text[middle] + text[right])
    return len(found)


def painting_oracle(arguments):
    rows, columns = arguments
    states = []
    for encoded in range(3 ** rows):
        value, column = encoded, []
        for _ in range(rows):
            column.append(value % 3)
            value //= 3
        if all(column[index] != column[index - 1] for index in range(1, rows)):
            states.append(tuple(column))
    counts = {state: 1 for state in states}
    for _ in range(1, columns):
        following = {}
        for state in states:
            following[state] = sum(amount for previous, amount in counts.items()
                                   if all(a != b for a, b in zip(previous, state))) % MOD
        counts = following
    return sum(counts.values()) % MOD


def _tree_from_level(values):
    if not values:
        return None
    root = [values[0], None, None]
    queue, index = deque([root]), 1
    while queue and index < len(values):
        node = queue.popleft()
        for side in (1, 2):
            if index < len(values) and values[index] is not None:
                node[side] = [values[index], None, None]
                queue.append(node[side])
            index += 1
    return root


def _tree_to_level(root):
    if root is None:
        return []
    output, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            output.append(None)
        else:
            output.append(node[0])
            queue.extend((node[1], node[2]))
    while output and output[-1] is None:
        output.pop()
    return output


def merge_bsts_oracle(arguments):
    forest = [_tree_from_level(values) for values in arguments[0]]
    roots = {tree[0]: tree for tree in forest}

    def expand(node, lower, upper, used):
        if node is None:
            return None, used
        value = node[0]
        if not lower < value < upper:
            raise ValueError
        current = node
        if node[1] is None and node[2] is None and value in roots and value not in used:
            current = roots[value]
            used = used | {value}
        left, used = expand(current[1], lower, value, used)
        right, used = expand(current[2], value, upper, used)
        return [value, left, right], used

    answers = []
    for value, root in roots.items():
        try:
            merged, used = expand(root, float("-inf"), float("inf"), {value})
            if len(used) == len(roots):
                answers.append(_tree_to_level(merged))
        except ValueError:
            pass
    return answers[0] if len(answers) == 1 else []


def decomposable_oracle(arguments):
    text = arguments[0]
    index = pairs = 0
    while index < len(text):
        end = index + 1
        while end < len(text) and text[end] == text[index]:
            end += 1
        remainder = (end - index) % 3
        if remainder == 1:
            return False
        pairs += remainder == 2
        index = end
    return pairs == 1


def typing_oracle(arguments):
    text, broken = arguments
    unusable = set(broken)
    return sum(all(char not in unusable for char in word) for word in text.split())


def random_palindrome(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(3, 13)))]


def random_painting(rng):
    return [rng.randint(1, 4), rng.randint(1, 6)]


def random_merge_bsts(rng):
    length = rng.randint(1, 7)
    values = sorted(rng.sample(range(1, 50), length))
    if rng.random() < .65:
        forest = [[values[index], values[index + 1]] for index in range(length - 1)] + [[values[-1]]]
    else:
        forest = [[values[index], values[index + 1]] for index in range(length - 1)] + [[values[-1]]]
        if length > 1:
            forest[rng.randrange(length - 1)][1] = rng.choice(values)
        else:
            forest.append([values[0] + 1])
    rng.shuffle(forest)
    return [forest]


def random_decomposable(rng):
    return ["".join(rng.choice("0123") for _ in range(rng.randint(2, 30)))]


def random_typing(rng):
    letters = "abcdef"
    words = ["".join(rng.choice(letters) for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(1, 10))]
    broken = "".join(rng.sample(letters, rng.randint(0, len(letters))))
    return [" ".join(words), broken]


PALINDROME = '''\
def count_length_three_palindromes(s):
    first = [-1] * 26
    last = [-1] * 26
    for index, char in enumerate(s):
        code = ord(char) - 97
        if first[code] == -1:
            first[code] = index
        last[code] = index
    answer = 0
    for code in range(26):
        if first[code] < last[code]:
            answer += len(set(s[first[code] + 1:last[code]]))
    return answer
'''

PAINTING = '''\
def count_three_color_grid_paintings(m, n):
    mod = 1_000_000_007
    states = []
    for encoded in range(3 ** m):
        value, column = encoded, []
        for _ in range(m):
            column.append(value % 3)
            value //= 3
        if all(column[row] != column[row - 1] for row in range(1, m)):
            states.append(tuple(column))
    compatible = {state: [other for other in states if all(a != b for a, b in zip(state, other))]
                  for state in states}
    ways = {state: 1 for state in states}
    for _ in range(1, n):
        ways = {state: sum(ways[previous] for previous in compatible[state]) % mod for state in states}
    return sum(ways.values()) % mod
'''

MERGE_BSTS = '''\
def merge_small_bsts(trees):
    roots = {tree.val: tree for tree in trees}
    children = set()
    for tree in trees:
        if tree.left:
            children.add(tree.left.val)
        if tree.right:
            children.add(tree.right.val)
    candidates = [tree for tree in trees if tree.val not in children]
    if len(candidates) != 1:
        return None
    root = candidates[0]
    used = {root.val}

    def validate(node, lower, upper):
        if node is None:
            return True
        if not lower < node.val < upper:
            return False
        if node.left is None and node.right is None and node.val in roots and node.val not in used:
            graft = roots[node.val]
            used.add(node.val)
            node.left, node.right = graft.left, graft.right
        return validate(node.left, lower, node.val) and validate(node.right, node.val, upper)

    return root if validate(root, float("-inf"), float("inf")) and len(used) == len(trees) else None
'''

DECOMPOSABLE = '''\
def valid_decomposable_string(s):
    pairs = 0
    index = 0
    while index < len(s):
        end = index + 1
        while end < len(s) and s[end] == s[index]:
            end += 1
        remainder = (end - index) % 3
        if remainder == 1:
            return False
        if remainder == 2:
            pairs += 1
        index = end
    return pairs == 1
'''

TYPING = '''\
def count_typable_words(text, broken_letters):
    broken = set(broken_letters)
    return sum(not broken.intersection(word) for word in text.split())
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    1930: entry(
        "count_length_three_palindromes", [("s", "str")], "int", ["strings", "hash maps"],
        ["s has 3 through 100000 lowercase English letters.",
         "Count distinct subsequence strings, not distinct index triples.",
         "Every counted palindrome has the form x-y-x."],
        [(["aabca"], "The distinct palindromes are aaa, aba, and aca."),
         (["adc"], "No character can serve as both ends of a length-three subsequence.")],
        [[s] for s in ["aaa", "bbcbaba", "abca", "aaaaa", "abcba", "abacada", "xyzxyz",
                       "ccdcc", "abcdefa", "aabaa", "cabac", "zzxyzz", "abababab", "qwertyq"]],
        PALINDROME,
        [PALINDROME.replace("answer += len(set(s[first[code] + 1:last[code]]))", "answer += last[code] - first[code] - 1"),
         '''def count_length_three_palindromes(s):\n    return len({s[i:i+3] for i in range(len(s)-2) if s[i] == s[i+2]})\n'''],
        ["Counts middle positions instead of distinct middle characters.", "Checks substrings only, missing noncontiguous subsequences."],
        palindrome_oracle, random_palindrome,
        lesson("Fixing the outer character reduces the question to which middle characters occur between its first and last positions.",
               "Record the first and last position of each letter, then count distinct letters strictly between them.",
               "For each alphabet letter with two occurrences, add the size of the set inside its widest span.",
               "Any valid triple lies inside that widest span; conversely every distinct character inside it creates exactly one distinct palindrome for those ends."),
        "O(n)", "O(1)", 5),
    1931: entry(
        "count_three_color_grid_paintings", [("m", "int"), ("n", "int")], "int", ["dynamic programming", "bitmasking"],
        ["1 <= m <= 5 and 1 <= n <= 1000.", "Use exactly three available colors.",
         "Horizontally and vertically adjacent cells must have different colors.", "Return the count modulo 1000000007."],
        [([1, 1], "A single cell can use any of the three colors."),
         ([1, 2], "Choose one of three colors, then either of the other two, giving six paintings.")],
        [[m, n] for m, n in [(2,1),(2,2),(2,3),(3,1),(3,2),(3,3),(4,2),(5,2),(1,10),(2,10),(3,7),(4,5),(5,4),(5,1000)]],
        PAINTING,
        [PAINTING.replace("all(a != b for a, b in zip(state, other))", "True"),
         PAINTING.replace("range(3 ** m)", "range(2 ** m)")],
        ["Treats all individually valid adjacent columns as compatible even when horizontal neighbors match.",
         "Enumerates only two colors, omitting valid paintings that use the third."],
        painting_oracle, random_painting,
        lesson("The narrow height makes an entire column a compact dynamic-programming state.",
               "Enumerate vertically valid color columns and connect pairs that differ in every row.",
               "Initialize one way per state; repeat n-1 times, summing compatible predecessor counts modulo the required modulus.",
               "Every legal grid has one legal state per column and one compatibility transition between neighbors, so the DP counts every grid exactly once."),
        "O(n*3^(2m))", "O(3^(2m))", 8),
    1932: entry(
        "merge_small_bsts", [("trees", "list[TreeNode]")], "TreeNode", ["trees", "binary search trees", "depth-first search"],
        ["trees contains 1 through 50000 distinct BST roots.", "Each input tree has at most three nodes and no grandchildren.",
         "Root values are unique; leaf values may name roots of other trees.",
         "Graft a matching root at a leaf and return one valid BST using every input tree, or None if impossible."],
        [([[[2,1],[3,2,5],[5,4]]], "Graft the tree rooted at 2 into leaf 2, then the tree rooted at 5 into leaf 5; the result is [3,2,5,1,null,4]."),
         ([[[5,3,8],[3,2,6]]], "Grafting root 3 would place 6 in the left subtree of 5, violating the BST bounds, so no merge exists.")],
        [[forest] for forest in [
            [[1]], [[2,1],[1]], [[1,None,2],[2]], [[4,2,6],[2,1,3],[6,5,7]],
            [[3,2,5],[2,1],[5,4,6]], [[2,1],[3,2]], [[2,None,3],[1],[3]],
            [[10,5,15],[5,2,7],[15,12,20]], [[8,4,12],[4,2,6],[12,10,14],[2,1,3]],
            [[2,3],[3,1]], [[5,3,8],[3,2,6]], [[2,1,3],[1,None,4]],
            [[3,1,5],[1],[5],[7]], [[1,None,2],[2,None,3],[3,None,4],[4]],
            [[4,2,6],[2,1,3],[6,5,7],[8,None,9],[9,8]]]],
        MERGE_BSTS,
        [MERGE_BSTS.replace("and len(used) == len(trees)", ""),
         MERGE_BSTS.replace("if not lower < node.val < upper:\n            return False", "if False:\n            return False")],
        ["Returns a locally valid component without requiring every supplied tree to be merged.",
         "Grafts matching roots without enforcing the global BST bounds inherited from ancestors."],
        merge_bsts_oracle, random_merge_bsts,
        lesson("A leaf value can be a join point only when it equals another tree's unique root value.",
               "Find the only root never named as a child, graft unused matching roots during a bounded BST traversal, and count consumed roots.",
               "Traverse with lower/upper limits; at a leaf, attach the matching root's children once; accept only valid bounds and all roots consumed.",
               "The unreferenced root is the only possible final root. Bounds certify the global BST property, while the consumed-root count prevents disconnected leftovers."),
        "O(n)", "O(n)", 8),
    1933: entry(
        "valid_decomposable_string", [("s", "str")], "bool", ["strings", "greedy"],
        ["s has 2 through 1000 digits.", "Partition equal consecutive digits into groups of length three, except exactly one group of length two.",
         "No group may mix different digits, and the entire string must be used."],
        [(["000111000"], "All three runs have length three, so the required single length-two group is missing."),
         (["0001111122"], "The runs split as 000, 111+11, and 22, which creates two length-two groups and is invalid.")],
        [[s] for s in ["00","000","00000","00000000","00111","00011","001111","11100022","11222",
                       "00011122","00000111","00111000","012","00111222"]],
        DECOMPOSABLE,
        [DECOMPOSABLE.replace("return pairs == 1", "return pairs <= 1"),
         DECOMPOSABLE.replace("if remainder == 1:\n            return False", "if False:\n            return False")],
        ["Allows zero length-two groups although the contract requires exactly one.", "Accepts runs whose length leaves an unusable remainder of one."],
        decomposable_oracle, random_decomposable,
        lesson("Only maximal runs of one digit matter because groups cannot cross a digit change.",
               "Inspect each run length modulo three: remainder one is impossible; remainder two contributes the unique pair.",
               "Scan runs, reject remainder one, count remainder-two runs, and accept exactly one.",
               "A run of length 3q uses triples; length 3q+2 uses triples plus one pair; length 3q+1 cannot be partitioned. Exactly one pair completes the global rule."),
        "O(n)", "O(1)", 3),
    1935: entry(
        "count_typable_words", [("text", "str"), ("broken_letters", "str")], "int", ["strings", "hash maps"],
        ["text contains 1 through 1000 lowercase letters and single spaces between words.",
         "broken_letters contains distinct lowercase letters and may be empty.",
         "A word is typable only when none of its letters is broken."],
        [(["hello world", "ad"], "hello avoids both broken letters, but world contains d, so exactly one word is typable."),
         (["leet code", "lt"], "Both words contain at least one broken letter, so the answer is zero.")],
        [[text, broken] for text, broken in [
            ("hello world","ad"),("leet code","lt"),("a",""),("a","a"),("abc def ghi","x"),
            ("abc def ghi","adg"),("one two three","e"),("quick brown fox","qz"),("aaaa bbbb","a"),
            ("cat dog","cd"),("algorithm practice","m"),("binary search","xy"),("recursion tree","rt"),("zoo","o")]],
        TYPING,
        ['''def count_typable_words(text, broken_letters):\n    broken = set(broken_letters)\n    return sum(all(char in broken for char in word) for word in text.split())\n''',
         '''def count_typable_words(text, broken_letters):\n    broken = set(broken_letters)\n    return sum(word[0] not in broken for word in text.split())\n'''],
        ["Counts words that contain a broken letter instead of words that avoid all broken letters.",
         "Checks only the first character and misses broken letters later in a word."],
        typing_oracle, random_typing,
        lesson("A word fails as soon as any of its characters belongs to the broken-letter set.",
               "Build a set once, then test each whitespace-separated word for an empty intersection.",
               "Split the sentence; count words for which no character is in broken.",
               "The predicate examines every character of each word, so it accepts exactly the words constructible with working keys."),
        "O(n)", "O(b)", 3),
}

BATCH[1932]["params"] = [("trees", "list[TreeNode]", "treenode_list")]
BATCH[1932]["adapter"] = "treenode"
BATCH[1932]["node_policy"] = "values"
