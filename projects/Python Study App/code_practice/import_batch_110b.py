"""Second reviewed group of workbook batch 110."""

from itertools import combinations

from .import_batch_055 import entry


def evaluate_expression(text):
    position = 0

    def parse():
        nonlocal position
        result = None
        operator = None
        while position < len(text):
            char = text[position]
            if char in "01":
                atom = int(char)
                position += 1
            elif char == "(":
                position += 1
                atom = parse()
            else:
                raise ValueError("expected an operand")
            if result is None:
                result = atom
            else:
                result = result & atom if operator == "&" else result | atom
            if position == len(text):
                return result
            if text[position] == ")":
                position += 1
                return result
            operator = text[position]
            position += 1
        return result

    return parse()


def expression_oracle(arguments):
    expression = arguments[0]
    editable = [index for index, char in enumerate(expression) if char in "01&|"]
    original = evaluate_expression(expression)
    opposite = {"0": "1", "1": "0", "&": "|", "|": "&"}
    for cost in range(1, len(editable) + 1):
        for changed in combinations(editable, cost):
            candidate = list(expression)
            for index in changed:
                candidate[index] = opposite[candidate[index]]
            if evaluate_expression("".join(candidate)) != original:
                return cost
    raise AssertionError("every valid expression can be changed")


def redistribution_oracle(arguments):
    words = arguments[0]
    joined = "".join(words)
    return all(joined.count(char) % len(words) == 0 for char in set(joined))


def removals_oracle(arguments):
    s, p, removable = arguments

    def remains(k):
        removed = set(removable[:k])
        position = 0
        for index, char in enumerate(s):
            if index not in removed and position < len(p) and char == p[position]:
                position += 1
        return position == len(p)

    return max(k for k in range(len(removable) + 1) if remains(k))


def triplets_oracle(arguments):
    triplets, target = arguments
    for mask in range(1, 1 << len(triplets)):
        merged = [0, 0, 0]
        for index, triplet in enumerate(triplets):
            if mask >> index & 1:
                merged = [max(left, right) for left, right in zip(merged, triplet)]
        if merged == target:
            return True
    return False


def tournament_oracle(arguments):
    n, first, second = arguments
    states = {tuple(range(1, n + 1))}
    meeting_rounds = []
    round_number = 1
    while states:
        next_states = set()
        for players in states:
            pairs = [(players[index], players[-1 - index]) for index in range(len(players) // 2)]
            if any({left, right} == {first, second} for left, right in pairs):
                meeting_rounds.append(round_number)
                continue
            middle = [players[len(players) // 2]] if len(players) % 2 else []
            choices = []
            for left, right in pairs:
                if left in {first, second}:
                    choices.append([left])
                elif right in {first, second}:
                    choices.append([right])
                else:
                    choices.append([left, right])
            winners = [middle]
            for pair_choices in choices:
                winners = [current + [winner] for current in winners for winner in pair_choices]
            next_states.update(tuple(sorted(current)) for current in winners)
        states = next_states
        round_number += 1
    return [min(meeting_rounds), max(meeting_rounds)]


def random_expression(rng):
    def build(depth):
        if depth == 0 or rng.random() < 0.35:
            return rng.choice("01")
        return "(" + build(depth - 1) + rng.choice("&|") + build(depth - 1) + ")"
    expression = build(2)
    return [expression[1:-1] if expression.startswith("(") and rng.random() < 0.5 else expression]


def random_redistribution(rng):
    return [["".join(rng.choice("abcd") for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(1, 8))]]


def random_removals(rng):
    length = rng.randint(1, 18)
    s = "".join(rng.choice("abc") for _ in range(length))
    selected = sorted(rng.sample(range(length), rng.randint(1, length)))
    p = "".join(s[index] for index in selected)
    removable = rng.sample(range(length), rng.randint(0, length - 1))
    return [s, p, removable]


def random_triplets(rng):
    count = rng.randint(1, 8)
    return [[[rng.randint(1, 8) for _ in range(3)] for _ in range(count)],
            [rng.randint(1, 8) for _ in range(3)]]


def random_tournament(rng):
    n = rng.randint(2, 10)
    first, second = sorted(rng.sample(range(1, n + 1), 2))
    return [n, first, second]


EXPRESSION = '''\
def minimum_expression_flip_cost(expression):
    values = []
    operators = []
    infinity = 10**9
    def combine(left, right, operator):
        costs = [infinity, infinity]
        for left_value in (0, 1):
            for right_value in (0, 1):
                for chosen in "&|":
                    result = left_value & right_value if chosen == "&" else left_value | right_value
                    cost = left[left_value] + right[right_value] + (chosen != operator)
                    costs[result] = min(costs[result], cost)
        return costs
    def reduce_once():
        right = values.pop()
        left = values.pop()
        operator = operators.pop()
        values.append(combine(left, right, operator))
    for char in expression:
        if char == "0":
            values.append([0, 1])
            if operators and operators[-1] in "&|":
                reduce_once()
        elif char == "1":
            values.append([1, 0])
            if operators and operators[-1] in "&|":
                reduce_once()
        elif char in "&|":
            operators.append(char)
        elif char == "(":
            operators.append(char)
        else:
            operators.pop()
            if operators and operators[-1] in "&|":
                reduce_once()
    return values[0][1] if values[0][0] == 0 else values[0][0]
'''

EXPRESSION_ALWAYS_ONE = '''\
def minimum_expression_flip_cost(expression):
    return 1
'''

REDISTRIBUTE = '''\
def can_redistribute_to_equal_words(words):
    from collections import Counter
    counts = Counter("".join(words))
    return all(amount % len(words) == 0 for amount in counts.values())
'''

REDISTRIBUTE_LENGTH = '''\
def can_redistribute_to_equal_words(words):
    return sum(map(len, words)) % len(words) == 0
'''

REDISTRIBUTE_CURRENT = '''\
def can_redistribute_to_equal_words(words):
    return len({len(word) for word in words}) == 1
'''

REMOVALS = '''\
def maximum_subsequence_removals(s, p, removable):
    def remains(k):
        removed = set(removable[:k])
        matched = 0
        for index, char in enumerate(s):
            if index not in removed and matched < len(p) and char == p[matched]:
                matched += 1
        return matched == len(p)
    left, right = 0, len(removable)
    while left < right:
        middle = (left + right + 1) // 2
        if remains(middle):
            left = middle
        else:
            right = middle - 1
    return left
'''

TRIPLETS = '''\
def can_merge_to_target_triplet(triplets, target):
    achieved = [0, 0, 0]
    for triplet in triplets:
        if all(value <= limit for value, limit in zip(triplet, target)):
            achieved = [max(current, value) for current, value in zip(achieved, triplet)]
    return achieved == target
'''

TRIPLETS_ALL = '''\
def can_merge_to_target_triplet(triplets, target):
    merged = [max(triplet[index] for triplet in triplets) for index in range(3)]
    return merged == target
'''

TRIPLETS_EXACT = '''\
def can_merge_to_target_triplet(triplets, target):
    return target in triplets
'''

TOURNAMENT = '''\
def earliest_and_latest_tournament_rounds(n, first_player, second_player):
    from functools import lru_cache
    infinity = 10**9
    @lru_cache(maxsize=None)
    def search(size, first, second):
        if first + second == size - 1:
            return (1, 1)
        pairs = size // 2
        outcomes = set()
        for mask in range(1 << pairs):
            winners = [False] * size
            for pair in range(pairs):
                winner = pair if mask >> pair & 1 else size - 1 - pair
                winners[winner] = True
            if size % 2:
                winners[pairs] = True
            winners[first] = winners[second] = True
            winners[size - 1 - first] = False
            winners[size - 1 - second] = False
            winners[first] = winners[second] = True
            next_first = sum(winners[:first])
            next_second = sum(winners[:second])
            outcomes.add((next_first, next_second, sum(winners)))
        earliest, latest = infinity, -infinity
        for next_first, next_second, next_size in outcomes:
            child_early, child_late = search(next_size, next_first, next_second)
            earliest = min(earliest, child_early + 1)
            latest = max(latest, child_late + 1)
        return earliest, latest
    return list(search(n, first_player - 1, second_player - 1))
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1896: entry(
        "minimum_expression_flip_cost", [("expression", "str")], "int",
        ["strings", "stacks", "dynamic-programming", "parsing"],
        ["The valid expression has length 1 through 100000 and contains only 0, 1, &, |, and matched parentheses.",
         "Parentheses evaluate first; outside them, & and | have equal precedence and evaluate left to right.",
         "One operation flips one digit or changes one operator; return the minimum operations that invert the final value."],
        [(["1&(0|1)"], "The expression evaluates to one; changing the first digit to zero changes the result at cost one."),
         (["1|1"], "Changing only one symbol cannot make both sides of the OR zero, so two digit flips are required.")],
        [[expression] for expression in [
            "0","1","1&0","1|0","1|1","0&0","1&(0|1)","(0&0)&(0&0)",
            "(0|1)&1","0|1&0","(1&1)|(0&1)","((1|0)&1)","(1|0)&(0|1)","((0&1)|(1&0))",
        ]],
        EXPRESSION,
        [EXPRESSION.replace('for chosen in "&|":', 'for chosen in operator:'), EXPRESSION_ALWAYS_ONE],
        ["Allows digit flips but never considers changing an operator.",
         "Assumes one edit always suffices, missing expressions such as 1|1 that require two changes."],
        expression_oracle, random_expression,
        lesson("For each subexpression, track the minimum cost to make its value zero and to make it one.",
               "Combine two cost pairs by trying both operand values and both possible operators, charging one if the operator changes.",
               "Use a stack to combine left-to-right within each parenthesis level and collapse a group at its closing parenthesis.",
               "The two costs enumerate every way to edit each parsed subexpression; optimal substructure and the stack's required evaluation order prove the final opposite-value cost."),
        "O(length)", "O(length)", 8),
    1897: entry(
        "can_redistribute_to_equal_words", [("words", "list[str]")], "bool",
        ["strings", "hash-maps", "counting"],
        ["There are 1 through 100 nonempty lowercase words of length at most 100.",
         "An operation moves one chosen character between different words and may insert it anywhere.",
         "Return whether all words can be made exactly equal."],
        [([["abc","aabc","bc"]], "Each of a, b, and c appears three times, so every final word can contain one of each."),
         ([["ab","a"]], "The single b cannot be divided equally between two final words.")],
        [[words] for words in [
            ["a"],["abc","aabc","bc"],["ab","a"],["a","a"],["abc","bca","cab"],
            ["aa","bb"],["ab","ba"],["a","b","c"],["abc","abc"],["aaa","a","aa"],
            ["abcd","bcda","cdab","dabc"],["x","xx"],["abca","bc","a"],["zz","zz","zz"],
        ]],
        REDISTRIBUTE,
        [REDISTRIBUTE_LENGTH, REDISTRIBUTE_CURRENT],
        ["Checks only total length divisibility and ignores whether each character count divides evenly.",
         "Checks current word lengths even though characters may be redistributed between words."],
        redistribution_oracle, random_redistribution,
        lesson("Moving characters preserves the total count of every letter.",
               "Count all letters across all words.",
               "Every letter count must be divisible by the number of final equal words.",
               "Divisibility is necessary because equal words use equal counts, and sufficient because arbitrary moves can distribute each letter's quotient to every word."),
        "O(total characters)", "O(1)", 3),
    1898: entry(
        "maximum_subsequence_removals", [("s", "str"), ("p", "str"), ("removable", "list[int]")], "int",
        ["strings", "binary-search", "two-pointers"],
        ["1 <= len(p) <= len(s) <= 100000 and p initially is a subsequence of s.",
         "removable contains distinct valid indices and may be empty.",
         "Remove exactly the first k listed indices and maximize k while p remains a subsequence."],
        [(["abcacb","ab",[3,1,0]], "After removing indices three and one, a and b remain; removing index zero next destroys the subsequence."),
         (["abcbddddd","abcd",[3,2,1,4,5,6]], "Only the first listed removal can occur while retaining a-b-c-d in order.")],
        [[s,p,removable] for s,p,removable in [
            ("a","a",[]),("abcacb","ab",[3,1,0]),("abcbddddd","abcd",[3,2,1,4,5,6]),
            ("abcab","abc",[4,3]),("aaaa","aa",[0,1,2]),("abc","abc",[0,1]),
            ("abcde","ace",[1,3]),("ababab","aaa",[1,3,5]),("leetcode","let",[7,6,5]),
            ("banana","ban",[5,3,1]),("axbycz","abc",[1,3,5]),("aaaaa","a",[0,1,2,3]),
            ("cabca","ca",[0,4,1]),("mississippi","mii",[10,8,5,2]),
        ]],
        REMOVALS,
        [REMOVALS.replace("removable[:k]", "removable[-k:] if k else []"),
         REMOVALS.replace("return left", "return min(len(removable), left + 1)")],
        ["Removes the last k listed indices instead of the required first k.",
         "Returns the first failing count rather than the largest passing count."],
        removals_oracle, random_removals,
        lesson("If p survives the first k removals, it survives every smaller prefix, giving a monotonic predicate.",
               "For a candidate k, mark its removed indices and scan s and p with two pointers.",
               "Binary-search the largest k whose scan matches all of p.",
               "Prefix nesting proves monotonicity, the scan exactly tests subsequence order, and upper-mid search retains the largest passing boundary."),
        "O((len(s)+len(removable))*log(len(removable)+1))", "O(len(s))", 6),
    1899: entry(
        "can_merge_to_target_triplet", [("triplets", "list[list[int]]"), ("target", "list[int]")], "bool",
        ["arrays", "greedy"],
        ["There are 1 through 100000 triplets of positive values at most 1000.", "target also has exactly three positive values.",
         "A merge takes the coordinate-wise maximum; determine whether some sequence of merges can equal target."],
        [([[[2,5,3],[1,8,4],[1,7,5]],[2,7,5]], "The first and third triplets merge to the target; the second must be excluded because its middle value is too large."),
         ([[[3,4,5],[4,5,6]],[3,2,5]], "Every useful-looking triplet exceeds the target in at least one coordinate, so the target is impossible.")],
        [[triplets,target] for triplets,target in [
            ([[1,1,1]],[1,1,1]),([[2,5,3],[1,8,4],[1,7,5]],[2,7,5]),
            ([[3,4,5],[4,5,6]],[3,2,5]),([[1,2,3],[2,1,3]],[2,2,3]),
            ([[5,1,1],[1,5,1],[1,1,5]],[5,5,5]),([[6,1,1],[1,5,5]],[5,5,5]),
            ([[2,2,2]],[3,3,3]),([[3,3,3],[1,1,1]],[3,3,3]),
            ([[2,7,5],[9,1,1]],[2,7,5]),([[1,4,2],[3,2,5],[2,5,4]],[3,5,5]),
            ([[10,2,3],[4,8,6],[7,5,9]],[10,8,9]),([[2,3,4],[2,4,3]],[2,4,4]),
            ([[1,9,1],[9,1,9],[1,1,9]],[9,9,9]),([[4,4,1],[4,1,4]],[4,4,4]),
        ]],
        TRIPLETS,
        [TRIPLETS_ALL, TRIPLETS_EXACT],
        ["Merges every triplet, allowing an irrelevant oversized coordinate to make the result exceed target.",
         "Requires one exact triplet and ignores that different triplets can supply different target coordinates."],
        triplets_oracle, random_triplets,
        lesson("A triplet exceeding target in any coordinate can never participate because maxima cannot decrease.",
               "Merge only component-wise safe triplets into an accumulated coordinate-wise maximum.",
               "Succeed exactly when all three accumulated coordinates reach target.",
               "Filtering is necessary by monotonicity of maximum, and every safe contributor may be merged without overshooting, so reaching all coordinates is sufficient."),
        "O(number of triplets)", "O(1)", 6),
    1900: entry(
        "earliest_and_latest_tournament_rounds", [("n", "int"), ("first_player", "int"), ("second_player", "int")], "list[int]",
        ["dynamic-programming", "memoization", "combinatorics", "recursion"],
        ["2 <= n <= 28 and 1 <= first_player < second_player <= n.",
         "Each round pairs players symmetrically from the ends; an unpaired middle player advances.",
         "The two named players always defeat others, while every other match outcome may vary; return earliest and latest possible meeting rounds."],
        [([11,2,4], "Across possible outcomes of other matches, the two players can first meet in round three or as late as round four."),
         ([5,1,5], "The two players are paired from opposite ends in the opening round.")],
        [[*case] for case in [
            (2,1,2),(3,1,3),(3,1,2),(4,1,4),(4,1,2),(5,1,5),(5,2,4),
            (6,2,5),(7,2,6),(8,1,3),(8,2,7),(9,3,8),(10,2,4),(11,2,4),
        ]],
        TOURNAMENT,
        [TOURNAMENT.replace("for mask in range(1 << pairs):", "for mask in range(1):"),
         TOURNAMENT.replace("for mask in range(1 << pairs):", "for mask in range((1 << pairs) - 1, 1 << pairs):")],
        ["Assumes the back-side player wins every unrelated match instead of exploring possible outcomes.",
         "Assumes the front-side player wins every unrelated match instead of exploring possible outcomes."],
        tournament_oracle, random_tournament,
        lesson("Only the ordered positions of the two protected players and the current field size affect future possibilities.",
               "Enumerate winners of unrelated symmetric matches while forcing both protected players to advance.",
               "Map their positions among sorted winners, memoize that smaller state, and combine child earliest/latest rounds.",
               "Every legal round outcome produces one mapped state and every mapped state is explored; memoized recursion therefore spans exactly all possible brackets."),
        "O(number of reachable states * 2^(n/2))", "O(number of reachable states)", 8),
}
