"""Ordinary Hard matching/array problems and greedy reachability contracts."""
from collections import deque
from fnmatch import fnmatchcase
import re

from .import_batch_003 import entry


def regex_oracle(args):
    # Python's independent regular-expression engine has exactly the required
    # semantics on the restricted lowercase/dot/star grammar used here.
    return re.fullmatch(args[1], args[0]) is not None


def wildcard_oracle(args):
    # With lowercase literals, ? and * only, no fnmatch bracket/path extensions
    # apply. fnmatchcase preserves the required case-sensitive whole-string match.
    return fnmatchcase(args[0], args[1])


def parentheses_oracle(args):
    text, = args
    longest = 0
    for start in range(len(text)):
        balance = 0
        for end in range(start, len(text)):
            balance += 1 if text[end] == "(" else -1
            if balance < 0:
                break
            if balance == 0:
                longest = max(longest, end - start + 1)
    return longest


def missing_oracle(args):
    present = set(args[0])
    return next(i for i in range(1, len(args[0]) + 2) if i not in present)


def jump_distances(nums):
    distances = {0: 0}
    queue = deque([0])
    while queue:
        index = queue.popleft()
        for destination in range(index + 1, min(len(nums), index + nums[index] + 1)):
            if destination not in distances:
                distances[destination] = distances[index] + 1
                queue.append(destination)
    return distances


def minimum_jumps_oracle(args):
    return jump_distances(args[0])[len(args[0]) - 1]


def reachable_oracle(args):
    return len(args[0]) - 1 in jump_distances(args[0])


def random_regex(rng):
    text = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
    pattern = "".join(rng.choice("ab.") + ("*" if rng.random() < .5 else "") for _ in range(rng.randint(1, 8)))
    return [text, pattern]


def random_wildcard(rng):
    return ["".join(rng.choice("ab") for _ in range(rng.randint(0, 12))),
            "".join(rng.choice("ab?*") for _ in range(rng.randint(0, 12)))]


def random_parentheses(rng):
    return ["".join(rng.choice("()") for _ in range(rng.randint(0, 30)))]


def random_missing(rng):
    if rng.random() < .5:
        n = rng.randint(1, 40)
        values = list(range(1, n + 2))
        values.remove(rng.randint(1, n + 1))
        rng.shuffle(values)
        return [values]
    return [[rng.choice([rng.randint(-20, 40), -(2**31), 2**31 - 1]) for _ in range(rng.randint(1, 40))]]


def random_reachable(rng):
    return [[rng.randrange(8) for _ in range(rng.randint(1, 30))]]


def random_jumps(rng):
    while True:
        args = random_reachable(rng)
        if reachable_oracle(args):
            return args


REGEX = '''\
def regex_match(s, p):
    previous = [False] * (len(p) + 1)
    previous[0] = True
    for j in range(2, len(p) + 1):
        if p[j - 1] == "*":
            previous[j] = previous[j - 2]
    for char in s:
        current = [False] * (len(p) + 1)
        for j in range(1, len(p) + 1):
            if p[j - 1] == "*":
                matches = p[j - 2] == "." or p[j - 2] == char
                current[j] = current[j - 2] or (matches and previous[j])
            else:
                matches = p[j - 1] == "." or p[j - 1] == char
                current[j] = matches and previous[j - 1]
        previous = current
    return previous[-1]
'''
WILDCARD = '''\
def wildcard_match(s, p):
    previous = [False] * (len(p) + 1)
    previous[0] = True
    for j in range(1, len(p) + 1):
        previous[j] = p[j - 1] == "*" and previous[j - 1]
    for char in s:
        current = [False] * (len(p) + 1)
        for j in range(1, len(p) + 1):
            if p[j - 1] == "*":
                current[j] = current[j - 1] or previous[j]
            else:
                matches = p[j - 1] == "?" or p[j - 1] == char
                current[j] = matches and previous[j - 1]
        previous = current
    return previous[-1]
'''
PARENTHESES = '''\
def longest_valid_parentheses(s):
    stack, longest = [-1], 0
    for index, char in enumerate(s):
        if char == "(":
            stack.append(index)
        else:
            stack.pop()
            if not stack:
                stack.append(index)
            else:
                longest = max(longest, index - stack[-1])
    return longest
'''
MISSING = '''\
def first_missing_positive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            destination = nums[i] - 1
            nums[i], nums[destination] = nums[destination], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
'''
JUMPS = '''\
def minimum_jumps(nums):
    jumps, end, farthest = 0, 0, 0
    for index in range(len(nums) - 1):
        farthest = max(farthest, index + nums[index])
        if index == end:
            jumps += 1
            end = farthest
    return jumps
'''
REACHABLE = '''\
def can_jump(nums):
    farthest = 0
    for index, reach in enumerate(nums):
        if index > farthest:
            return False
        farthest = max(farthest, index + reach)
        if farthest >= len(nums) - 1:
            return True
    return True
'''

BATCH = {
    10: entry("regex_match", [("s","str"),("p","str")], "bool", ["strings","dynamic-programming","recursion"],
        ["s and p each have length 1–20. s contains lowercase English letters.", "p contains lowercase letters, '.' (one arbitrary character), and '*' (zero or more of the preceding atom).", "Every star follows a valid non-star atom. Match the entire string, not a substring."],
        [(["aa","a"],"The pattern consumes only one a, so it does not cover the entire two-character input."),
         (["aab","c*a*b"],"Use zero copies of c, two copies of a, then b; the full string matches.")],
        [["a","a"],["a","b"],["a","."],["aa","a*"],["ab",".*"],["ab",".*c"],["ab","ac*b"],["aaa","a*a"],
         ["mississippi","mis*is*p*."],["b","a*b"],["a","ab*"],["abc","a.c"]],
        REGEX, [REGEX.replace('current[j - 2] or (matches and previous[j])','matches and previous[j]'),
                REGEX.replace('p[j - 2] == "." or ', '').replace('p[j - 1] == "." or ', '')],
        ["Requires a starred atom to consume something, missing zero-repetition matches.", "Treats dot as a literal rather than as a one-character wildcard."], regex_oracle, random_regex,
        ["A star belongs to the atom before it; this differs from an independent wildcard star.","Define whether each text prefix matches each pattern prefix.","For x*, either skip both pattern characters or consume a matching text character while retaining x*. An ordinary atom consumes one from both sides.","Initialize empty-text matches through chains of starred atoms, then return the full-prefix state."],
        "Use prefix DP. An ordinary letter or dot needs the preceding text/pattern prefixes to match and then consumes one character. A starred atom has two choices: zero repetitions drops that atom and its star, while another matching repetition consumes a text character without advancing the pattern. Only the previous text row and the current row are needed. This avoids exponential recursive re-exploration; memoized recursion is an equivalent formulation. The independent oracle uses Python's full-match regex engine on exactly this restricted grammar.","O(|s| × |p|)","O(|p|)",difficulty=8),
    32: entry("longest_valid_parentheses", [("s","str")], "int", ["strings","stacks"],
        ["0–30,000 characters, each '(' or ')'.", "Return the length of the longest contiguous well-formed parentheses substring, not a subsequence."],
        [(["(()"],"The final two characters form (), so the longest valid substring has length two."),
         ([")()())"],"The middle ()() is valid and has length four; the unmatched closing parentheses cannot be included.")],
        [[s] for s in ("","(",")","()", ")(","((","))","(())","()()","())(()","()(())","(()())")],
        PARENTHESES, [PARENTHESES.replace("[-1]", "[0]", 1),
                      'def longest_valid_parentheses(s):\n    return 2 * min(s.count("("), s.count(")"))\n'],
        ["Uses zero instead of the virtual boundary -1, shortening matches that start at index zero.", "Counts pairs globally, ignoring ordering and contiguity."], parentheses_oracle, random_parentheses,
        ["An unmatched parenthesis forms a boundary that a valid substring cannot cross.","Store unmatched opening indices above a sentinel marking the latest invalid boundary.","Push openings. On a closing pop once; if empty, install a new boundary. Otherwise measure index minus the remaining top.","The sentinel begins at -1 so a valid prefix gets its full length."],
        "The stack holds unmatched opening positions and an invalid-boundary sentinel. Matching a closing parenthesis removes the latest opening, after which the remaining top marks the boundary before the valid suffix ending here. If popping empties the stack, this closing parenthesis itself becomes the new invalid boundary. Taking the longest suffix length over all positions yields the longest valid substring in linear time. The oracle examines substrings using balance counts instead of this index-stack invariant.","O(n)","O(n)",difficulty=8,
        stress=[(["("*15000 + ")"*15000],30000)]),
    41: entry("first_missing_positive", [("nums","list[int]")], "int", ["arrays","hash-maps"],
        ["1–100,000 signed 32-bit integers.", "Return the smallest absent positive integer in O(n) time and O(1) auxiliary space. Input rearrangement is allowed."],
        [([[1,2,0]],"1 and 2 are present, while 3 is absent; zero is not positive."),
         ([[3,4,-1,1]],"1 is present but 2 is missing, regardless of the negative entry and larger values.")],
        [[v] for v in ([1],[2],[0],[-1],[1,1],[2,2],[1,2,3],[3,2,1],[7,8,9,11,12],[0,2,2,1,1],[2**31-1,-(2**31)],[2,3,4,5])],
        MISSING, [MISSING.replace("return n + 1","return n"), MISSING.replace("return i + 1","return i")],
        ["Returns n instead of n+1 when all values 1 through n are present.", "Returns a zero-based array position instead of its one-based positive value."], missing_oracle, random_missing,
        ["For n entries, the answer is always among 1 through n+1.","Use the array as its own position table: value x belongs at index x-1 when 1<=x<=n.","Swap an eligible value into place until the current position is settled or irrelevant. Then scan for the first index without index+1.","Check whether the destination already contains that value to stop duplicate-value cycles."],
        "Place each relevant value x at index x-1 using swaps. Values outside 1…n cannot affect an earlier missing positive and need no position. Never swap identical destination values, which would loop on duplicates. Each productive swap permanently places at least one value, bounding total swaps by O(n). The first mismatching position identifies the answer; if every position matches, return n+1. The independent set-based oracle is intentionally not the constant-space reference approach.","O(n)","O(1)",difficulty=8,
        stress=[([list(range(100000,0,-1))],100001)]),
    44: entry("wildcard_match", [("s","str"),("p","str")], "bool", ["strings","dynamic-programming","recursion"],
        ["s and p each have length 0–2000. s contains lowercase letters.", "p contains lowercase letters, '?' (exactly one arbitrary character), and '*' (any sequence, possibly empty).", "Match the entire string. A star acts independently, not on the preceding character."],
        [(["aa","a"],"A single literal a cannot cover the entire string aa."),
         (["adceb","*a*b"],"The first star can be empty, a matches a, the second star covers dce, and b matches b.")],
        [["",""],["","*"],["","?"],["a",""],["a","?"],["aa","*"],["cb","?a"],["ab","a*b"],
         ["abc","a?c"],["abc","***"],["acdcb","a*c?b"],["ab","*c"]],
        WILDCARD, [WILDCARD.replace("current[j - 1] or previous[j]", "previous[j]"),
                   WILDCARD.replace('p[j - 1] == "?" or ', '')],
        ["Disallows a star from matching an empty sequence after a text prefix.", "Treats question mark as a literal character."], wildcard_oracle, random_wildcard,
        ["Ask whether each text prefix matches each pattern prefix.","A star can either match nothing or consume another text character while staying on the same star.","For a star use current[j-1] or previous[j]; for a literal/question mark use the diagonal state and a one-character match.","Only a prefix made entirely of stars can match empty text. Question mark always consumes exactly one character."],
        "In prefix DP, an independent star either advances only the pattern (empty match) or advances only the text (another consumed character). Other pattern characters consume one from each side and require literal equality or a question mark. Initialize the empty-text row through consecutive stars. Keeping only two rows limits auxiliary space to the pattern length. The independent oracle is fnmatchcase, whose whole-string semantics agree on this restricted grammar without brackets or other extensions.","O(|s| × |p|)","O(|p|)",difficulty=8,
        stress=[(["a"*2000,"a"*2000],True),(["a"*2000,"a"*1999+"b"],False)]),
    45: entry("minimum_jumps", [("nums","list[int]")], "int", ["arrays","greedy"],
        ["1–10,000 entries; each maximum jump length is 0–1000.", "Start at index zero; the final index is guaranteed reachable. A jump may be any positive length up to the current maximum."],
        [([[2,3,1,1,4]],"Jump from index 0 to 1, then from 1 to 4. Two jumps are minimal."),
         ([[2,3,0,1,4]],"The same 0→1→4 route avoids the zero at index 2 and still uses two jumps.")],
        [[v] for v in ([0],[1],[1,0],[2,0,0],[1,1,0],[3,0,0,0],[2,1,1,0],[1,2,0,1],[2,3,0,1,1,1],[4,1,1,1,0],[1,1,1,1],[2,0,2,0,0])],
        JUMPS, [JUMPS.replace("range(len(nums) - 1)","range(len(nums))"),
                JUMPS.replace("max(farthest, index + nums[index])","index + nums[index]")],
        ["Counts another jump when scanning the destination itself.", "Forgets the farthest reach from other positions in the same jump layer."], minimum_jumps_oracle, random_jumps,
        ["Think of positions reachable in the same number of jumps as one breadth-first layer.","Scan the current layer while recording the farthest endpoint the next jump can reach.","When the scan reaches the current layer's end, increment the jump count and promote farthest to the new end.","Do not scan the final index as a departure point: no jump is needed after arrival."],
        "All reachable indices between layer boundaries are achievable with the current jump count. Scan those indices once and take the maximum of their endpoints. Crossing the layer boundary commits one more jump and expands to that maximum endpoint. This is breadth-first search compressed into two range bounds, so it finds the minimum count without exploring every jump edge. The independent oracle performs ordinary queue-based shortest-path search on those edges.","O(n)","O(1)",difficulty=5,
        stress=[([[1]*10000],9999)]),
    55: entry("can_jump", [("nums","list[int]")], "bool", ["arrays","greedy"],
        ["1–10,000 entries; each maximum jump length is 0–100,000.", "Start at index zero and decide whether the final index can be reached. Shorter jumps than the maximum are allowed."],
        [([[2,3,1,1,4]],"Index 1 is reachable from 0 and can then reach index 4."),
         ([[3,2,1,0,4]],"Every possible route stops at or before the zero at index 3, leaving the last index unreachable.")],
        [[v] for v in ([0],[1],[0,1],[1,0],[2,0,0],[1,0,1],[2,1,0,1],[3,0,0,0],[1,1,1,0],[4,0,0,0,1],[2,0,1,0],[1,2,0,0])],
        REACHABLE, [REACHABLE.replace("if index > farthest:","if index >= farthest:"),
                    REACHABLE.replace("max(farthest, index + reach)","index + reach").replace("        if farthest >= len(nums) - 1:\n            return True\n", "")],
        ["Rejects an index exactly on the reachable boundary, including the starting index.", "Replaces the reachable frontier with the current jump endpoint, losing earlier longer jumps."], reachable_oracle, random_reachable,
        ["Reachable forward positions form a prefix ending at a farthest known index.","Every reachable position may extend that prefix; no unreachable position can help.","If index exceeds farthest, fail. Otherwise maximize farthest with index+nums[index], succeeding once it reaches the end.","A zero is only fatal when no earlier reachable position can jump past it."],
        "Maintain the farthest position reachable from all already scanned reachable indices. If the scan reaches a position beyond that frontier, no earlier jump can cross the gap, so the destination is unreachable. Otherwise extend the frontier with the current endpoint. Reaching or passing the last index proves success. A single-element input is already at its destination. The oracle independently traverses the directed graph of legal jumps.","O(n)","O(1)",difficulty=5,
        stress=[([[1]*9999+[0]],True),([[0]+[100000]*9999],False)]),
}

for source_id, prerequisites in {10:["strings","dynamic-programming"],32:["stacks"],41:["arrays"],44:["strings","dynamic-programming"]}.items():
    BATCH[source_id]["prerequisites"] = prerequisites
