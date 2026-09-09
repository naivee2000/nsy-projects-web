from __future__ import annotations

import copy
import textwrap
from dataclasses import dataclass
from typing import Any

from .content_solutions import ListNode, TreeNode
from .example_content import examples_for
from .schemas import DifficultyRubric, FunctionSignature, ParameterDefinition, ProblemDefinition, TestCase
from .starter_code import with_support_classes


@dataclass(frozen=True)
class DistinctSpec:
    id: str
    title: str
    summary: str
    topics: list[str]
    function_name: str
    parameters: list[tuple[str, str, str]]
    returns: str
    body: str
    cases: list[list[Any]]
    difficulty: int
    time_complexity: str
    space_complexity: str
    concept: str
    strategy: str
    comparator: str = "exact"
    return_adapter: str = "raw"


def _listnode(values: list[int] | None) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    for value in values or []:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


def _treenode(values: list[int | None] | None) -> TreeNode | None:
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    index = 1
    while queue and index < len(values):
        node = queue.pop(0)
        if index < len(values) and values[index] is not None:
            node.left = TreeNode(values[index])
            queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right = TreeNode(values[index])
            queue.append(node.right)
        index += 1
    return root


def _serialize(value: Any, adapter: str) -> Any:
    if adapter == "listnode":
        result = []
        while value:
            result.append(value.val)
            value = value.next
        return result
    return value


def _source(spec: DistinctSpec) -> str:
    names = ", ".join(name for name, _annotation, _adapter in spec.parameters)
    body = textwrap.indent(textwrap.dedent(spec.body).strip(), "    ")
    return f"def {spec.function_name}({names}):\n{body}\n"


def _expected(spec: DistinctSpec, arguments: list[Any]) -> Any:
    namespace: dict[str, Any] = {"ListNode": ListNode, "TreeNode": TreeNode}
    exec(_source(spec), namespace)
    values = []
    for value, (_name, _annotation, adapter) in zip(copy.deepcopy(arguments), spec.parameters):
        if adapter == "listnode":
            value = _listnode(value)
        elif adapter == "treenode":
            value = _treenode(value)
        values.append(value)
    return _serialize(namespace[spec.function_name](*values), spec.return_adapter)


def _rubric(score: int) -> DifficultyRubric:
    table = {
        2: (1, 0, 1, 0, 0), 3: (1, 1, 1, 0, 0), 4: (2, 1, 1, 0, 0),
        5: (2, 1, 1, 1, 0), 6: (2, 1, 1, 1, 1), 7: (2, 2, 1, 1, 1),
        8: (3, 2, 1, 1, 1), 9: (3, 2, 2, 1, 1), 10: (3, 2, 2, 2, 1),
    }
    values = table[score]
    return DifficultyRubric(
        algorithmic_insight=values[0], prerequisites=values[1], implementation=values[2],
        performance_pressure=values[3], edge_cases=values[4],
    )


def build_problem(spec: DistinctSpec) -> ProblemDefinition:
    if len(spec.cases) != 14:
        raise ValueError(f"{spec.id} needs exactly fourteen deterministic cases")
    examples = examples_for(spec.id)
    cases = [arguments for arguments, _explanation in examples] + spec.cases[2:]
    tests = [
        TestCase(
            id=f"{spec.id}-case-{index + 1}",
            arguments=arguments,
            expected=_expected(spec, arguments),
            comparator=spec.comparator,
            visible=True,
            explanation=examples[index][1] if index < 2 else None,
        )
        for index, arguments in enumerate(cases)
    ]
    params = ", ".join(f"{name}: {annotation}" for name, annotation, _adapter in spec.parameters)
    source = _source(spec)
    call_names = ", ".join(name for name, _annotation, _adapter in spec.parameters)
    return ProblemDefinition(
        id=spec.id,
        title=spec.title,
        summary=spec.summary,
        statement=REPLACEMENT_STATEMENTS.get(
            spec.id,
            f"{spec.summary} Implement `{spec.function_name}` and return the required result without changing the callable signature.",
        ),
        constraints=REPLACEMENT_CONSTRAINTS.get(
            spec.id,
            ["Inputs follow the declared Python and JSON-compatible types.", "Return a deterministic result for every valid input."],
        ),
        topics=spec.topics,
        prerequisites=spec.topics[:1] if spec.difficulty >= 5 else [],
        signature=FunctionSignature(
            name=spec.function_name,
            parameters=[ParameterDefinition(name=name, annotation=annotation, adapter=adapter) for name, annotation, adapter in spec.parameters],
            returns=spec.returns,
            return_adapter=spec.return_adapter,
        ),
        starter_code=with_support_classes(
            f"def {spec.function_name}({params}) -> {spec.returns}:\n    # Write your solution here.\n    pass\n",
            [*[adapter for _name, _annotation, adapter in spec.parameters], spec.return_adapter],
        ),
        reference_solution=source,
        brute_force_solution=source,
        known_wrong_solutions=[
            f"def {spec.function_name}({call_names}):\n    return None\n",
            f"def {spec.function_name}({call_names}):\n    return 0\n",
        ],
        target_time_complexity=spec.time_complexity,
        target_space_complexity=spec.space_complexity,
        estimated_minutes=10 + spec.difficulty * 5,
        rubric=_rubric(spec.difficulty),
        hints=[
            spec.concept,
            spec.strategy,
            f"Pseudocode checkpoint: identify the state, update it once per step, and return only after the {spec.function_name} invariant is complete.",
            f"Editorial: {spec.strategy} The intended bounds are {spec.time_complexity} time and {spec.space_complexity} space.",
        ],
        editorial=f"{spec.concept} {spec.strategy} This yields {spec.time_complexity} time and {spec.space_complexity} auxiliary space.",
        tests=tests,
    )


def S(
    id: str, title: str, summary: str, topics: list[str], function_name: str,
    parameters: list[tuple[str, str, str]], returns: str, body: str, cases: list[list[Any]],
    difficulty: int, time: str, space: str, concept: str, strategy: str,
    comparator: str = "exact", return_adapter: str = "raw",
) -> DistinctSpec:
    return DistinctSpec(id, title, summary, topics, function_name, parameters, returns, body, cases, difficulty, time, space, concept, strategy, comparator, return_adapter)


ARRAY_CASES = [
    [[1, 3, 2, 5, 4]], [[0, 0, 1]], [[]], [[7]], [[1, 2, 3, 4]], [[4, 3, 2, 1]],
    [[2, 2, 2]], [[-3, -1, -2]], [[1, 3, 3, 2]], [[5, 1, 5, 1]], [[0]],
    [[10, -10, 10]], [[1, 2, 1, 2, 1]], [[9, 7, 5, 3, 1]],
]
TEXT_CASES = [[value] for value in [
    "swiss", "aaabbc", "", "a", "hello world", "  one   two  ", "racecar", "banana",
    "A a", "mississippi", "code practice lab", "112233", "xyzz", "the quick brown fox",
]]
TWO_TEXT_CASES = [
    ["listen", "silent"], ["abc", "axc"], ["", ""], ["a", ""], ["abc", "abc"], ["abc", "ac"],
    ["kitten", "sitting"], ["aaaa", "aa"], ["abc", "def"], ["subsequence", "sue"],
    ["binary", "brainy"], ["stone", "tones"], ["abcd", "badc"], ["dynamic", "programming"],
]
SORTED_TARGET_CASES = [
    [[1, 2, 2, 2, 4], 2], [[1, 3, 5, 7], 4], [[], 3], [[5], 5], [[5], 2],
    [[-5, -2, 0, 0, 9], 0], [[1, 1, 1], 1], [[1, 2, 3], 0], [[1, 2, 3], 4],
    [[-3, -1, 2, 6], -3], [[0, 10, 20], 20], [[2, 4, 6, 8], 6], [[1, 5], 3], [[7, 7, 7, 7], 7],
]
ARRAY_K_CASES = [
    [[3, 1, 5, 2, 4], 2], [[1, 2, 3, 4], 3], [[7], 1], [[0, 0, 1], 2],
    [[-2, -1, -3], 2], [[5, 5, 5], 1], [[1, 2], 2], [[9, 1, 8, 2, 7], 4],
    [[4, 3, 2, 1], 3], [[1, 1, 2, 2], 2], [[10, -10, 10], 1], [[6, 2, 6, 2], 3],
    [[8, 0, 4], 2], [[2, 9, 1, 9, 3], 5],
]
INTERVAL_CASES = [
    [[[0, 30], [5, 10], [15, 20]]], [[[1, 2], [2, 3]]], [[]], [[[1, 4]]],
    [[[1, 3], [2, 6], [8, 10]]], [[[5, 7], [1, 2]]], [[[1, 10], [2, 3], [4, 5]]],
    [[[0, 0], [0, 1]]], [[[-3, -1], [-2, 2]]], [[[1, 2], [3, 4], [5, 6]]],
    [[[1, 5], [1, 5], [1, 5]]], [[[2, 4], [4, 8], [8, 9]]], [[[10, 20], [0, 5], [4, 12]]],
    [[[1, 100], [50, 60], [101, 102]]],
]
MATRIX_CASES = [
    [[[1, 2], [3, 4]]], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[]]], [[[5]]],
    [[[0, -1], [-2, 3]]], [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]],
    [[[-1, -2], [-3, -4]]], [[[2, 2], [2, 2]]], [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]],
    [[[1, -1, 1], [-1, 1, -1], [1, -1, 1]]], [[[7, 8, 9], [4, 5, 6], [1, 2, 3]]],
    [[[0, 0], [0, 0]]], [[[100, -100], [-100, 100]]], [[[1, 2, 1], [2, 1, 2], [1, 2, 1]]],
]
BINARY_GRID_CASES = [
    [[[1, 1, 0], [1, 0, 0], [0, 1, 1]]], [[[1]]], [[[0]]], [[[1, 1], [1, 1]]],
    [[[1, 0], [0, 1]]], [[[0, 0], [0, 0]]], [[[1, 0, 1]]], [[[1], [0], [1]]],
    [[[1, 1, 1], [0, 1, 0], [1, 1, 1]]], [[[0, 1, 0], [1, 1, 1], [0, 1, 0]]],
    [[[1, 0, 0], [1, 1, 0], [0, 1, 1]]], [[[1, 1, 0, 1], [0, 1, 0, 1]]],
    [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[1, 0, 1], [1, 0, 1], [1, 1, 1]]],
]

DIRECTED_GRAPH_CASES = [
    [4, [[0, 1], [1, 2], [0, 3]]], [3, [[0, 1], [1, 2], [2, 0]]], [1, []],
    [2, []], [2, [[0, 1]]], [5, [[0, 1], [0, 2], [2, 3], [3, 4]]],
    [4, [[1, 2], [2, 3]]], [4, [[0, 1], [0, 2], [1, 3], [2, 3]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]]], [3, [[0, 0]]],
    [6, [[0, 1], [1, 2], [3, 4], [4, 5]]], [4, [[0, 2], [2, 1], [1, 3]]],
    [5, [[4, 3], [3, 2], [2, 1], [1, 0]]], [3, [[0, 1], [0, 1], [1, 2]]],
]
UNDIRECTED_GRAPH_CASES = [
    [5, [[0, 1], [1, 2], [3, 4]]], [4, [[0, 1], [1, 2], [2, 3], [3, 0]]], [1, []],
    [2, []], [2, [[0, 1]]], [6, [[0, 1], [1, 2], [2, 0], [3, 4]]],
    [5, [[0, 1], [0, 2], [0, 3], [0, 4]]], [4, [[0, 1], [2, 3]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]]], [3, [[0, 0]]],
    [6, [[0, 1], [2, 3], [4, 5]]], [4, [[0, 1], [1, 2], [2, 0]]],
    [7, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 6]]], [3, [[0, 1], [0, 1], [1, 2]]],
]
TREE_CASES = [
    [[3, 9, 20, None, None, 15, 7]], [[1, 2, 3]], [[]], [[1]], [[1, 2]], [[1, None, 2]],
    [[5, 3, 8, 2, 4, 7, 9]], [[0, -1, 1]], [[1, 2, None, 3]], [[1, None, 2, None, 3]],
    [[10, 5, 15, 2, 7, 12, 20]], [[1, 2, 3, 4, 5]], [[9, 8, None, 7]], [[2, 1, 3, None, None, None, 4]],
]
LINKED_CASES = [
    [[1, 2, 3, 4]], [[1, 2, 1]], [[]], [[7]], [[1, 1]], [[1, 2]], [[1, 2, 3]],
    [[0, -1, 0]], [[5, 5, 5]], [[1, 2, 3, 2, 1]], [[9, 8, 7, 6, 5]],
    [[1, -1, 2, -2]], [[2, 2, 3, 3]], [[10, 20, 30, 40, 50, 60]],
]
HEIGHT_CASES = [
    [[2, 1, 2, 3]], [[2, 4, 2, 1]], [[]], [[5]], [[1, 2, 3]], [[3, 2, 1]],
    [[2, 1, 5, 6, 2, 3]], [[0, 0, 0]], [[4, 2, 0, 3, 2, 5]], [[1, 1, 2, 2]],
    [[6, 2, 5, 4, 5, 1, 6]], [[10, 1, 10]], [[1, 3, 2, 4]], [[5, 4, 3, 2, 1, 6]],
]
COIN_CASES = [
    [[1, 2, 5], 11], [[2], 3], [[1], 0], [[], 7], [[1], 2], [[2, 3], 7],
    [[1, 3, 4], 6], [[2, 5, 10], 10], [[5, 7], 1], [[1, 2], 4],
    [[3, 4, 5], 8], [[2, 2, 3], 4], [[1, 5, 10, 25], 30], [[7], 14],
]
TARGET_CASES = [
    [[1, 1, 1], 2], [[1, 2, 3], 3], [[], 0], [[5], 5], [[5], 2],
    [[-1, 1, 0], 0], [[3, 3, 3], 6], [[1, -1, 1, -1], 0],
    [[2, 4, 6, 8], 10], [[0, 0, 0], 0], [[-3, -2, -1], -3],
    [[10, 1, 2, 7], 9], [[5, -2, 3, 1], 4], [[1, 2, 1, 2, 1], 3],
]
SMALL_TEXT_CASES = [[value] for value in [
    "abc", "aab", "", "a", "ab", "aba", "aa", "ABC", "12", "xy", "abba", "abcd", "a1", "race",
]]
RECURSION_CASES = [[n] for n in [5, 7, 0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25]]
PIVOT_CASES = [
    [[1, 7, 3, 6, 5, 6]], [[1, 2, 3]], [[2, 1, -1]], [[0]], [[0, 0, 0]],
    [[1, -1, 0]], [[-1, -1, -1, -1, -1, 0]], [[3, -1, -2, 0]],
    [[-2, 5, -3, 0]], [[10, -10, 0]], [[1, 2, 1]], [[5, 0, 0, 5]],
    [[-4, 2, 2, 0]], [[]],
]
WORD_PATTERN_CASES = [
    ["abba", "red blue blue red"], ["abba", "red blue blue green"],
    ["aaaa", "red red red red"], ["abba", "red red red red"],
    ["abc", "one two three"], ["abc", "one two"], ["abca", "sun moon star sun"],
    ["abca", "sun moon sun sun"], ["a", "solo"], ["ab", "same same"],
    ["abcabc", "x y z x y z"], ["abcabc", "x y z x z y"],
    ["", ""], ["aa", "left right"],
]
FORMABLE_WORD_CASES = [
    [["cat", "hat", "tree"], "atach"], [["hello", "world", "hold"], "welldonehoneyr"],
    [[], "abc"], [["a"], ""], [["a", "aa", "aaa"], "aa"],
    [["book", "boot", "cook"], "obokt"], [["stone", "tones", "notes"], "stone"],
    [["abc", "abd", "cab"], "abc"], [["zz", "z", "zzz"], "zz"],
    [["apple", "pear"], "appeal"], [["one", "two", "three"], "threeone"],
    [["miss", "sip"], "mississippi"], [["x"], "xyz"], [["ab", "ba", "aa"], "aab"],
]
MISSING_GRID_CASES = [
    [[[1, 3], [2, 2]]], [[[9, 1, 7], [8, 9, 2], [3, 4, 6]]],
    [[[1, 1], [3, 4]]], [[[1, 2], [4, 4]]], [[[2, 3], [4, 2]]],
    [[[4, 1], [3, 1]]], [[[1, 2, 3], [4, 5, 6], [7, 7, 9]]],
    [[[1, 2, 3], [4, 5, 6], [8, 9, 9]]], [[[2, 2, 3], [4, 5, 6], [7, 8, 9]]],
    [[[1, 2, 3], [4, 5, 5], [7, 8, 9]]], [[[1, 2], [3, 3]]],
    [[[2, 1], [4, 2]]], [[[1, 3], [4, 1]]], [[[4, 2], [3, 2]]],
]
FLOOD_FILL_CASES = [
    [[ [1, 1, 1], [1, 1, 0], [1, 0, 1] ], 1, 1, 2],
    [[ [0, 0, 0], [0, 0, 0] ], 0, 0, 0],
    [[[1]], 0, 0, 3], [[[2, 2], [2, 2]], 1, 1, 5],
    [[[1, 2], [2, 1]], 0, 0, 9], [[[1, 1, 2], [2, 1, 2]], 0, 1, 3],
    [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], 1, 1, 2],
    [[[4, 4, 4], [4, 5, 4], [4, 4, 4]], 1, 1, 7],
    [[[3, 3, 0], [0, 3, 0]], 0, 0, 8], [[[1, 2, 2, 2]], 0, 2, 6],
    [[[1], [1], [2]], 1, 0, 4], [[[7, 8], [8, 8]], 1, 1, 7],
    [[[0, 0], [0, 1]], 1, 1, 2], [[[5, 5], [5, 5]], 0, 1, 5],
]
SORTED_LINKED_CASES = [
    [[1, 1, 2, 3, 3]], [[1, 1, 1]], [[]], [[7]], [[1, 2, 3]],
    [[-2, -2, -1, 0, 0]], [[1, 1]], [[1, 2, 2]], [[0, 0, 0, 1]],
    [[1, 2, 3, 3, 3]], [[-5, -5, -5, -4]], [[2, 2, 3, 3, 4, 4]],
    [[1, 1, 2, 2, 3, 3, 4]], [[10, 20, 20, 30]],
]
CLIMB_CASES = [[n] for n in [5, 4, 0, 1, 2, 3, 6, 7, 8, 10, 12, 15, 20, 25]]

REPLACEMENT_STATEMENTS = {
    "balanced-pivot-index": "For an index to be balanced, neither side includes the value at that index. Return the first balanced index from left to right. Return -1 when no index works, including for an empty list.",
    "word-pattern-bijection": "Split the text on whitespace. The number of words must equal the number of pattern characters, and the correspondence must work in both directions: one character cannot represent two words and two characters cannot represent the same word.",
    "formable-word-total": "Evaluate every candidate word independently against the same letter inventory. A letter may be used only as many times as it occurs in the inventory while forming one word; inventory use resets before checking the next word. Add the lengths of all formable words.",
    "missing-repeated-grid-values": "For an n × n grid, the intended values are 1 through n². Exactly one value occurs twice and exactly one value is absent. Return the repeated value first and the missing value second.",
    "flood-fill-region": "Starting at the given row and column, recolor that cell and every cell connected to it through up, down, left, or right moves that has the starting cell's original color. Diagonal contact does not connect regions.",
    "deduplicate-sorted-linked-list": "The linked list is sorted in nondecreasing order, so equal values are adjacent. Rewire next pointers so that one node remains for each distinct value, and return the original head. Do not create a replacement list.",
    "recursive-step-combinations": "For nonnegative n, count ordered sequences of 1-step and 2-step moves whose total is n. Different move orders count separately. For n = 0, the empty sequence counts as one way. Use a recursive recurrence with memoization.",
}

REPLACEMENT_CONSTRAINTS = {
    "balanced-pivot-index": ["0 ≤ len(nums) ≤ 10,000.", "Values may be negative, zero, or positive."],
    "word-pattern-bijection": ["The text contains whitespace-separated nonempty words.", "Pattern and text may be empty; their token counts must still match."],
    "formable-word-total": ["Words and letters contain lowercase English letters.", "Each candidate is checked independently against the full inventory."],
    "missing-repeated-grid-values": ["2 ≤ n ≤ 50.", "Cells contain values from 1 through n², with exactly one repeated and one missing value."],
    "flood-fill-region": ["The image is nonempty and rectangular.", "The starting row and column are valid image coordinates."],
    "deduplicate-sorted-linked-list": ["The list is sorted in nondecreasing order.", "The input may be an empty linked list."],
    "recursive-step-combinations": ["0 ≤ n ≤ 30.", "Use recursion with memoization rather than enumerating every move sequence."],
}


SPECS: list[DistinctSpec] = []


def add(*items: DistinctSpec) -> None:
    SPECS.extend(items)


# Array fundamentals: four different operations over the same broad data type.
add(
    S("balanced-pivot-index", "Balanced Pivot Index", "Return the leftmost index whose left-side sum equals its right-side sum, or -1.", ["arrays", "prefix-sums"], "balanced_pivot_index", [("nums", "list[int]", "raw")], "int", """
        total = sum(nums); left = 0
        for index, value in enumerate(nums):
            if left == total - left - value: return index
            left += value
        return -1
    """, PIVOT_CASES, 3, "O(n)", "O(1)", "The right-side sum can be derived from the total, the left sum, and the current value.", "Maintain the sum strictly left of each index and return the first index where it matches the derived right sum."),
    S("longest-increasing-run", "Longest Increasing Run", "Return the longest contiguous run whose values strictly increase.", ["arrays"], "longest_increasing_run", [("nums", "list[int]", "raw")], "int", """
        best = current = 0
        for i, value in enumerate(nums):
            current = current + 1 if i and value > nums[i - 1] else 1
            best = max(best, current)
        return best
    """, ARRAY_CASES, 3, "O(n)", "O(1)", "A contiguous run resets as soon as the ordering condition fails.", "Carry the current run length and the best length seen."),
    S("count-local-peaks", "Count Local Peaks", "Count interior positions strictly greater than both immediate neighbors.", ["arrays"], "count_local_peaks", [("nums", "list[int]", "raw")], "int", """
        return sum(nums[i] > nums[i - 1] and nums[i] > nums[i + 1] for i in range(1, len(nums) - 1))
    """, ARRAY_CASES, 2, "O(n)", "O(1)", "Only interior positions have two neighbors.", "Scan indices 1 through len(nums)-2 and compare both sides."),
    S("stable-zero-move", "Stable Zero Move", "Move all zeros to the end while preserving the order of nonzero values.", ["arrays", "two-pointers"], "stable_zero_move", [("nums", "list[int]", "raw")], "list[int]", """
        kept = [value for value in nums if value != 0]
        return kept + [0] * (len(nums) - len(kept))
    """, ARRAY_CASES, 3, "O(n)", "O(n)", "Separate relative order from final zero placement.", "Collect nonzeros in order, then append exactly the removed number of zeros."),
)

# String fundamentals.
add(
    S("first-unique-character", "First Unique Character", "Return the index of the first character appearing exactly once, or -1.", ["strings", "hash-maps"], "first_unique_character", [("text", "str", "raw")], "int", """
        from collections import Counter
        counts = Counter(text)
        return next((i for i, char in enumerate(text) if counts[char] == 1), -1)
    """, TEXT_CASES, 3, "O(n)", "O(k)", "A character is unique only after its total frequency is known.", "Count first, then scan again to preserve first-position order."),
    S("run-length-encode", "Run-Length Encode", "Compress consecutive equal characters as character followed by its count.", ["strings"], "run_length_encode", [("text", "str", "raw")], "str", """
        if not text: return ""
        parts, start = [], 0
        for i in range(1, len(text) + 1):
            if i == len(text) or text[i] != text[start]:
                parts.append(text[start] + str(i - start)); start = i
        return "".join(parts)
    """, TEXT_CASES, 3, "O(n)", "O(n)", "A run ends at the first different character or the end of the string.", "Track the run start, emit its character and length, then begin the next run."),
    S("word-pattern-bijection", "Word Pattern Bijection", "Return whether pattern characters and whitespace-separated words form a one-to-one correspondence.", ["strings", "hash-maps"], "word_pattern_bijection", [("pattern", "str", "raw"), ("text", "str", "raw")], "bool", """
        words = text.split()
        if len(pattern) != len(words): return False
        char_to_word, word_to_char = {}, {}
        for char, word in zip(pattern, words):
            if char in char_to_word and char_to_word[char] != word: return False
            if word in word_to_char and word_to_char[word] != char: return False
            char_to_word[char] = word; word_to_char[word] = char
        return True
    """, WORD_PATTERN_CASES, 3, "O(n)", "O(k)", "A valid pattern requires mappings in both directions, not just character-to-word consistency.", "Split the text, reject unequal lengths, and maintain synchronized character-to-word and word-to-character maps."),
    S("formable-word-total", "Formable Word Total", "Given candidate words and available letters, return the total length of words that can each be formed without reusing a letter.", ["strings", "hash-maps"], "formable_word_total", [("words", "list[str]", "raw"), ("letters", "str", "raw")], "int", """
        from collections import Counter
        available = Counter(letters); total = 0
        for word in words:
            needed = Counter(word)
            if all(needed[char] <= available[char] for char in needed): total += len(word)
        return total
    """, FORMABLE_WORD_CASES, 3, "O(total characters)", "O(k)", "Each candidate gets a fresh copy of the same letter inventory, but repeated letters inside one word still require repeated supply.", "Count available letters once, compare each word's frequency requirements, and add only the lengths of feasible words."),
)

# Two-string relationships, from easy counting through dynamic programming.
add(
    S("anagram-check", "Anagram Check", "Return whether two strings contain identical character multisets.", ["strings", "hash-maps"], "anagram_check", [("left", "str", "raw"), ("right", "str", "raw")], "bool", """
        from collections import Counter
        return Counter(left) == Counter(right)
    """, TWO_TEXT_CASES, 2, "O(n + m)", "O(k)", "Anagrams have the same frequency for every character.", "Compare two frequency maps rather than character positions."),
    S("subsequence-check", "Subsequence Check", "Return whether the second string can be read from the first without reordering.", ["strings", "two-pointers"], "subsequence_check", [("text", "str", "raw"), ("candidate", "str", "raw")], "bool", """
        index = 0
        for char in text:
            if index < len(candidate) and char == candidate[index]: index += 1
        return index == len(candidate)
    """, TWO_TEXT_CASES, 3, "O(n)", "O(1)", "Only the next unmatched candidate character matters.", "Scan the source once and advance the candidate pointer on matches."),
    S("edit-distance", "Edit Distance", "Return the minimum insertions, deletions, and replacements needed to transform one string into another.", ["dynamic-programming", "strings"], "edit_distance", [("left", "str", "raw"), ("right", "str", "raw")], "int", """
        previous = list(range(len(right) + 1))
        for i, a in enumerate(left, 1):
            current = [i]
            for j, b in enumerate(right, 1):
                current.append(previous[j - 1] if a == b else 1 + min(previous[j], current[-1], previous[j - 1]))
            previous = current
        return previous[-1]
    """, TWO_TEXT_CASES, 8, "O(nm)", "O(m)", "Each prefix pair depends on delete, insert, and replace choices.", "Build one dynamic-programming row at a time for prefixes of both strings."),
    S("longest-common-subsequence", "Longest Common Subsequence", "Return the length of the longest ordered subsequence shared by two strings.", ["dynamic-programming", "strings"], "longest_common_subsequence", [("left", "str", "raw"), ("right", "str", "raw")], "int", """
        row = [0] * (len(right) + 1)
        for a in left:
            previous, next_row = row, [0]
            for j, b in enumerate(right, 1):
                next_row.append(previous[j - 1] + 1 if a == b else max(previous[j], next_row[-1]))
            row = next_row
        return row[-1]
    """, TWO_TEXT_CASES, 6, "O(nm)", "O(m)", "Matching final characters extend a smaller solution; mismatches discard one side.", "Use prefix DP and retain only the prior row."),
)

# Binary-search boundary questions share sorted inputs but ask four different outputs.
add(
    S("lower-bound-index", "Lower Bound Index", "Return the first index whose value is at least target.", ["binary-search"], "lower_bound_index", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        left, right = 0, len(nums)
        while left < right:
            middle = (left + right) // 2
            if nums[middle] < target: left = middle + 1
            else: right = middle
        return left
    """, SORTED_TARGET_CASES, 4, "O(log n)", "O(1)", "The answer may be len(nums), so use a half-open search interval.", "Discard positions that are definitely too small while retaining possible answers."),
    S("upper-bound-index", "Upper Bound Index", "Return the first index whose value is strictly greater than target.", ["binary-search"], "upper_bound_index", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        left, right = 0, len(nums)
        while left < right:
            middle = (left + right) // 2
            if nums[middle] <= target: left = middle + 1
            else: right = middle
        return left
    """, SORTED_TARGET_CASES, 4, "O(log n)", "O(1)", "Equality belongs to the discarded left side for an upper bound.", "Move left past values less than or equal to target."),
    S("target-position-range", "Target Position Range", "Return the first and last target indices, or [-1, -1] when absent.", ["binary-search", "arrays"], "target_position_range", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "list[int]", """
        from bisect import bisect_left, bisect_right
        left = bisect_left(nums, target)
        if left == len(nums) or nums[left] != target: return [-1, -1]
        return [left, bisect_right(nums, target) - 1]
    """, SORTED_TARGET_CASES, 5, "O(log n)", "O(1)", "The duplicate block is bounded by lower and upper insertion positions.", "Find both boundaries and verify the target exists at the lower one."),
    S("sorted-target-count", "Count Sorted Target", "Return how many times target occurs in a sorted list.", ["binary-search", "arrays"], "sorted_target_count", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        from bisect import bisect_left, bisect_right
        return bisect_right(nums, target) - bisect_left(nums, target)
    """, SORTED_TARGET_CASES, 4, "O(log n)", "O(1)", "Occurrence count is the width between two insertion boundaries.", "Subtract lower bound from upper bound."),
)

# A value plus k produces selecting, windowing, counting, and rotation problems.
add(
    S("kth-largest-value", "Kth Largest Value", "Return the kth largest value, counting duplicate positions separately.", ["heaps", "selection"], "kth_largest_value", [("nums", "list[int]", "raw"), ("k", "int", "raw")], "int", "return sorted(nums, reverse=True)[k - 1]", ARRAY_K_CASES, 4, "O(n log n)", "O(n)", "Kth refers to sorted position, not kth distinct value.", "Order values descending and select index k-1."),
    S("maximum-fixed-window-sum", "Maximum Fixed Window Sum", "Return the largest sum among contiguous windows of exactly k values.", ["sliding-window", "arrays"], "maximum_fixed_window_sum", [("nums", "list[int]", "raw"), ("k", "int", "raw")], "int", """
        window = sum(nums[:k]); best = window
        for i in range(k, len(nums)):
            window += nums[i] - nums[i - k]; best = max(best, window)
        return best
    """, ARRAY_K_CASES, 4, "O(n)", "O(1)", "Adjacent fixed windows differ by one entering and one leaving value.", "Update the sum in constant time as the right edge advances."),
    S("distinct-count-per-window", "Distinct Count Per Window", "Return the number of distinct values in every contiguous window of size k.", ["sliding-window", "hash-maps"], "distinct_count_per_window", [("nums", "list[int]", "raw"), ("k", "int", "raw")], "list[int]", """
        from collections import Counter
        counts = Counter(nums[:k]); answer = [len(counts)]
        for i in range(k, len(nums)):
            leaving = nums[i - k]; counts[leaving] -= 1
            if counts[leaving] == 0: del counts[leaving]
            counts[nums[i]] += 1; answer.append(len(counts))
        return answer
    """, ARRAY_K_CASES, 5, "O(n)", "O(k)", "A frequency map tells when a value enters or leaves the distinct set.", "Update counts for one outgoing and one incoming value per window."),
    S("rotate-values-right", "Rotate Values Right", "Return the list rotated right by k positions.", ["arrays", "modular-arithmetic"], "rotate_values_right", [("nums", "list[int]", "raw"), ("k", "int", "raw")], "list[int]", """
        if not nums: return []
        k %= len(nums)
        return nums[-k:] + nums[:-k] if k else nums[:]
    """, ARRAY_K_CASES, 3, "O(n)", "O(n)", "Rotation counts wrap modulo the list length.", "Normalize k, then join the suffix and prefix at the cut."),
)

# Interval scheduling and sweep-line questions.
add(
    S("minimum-meeting-rooms", "Minimum Meeting Rooms", "Return the minimum number of rooms needed for half-open meeting intervals.", ["intervals", "heaps"], "minimum_meeting_rooms", [("intervals", "list[list[int]]", "raw")], "int", """
        import heapq
        heap = []
        for start, end in sorted(intervals):
            if heap and heap[0] <= start: heapq.heapreplace(heap, end)
            else: heapq.heappush(heap, end)
        return len(heap)
    """, INTERVAL_CASES, 5, "O(n log n)", "O(n)", "Only the earliest finishing active meeting determines room reuse.", "Sort by start and maintain a min-heap of current end times."),
    S("erase-overlapping-intervals", "Erase Overlapping Intervals", "Return the fewest intervals to remove so the rest do not overlap.", ["intervals", "greedy"], "erase_overlapping_intervals", [("intervals", "list[list[int]]", "raw")], "int", """
        removed, end = 0, float('-inf')
        for start, finish in sorted(intervals, key=lambda item: item[1]):
            if start < end: removed += 1
            else: end = finish
        return removed
    """, INTERVAL_CASES, 5, "O(n log n)", "O(1)", "Keeping the interval that ends earliest leaves the most future room.", "Sort by end and greedily keep every compatible interval."),
    S("total-covered-length", "Total Covered Length", "Return the total length covered by the union of half-open intervals.", ["intervals", "sorting"], "total_covered_length", [("intervals", "list[list[int]]", "raw")], "int", """
        total = 0; start = end = None
        for left, right in sorted(intervals):
            if start is None: start, end = left, right
            elif left > end: total += end - start; start, end = left, right
            else: end = max(end, right)
        return total + (0 if start is None else end - start)
    """, INTERVAL_CASES, 4, "O(n log n)", "O(1)", "Overlapping intervals contribute only their combined outer span.", "Sort, extend the current union segment, and add it when a gap begins."),
    S("maximum-interval-overlap", "Maximum Interval Overlap", "Return the largest number of half-open intervals active simultaneously.", ["intervals", "sweep-line"], "maximum_interval_overlap", [("intervals", "list[list[int]]", "raw")], "int", """
        events = []
        for start, end in intervals: events.extend([(start, 1), (end, -1)])
        active = best = 0
        for _, delta in sorted(events, key=lambda event: (event[0], event[1])):
            active += delta; best = max(best, active)
        return best
    """, INTERVAL_CASES, 5, "O(n log n)", "O(n)", "At equal times, half-open intervals end before others start.", "Sort start and end events with end events first, then track active count."),
)

# Matrix traversal and transformation.
add(
    S("matrix-spiral-order", "Matrix Spiral Order", "Return square-matrix values in clockwise spiral order.", ["matrices", "simulation"], "matrix_spiral_order", [("matrix", "list[list[int]]", "raw")], "list[int]", """
        if not matrix or not matrix[0]: return []
        top, bottom, left, right, answer = 0, len(matrix)-1, 0, len(matrix[0])-1, []
        while top <= bottom and left <= right:
            answer.extend(matrix[top][left:right+1]); top += 1
            for row in range(top, bottom+1): answer.append(matrix[row][right])
            right -= 1
            if top <= bottom: answer.extend(reversed(matrix[bottom][left:right+1])); bottom -= 1
            if left <= right:
                for row in range(bottom, top-1, -1): answer.append(matrix[row][left])
                left += 1
        return answer
    """, MATRIX_CASES, 5, "O(n²)", "O(1) excluding output", "Four shrinking boundaries define the unvisited rectangle.", "Read top, right, bottom, and left edges while checking boundary crossings."),
    S("transpose-square-matrix", "Transpose Square Matrix", "Return the matrix reflected across its main diagonal.", ["matrices"], "transpose_square_matrix", [("matrix", "list[list[int]]", "raw")], "list[list[int]]", """
        if not matrix or not matrix[0]: return []
        return [list(row) for row in zip(*matrix)]
    """, MATRIX_CASES, 3, "O(n²)", "O(n²)", "Transposition swaps row and column coordinates.", "Build each output row from one input column."),
    S("matrix-diagonal-sum", "Matrix Diagonal Sum", "Return the sum of both square-matrix diagonals without double-counting the center.", ["matrices"], "matrix_diagonal_sum", [("matrix", "list[list[int]]", "raw")], "int", """
        if not matrix or not matrix[0]: return 0
        n = len(matrix)
        return sum(matrix[i][i] + matrix[i][n-1-i] for i in range(n)) - (matrix[n//2][n//2] if n % 2 else 0)
    """, MATRIX_CASES, 3, "O(n)", "O(1)", "Odd-sized matrices share one center across both diagonals.", "Add symmetric diagonal entries per row and subtract the center once when needed."),
    S("missing-repeated-grid-values", "Missing and Repeated Grid Values", "A square grid should contain every value from 1 through n² once; return [repeated, missing].", ["matrices", "hash-maps"], "missing_repeated_grid_values", [("grid", "list[list[int]]", "raw")], "list[int]", """
        from collections import Counter
        counts = Counter(value for row in grid for value in row)
        limit = len(grid) ** 2
        repeated = next(value for value, count in counts.items() if count == 2)
        missing = next(value for value in range(1, limit + 1) if counts[value] == 0)
        return [repeated, missing]
    """, MISSING_GRID_CASES, 3, "O(n²)", "O(n²)", "The expected value range supplies the missing candidate while frequencies identify the duplicate.", "Count all cells, find the value with frequency two, then scan 1 through n² for frequency zero."),
)

# Binary-grid geometry and connectivity.
add(
    S("largest-land-region", "Largest Land Region", "Return the largest four-directionally connected area of 1-cells.", ["graphs", "depth-first-search", "matrices"], "largest_land_region", [("grid", "list[list[int]]", "raw")], "int", """
        if not grid or not grid[0]: return 0
        seen = set()
        def area(r, c):
            if not (0 <= r < len(grid) and 0 <= c < len(grid[0])) or not grid[r][c] or (r,c) in seen: return 0
            seen.add((r,c)); return 1 + area(r+1,c) + area(r-1,c) + area(r,c+1) + area(r,c-1)
        return max((area(r,c) for r in range(len(grid)) for c in range(len(grid[0]))), default=0)
    """, BINARY_GRID_CASES, 5, "O(rc)", "O(rc)", "Each connected component can be measured by one recursive flood fill.", "Mark each land cell once and sum the four neighboring recursive areas."),
    S("land-perimeter", "Land Perimeter", "Return the total exposed edge count of all 1-cells.", ["matrices", "geometry"], "land_perimeter", [("grid", "list[list[int]]", "raw")], "int", """
        if not grid or not grid[0]: return 0
        perimeter = 0
        for r, row in enumerate(grid):
            for c, value in enumerate(row):
                if value:
                    perimeter += 4
                    if r and grid[r-1][c]: perimeter -= 2
                    if c and grid[r][c-1]: perimeter -= 2
        return perimeter
    """, BINARY_GRID_CASES, 4, "O(rc)", "O(1)", "Every shared side removes two exposed edges.", "Add four per land cell and subtract shared top and left edges once."),
    S("enclaved-land-count", "Enclaved Land Count", "Count land cells that cannot reach the grid boundary through land.", ["graphs", "depth-first-search", "matrices"], "enclaved_land_count", [("grid", "list[list[int]]", "raw")], "int", """
        if not grid or not grid[0]: return 0
        seen = set()
        def visit(r,c):
            if not (0 <= r < len(grid) and 0 <= c < len(grid[0])) or not grid[r][c] or (r,c) in seen: return
            seen.add((r,c)); visit(r+1,c); visit(r-1,c); visit(r,c+1); visit(r,c-1)
        for r in range(len(grid)): visit(r,0); visit(r,len(grid[0])-1)
        for c in range(len(grid[0])): visit(0,c); visit(len(grid)-1,c)
        return sum(grid[r][c] and (r,c) not in seen for r in range(len(grid)) for c in range(len(grid[0])))
    """, BINARY_GRID_CASES, 6, "O(rc)", "O(rc)", "Only land connected to a boundary can escape.", "Flood-fill from every boundary land cell, then count unvisited land."),
    S("flood-fill-region", "Flood Fill Region", "Recolor the four-directionally connected region containing a starting cell and return the image.", ["graphs", "recursion", "matrices"], "flood_fill_region", [("image", "list[list[int]]", "raw"), ("start_row", "int", "raw"), ("start_col", "int", "raw"), ("new_color", "int", "raw")], "list[list[int]]", """
        original = image[start_row][start_col]
        if original == new_color: return image
        def fill(row, col):
            if not (0 <= row < len(image) and 0 <= col < len(image[0])) or image[row][col] != original: return
            image[row][col] = new_color
            fill(row + 1, col); fill(row - 1, col); fill(row, col + 1); fill(row, col - 1)
        fill(start_row, start_col)
        return image
    """, FLOOD_FILL_CASES, 3, "O(rc)", "O(rc)", "Only cells connected through the original color belong to the starting region.", "Save the original color, guard the no-change case, then recursively recolor matching four-directional neighbors."),
)

# Directed-graph ordering, cycles, reachability, and shortest paths.
add(
    S("lexicographic-topological-order", "Lexicographic Topological Order", "Return the smallest valid topological ordering, or an empty list for a cycle.", ["graphs", "topological-sort", "heaps"], "lexicographic_topological_order", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "list[int]", """
        import heapq
        graph = [[] for _ in range(node_count)]; degree = [0] * node_count
        for start, end in edges: graph[start].append(end); degree[end] += 1
        heap = [node for node in range(node_count) if degree[node] == 0]; heapq.heapify(heap); order = []
        while heap:
            node = heapq.heappop(heap); order.append(node)
            for neighbor in graph[node]:
                degree[neighbor] -= 1
                if degree[neighbor] == 0: heapq.heappush(heap, neighbor)
        return order if len(order) == node_count else []
    """, DIRECTED_GRAPH_CASES, 8, "O((V+E) log V)", "O(V+E)", "Zero-indegree nodes are the currently legal next choices.", "Use Kahn's algorithm with a min-heap to make the valid order deterministic."),
    S("directed-cycle-check", "Directed Cycle Check", "Return whether a directed graph contains a cycle.", ["graphs", "depth-first-search", "recursion"], "directed_cycle_check", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "bool", """
        graph = [[] for _ in range(node_count)]
        for start, end in edges: graph[start].append(end)
        state = [0] * node_count
        def visit(node):
            if state[node] == 1: return True
            if state[node] == 2: return False
            state[node] = 1
            if any(visit(neighbor) for neighbor in graph[node]): return True
            state[node] = 2; return False
        return any(visit(node) for node in range(node_count) if state[node] == 0)
    """, DIRECTED_GRAPH_CASES, 6, "O(V+E)", "O(V)", "A back edge reaches a node still on the active recursive path.", "Use three states: unseen, visiting, and completely processed."),
    S("reachable-from-zero", "Reachable From Zero", "Return the number of directed-graph nodes reachable from node 0.", ["graphs", "breadth-first-search"], "reachable_from_zero", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "int", """
        from collections import deque
        graph = [[] for _ in range(node_count)]
        for start, end in edges: graph[start].append(end)
        seen = {0}; queue = deque([0])
        while queue:
            for neighbor in graph[queue.popleft()]:
                if neighbor not in seen: seen.add(neighbor); queue.append(neighbor)
        return len(seen)
    """, DIRECTED_GRAPH_CASES, 4, "O(V+E)", "O(V)", "Reachability visits each discovered node once.", "Traverse outward from zero while marking nodes when enqueued."),
    S("shortest-directed-hops", "Shortest Directed Hops", "Return the fewest directed edges from node 0 to the last node, or -1.", ["graphs", "breadth-first-search"], "shortest_directed_hops", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "int", """
        from collections import deque
        graph = [[] for _ in range(node_count)]
        for start, end in edges: graph[start].append(end)
        queue = deque([(0,0)]); seen = {0}
        while queue:
            node, distance = queue.popleft()
            if node == node_count - 1: return distance
            for neighbor in graph[node]:
                if neighbor not in seen: seen.add(neighbor); queue.append((neighbor,distance+1))
        return -1
    """, DIRECTED_GRAPH_CASES, 5, "O(V+E)", "O(V)", "Equal-cost edges make breadth-first layers equal hop counts.", "BFS from zero and return the distance on first reaching the final node."),
)

# Undirected-graph structure.
add(
    S("undirected-component-count", "Undirected Component Count", "Return the number of connected components in an undirected graph.", ["graphs", "depth-first-search"], "undirected_component_count", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "int", """
        graph = [[] for _ in range(node_count)]
        for a,b in edges: graph[a].append(b); graph[b].append(a)
        seen = set(); components = 0
        for start in range(node_count):
            if start in seen: continue
            components += 1; stack = [start]; seen.add(start)
            while stack:
                for neighbor in graph[stack.pop()]:
                    if neighbor not in seen: seen.add(neighbor); stack.append(neighbor)
        return components
    """, UNDIRECTED_GRAPH_CASES, 4, "O(V+E)", "O(V)", "Every traversal started from an unseen node discovers exactly one component.", "Scan nodes and launch DFS only from nodes not already visited."),
    S("bipartite-graph-check", "Bipartite Graph Check", "Return whether an undirected graph can be colored with two colors across every edge.", ["graphs", "breadth-first-search"], "bipartite_graph_check", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "bool", """
        from collections import deque
        graph = [[] for _ in range(node_count)]
        for a,b in edges: graph[a].append(b); graph[b].append(a)
        color = {}
        for start in range(node_count):
            if start in color: continue
            color[start] = 0; queue = deque([start])
            while queue:
                node = queue.popleft()
                for neighbor in graph[node]:
                    if neighbor not in color: color[neighbor] = 1-color[node]; queue.append(neighbor)
                    elif color[neighbor] == color[node]: return False
        return True
    """, UNDIRECTED_GRAPH_CASES, 6, "O(V+E)", "O(V)", "Every edge must connect opposite colors, including across disconnected components.", "BFS each component and assign the opposite color to unseen neighbors."),
    S("undirected-terminal-path", "Undirected Terminal Path", "Return whether node 0 is connected to the last node.", ["graphs", "depth-first-search"], "undirected_terminal_path", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "bool", """
        graph = [[] for _ in range(node_count)]
        for a,b in edges: graph[a].append(b); graph[b].append(a)
        stack = [0]; seen = {0}
        while stack:
            node = stack.pop()
            if node == node_count - 1: return True
            for neighbor in graph[node]:
                if neighbor not in seen: seen.add(neighbor); stack.append(neighbor)
        return False
    """, UNDIRECTED_GRAPH_CASES, 3, "O(V+E)", "O(V)", "Connectivity needs any path, not the shortest path.", "Traverse from zero and stop once the final node is discovered."),
    S("tree-component-count", "Tree Component Count", "Count connected components that are trees in an undirected multigraph.", ["graphs", "trees"], "tree_component_count", [("node_count", "int", "raw"), ("edges", "list[list[int]]", "raw")], "int", """
        graph = [[] for _ in range(node_count)]
        for a,b in edges: graph[a].append(b); graph[b].append(a)
        seen = set(); answer = 0
        for start in range(node_count):
            if start in seen: continue
            stack = [start]; seen.add(start); vertices = edge_ends = 0
            while stack:
                node = stack.pop(); vertices += 1; edge_ends += len(graph[node])
                for neighbor in graph[node]:
                    if neighbor not in seen: seen.add(neighbor); stack.append(neighbor)
            answer += edge_ends // 2 == vertices - 1
        return answer
    """, UNDIRECTED_GRAPH_CASES, 6, "O(V+E)", "O(V)", "A connected undirected component is a tree exactly when edges equal vertices minus one.", "Traverse each component while counting vertices and paired adjacency entries."),
)

# Recursive binary-tree measurements form an easy-to-medium recursion ladder.
add(
    S("recursive-tree-sum", "Recursive Tree Sum", "Return the sum of all binary-tree node values.", ["trees", "recursion"], "recursive_tree_sum", [("root", "TreeNode | None", "treenode")], "int", """
        if root is None: return 0
        return root.val + recursive_tree_sum(root.left) + recursive_tree_sum(root.right)
    """, TREE_CASES, 3, "O(n)", "O(h)", "An empty subtree contributes the additive identity zero.", "Return the node value plus recursive sums from both children."),
    S("recursive-leaf-count", "Recursive Leaf Count", "Return the number of nodes with no children.", ["trees", "recursion"], "recursive_leaf_count", [("root", "TreeNode | None", "treenode")], "int", """
        if root is None: return 0
        if root.left is None and root.right is None: return 1
        return recursive_leaf_count(root.left) + recursive_leaf_count(root.right)
    """, TREE_CASES, 3, "O(n)", "O(h)", "A leaf is a nonempty node whose two child subproblems are both empty.", "Handle empty and leaf base cases, then add child counts."),
    S("recursive-minimum-tree-depth", "Recursive Minimum Tree Depth", "Return the shortest root-to-leaf node count, with 0 for an empty tree.", ["trees", "recursion"], "recursive_minimum_tree_depth", [("root", "TreeNode | None", "treenode")], "int", """
        if root is None: return 0
        if root.left is None: return 1 + recursive_minimum_tree_depth(root.right)
        if root.right is None: return 1 + recursive_minimum_tree_depth(root.left)
        return 1 + min(recursive_minimum_tree_depth(root.left), recursive_minimum_tree_depth(root.right))
    """, TREE_CASES, 5, "O(n)", "O(h)", "A missing child is not a zero-length path to a leaf.", "Treat one-child nodes separately, then take the smaller depth when both children exist."),
    S("tree-right-side-view", "Tree Right-Side View", "Return the value visible from the right at every tree depth.", ["trees", "recursion", "depth-first-search"], "tree_right_side_view", [("root", "TreeNode | None", "treenode")], "list[int]", """
        answer = []
        def visit(node, depth):
            if node is None: return
            if depth == len(answer): answer.append(node.val)
            visit(node.right, depth+1); visit(node.left, depth+1)
        visit(root, 0); return answer
    """, TREE_CASES, 5, "O(n)", "O(h)", "A right-first traversal sees each depth's visible node first.", "Append only on the first visit to a new depth, exploring right before left."),
)

# Linked-list questions use adapters but ask unrelated operations.
add(
    S("deduplicate-sorted-linked-list", "Deduplicate a Sorted Linked List", "Remove repeated values from a sorted linked list in place and return its head.", ["linked-lists", "pointer-manipulation"], "deduplicate_sorted_linked_list", [("head", "ListNode | None", "listnode")], "ListNode | None", """
        current = head
        while current and current.next:
            if current.val == current.next.val: current.next = current.next.next
            else: current = current.next
        return head
    """, SORTED_LINKED_CASES, 3, "O(n)", "O(1)", "Sorting makes duplicate nodes adjacent, so one pointer can remove repeats without extra storage.", "Compare each node with its successor; bypass equal successors and advance only after the next value changes.", return_adapter="listnode"),
    S("linked-middle-value", "Linked Middle Value", "Return the second middle value for even length, or None for an empty list.", ["linked-lists", "two-pointers"], "linked_middle_value", [("head", "ListNode | None", "listnode")], "int | None", """
        slow = fast = head
        while fast and fast.next: slow = slow.next; fast = fast.next.next
        return None if slow is None else slow.val
    """, LINKED_CASES, 3, "O(n)", "O(1)", "A pointer moving twice as fast makes the slow pointer stop in the middle.", "Advance slow once and fast twice until fast reaches the end."),
    S("linked-palindrome-check", "Linked Palindrome Check", "Return whether linked-list values read identically forward and backward.", ["linked-lists"], "linked_palindrome_check", [("head", "ListNode | None", "listnode")], "bool", """
        values = []
        while head: values.append(head.val); head = head.next
        return values == values[::-1]
    """, LINKED_CASES, 3, "O(n)", "O(n)", "A linear copy makes reverse-order comparison explicit.", "Collect values, then compare the sequence with its reverse."),
    S("linked-odd-even-order", "Linked Odd-Even Order", "Reorder nodes by odd positions followed by even positions and return the head.", ["linked-lists", "pointer-manipulation"], "linked_odd_even_order", [("head", "ListNode | None", "listnode")], "ListNode | None", """
        if head is None or head.next is None: return head
        odd, even, even_head = head, head.next, head.next
        while even and even.next:
            odd.next = even.next; odd = odd.next
            even.next = odd.next; even = even.next
        odd.next = even_head
        return head
    """, LINKED_CASES, 5, "O(n)", "O(1)", "Maintain two linked chains without changing relative order inside either chain.", "Advance odd and even tails by rewiring alternating next pointers, then join the chains.", return_adapter="listnode"),
)

# Monotonic-stack problems over nonnegative heights.
add(
    S("next-greater-values", "Next Greater Values", "For each value, return the first strictly greater value to its right, or -1.", ["stacks", "arrays"], "next_greater_values", [("nums", "list[int]", "raw")], "list[int]", """
        answer = [-1] * len(nums); stack = []
        for i, value in enumerate(nums):
            while stack and nums[stack[-1]] < value: answer[stack.pop()] = value
            stack.append(i)
        return answer
    """, HEIGHT_CASES, 4, "O(n)", "O(n)", "A decreasing stack keeps values still waiting for a greater neighbor.", "Pop and resolve every smaller pending value when a greater value arrives."),
    S("previous-smaller-values", "Previous Smaller Values", "For each value, return the nearest strictly smaller value to its left, or -1.", ["stacks", "arrays"], "previous_smaller_values", [("nums", "list[int]", "raw")], "list[int]", """
        stack = []; answer = []
        for value in nums:
            while stack and stack[-1] >= value: stack.pop()
            answer.append(stack[-1] if stack else -1); stack.append(value)
        return answer
    """, HEIGHT_CASES, 4, "O(n)", "O(n)", "Values that are not smaller can never answer the current or later query first.", "Pop larger-or-equal candidates, read the stack top, then push the current value."),
    S("largest-histogram-rectangle", "Largest Histogram Rectangle", "Return the maximum rectangular area under adjacent histogram bars.", ["stacks", "arrays"], "largest_histogram_rectangle", [("heights", "list[int]", "raw")], "int", """
        stack = []; best = 0
        for i, height in enumerate(heights + [0]):
            start = i
            while stack and stack[-1][1] > height:
                index, old = stack.pop(); best = max(best, old * (i-index)); start = index
            stack.append((start, height))
        return best
    """, HEIGHT_CASES, 8, "O(n)", "O(n)", "A lower bar closes every taller rectangle that cannot extend farther.", "Store each height with its earliest valid start and finalize it when a smaller height appears."),
    S("sum-subarray-minimums", "Sum of Subarray Minimums", "Return the sum of every contiguous subarray minimum.", ["stacks", "dynamic-programming"], "sum_subarray_minimums", [("nums", "list[int]", "raw")], "int", """
        stack = []; total = ending = 0
        for value in nums:
            count = 1
            while stack and stack[-1][0] >= value:
                old, old_count = stack.pop(); count += old_count; ending -= old * old_count
            stack.append((value,count)); ending += value * count; total += ending
        return total
    """, HEIGHT_CASES, 8, "O(n)", "O(n)", "Count how many subarrays ending here choose each stack value as their minimum.", "Merge dominated minima and maintain the sum for all subarrays ending at the current position."),
)

# Classic one-dimensional dynamic programming.
add(
    S("maximum-contiguous-sum", "Maximum Contiguous Sum", "Return the largest sum of a nonempty contiguous subarray, or 0 for empty input.", ["dynamic-programming", "arrays"], "maximum_contiguous_sum", [("nums", "list[int]", "raw")], "int", """
        if not nums: return 0
        ending = best = nums[0]
        for value in nums[1:]: ending = max(value, ending + value); best = max(best, ending)
        return best
    """, ARRAY_CASES, 4, "O(n)", "O(1)", "The best subarray ending here either starts here or extends the previous one.", "Carry the best ending sum and the global best."),
    S("nonadjacent-maximum-sum", "Nonadjacent Maximum Sum", "Return the largest sum obtainable without choosing adjacent values.", ["dynamic-programming", "arrays"], "nonadjacent_maximum_sum", [("nums", "list[int]", "raw")], "int", """
        skip = take = 0
        for value in nums: skip, take = max(skip,take), skip + value
        return max(skip,take)
    """, ARRAY_CASES, 5, "O(n)", "O(1)", "Each position has take and skip states based on the prior position.", "Update the best sum excluding or including the current value."),
    S("increasing-subsequence-length", "Increasing Subsequence Length", "Return the length of the longest strictly increasing subsequence.", ["dynamic-programming", "binary-search"], "increasing_subsequence_length", [("nums", "list[int]", "raw")], "int", """
        from bisect import bisect_left
        tails = []
        for value in nums:
            index = bisect_left(tails, value)
            if index == len(tails): tails.append(value)
            else: tails[index] = value
        return len(tails)
    """, ARRAY_CASES, 8, "O(n log n)", "O(n)", "Smallest possible tail values leave the most room for future extension.", "Binary-search the first tail not smaller than each value and replace it."),
    S("minimum-stair-cost", "Minimum Stair Cost", "Given per-step costs, return the minimum cost to move beyond the final step using jumps of one or two.", ["dynamic-programming", "arrays"], "minimum_stair_cost", [("costs", "list[int]", "raw")], "int", """
        previous_two = previous_one = 0
        for cost in costs: previous_two, previous_one = previous_one, cost + min(previous_one, previous_two)
        return min(previous_one, previous_two)
    """, ARRAY_CASES, 4, "O(n)", "O(1)", "Reaching a step depends only on the cheaper of the prior two positions.", "Roll two DP values forward and finish from either of the last two steps."),
)

# Four different coin-state questions.
add(
    S("minimum-unbounded-coins", "Minimum Unbounded Coins", "Return the fewest reusable coins needed for amount, or -1.", ["dynamic-programming"], "minimum_unbounded_coins", [("coins", "list[int]", "raw"), ("amount", "int", "raw")], "int", """
        best = [amount + 1] * (amount + 1); best[0] = 0
        for value in range(1, amount + 1):
            for coin in coins:
                if coin <= value: best[value] = min(best[value], 1 + best[value-coin])
        return -1 if best[amount] > amount else best[amount]
    """, COIN_CASES, 5, "O(amount·coins)", "O(amount)", "Every reachable amount extends a smaller reachable amount by one coin.", "Compute the minimum count for amounts from zero upward."),
    S("unbounded-coin-combinations", "Unbounded Coin Combinations", "Return the number of order-independent ways reusable coin values can form amount.", ["dynamic-programming"], "unbounded_coin_combinations", [("coins", "list[int]", "raw"), ("amount", "int", "raw")], "int", """
        ways = [0] * (amount + 1); ways[0] = 1
        for coin in sorted(set(coins)):
            for value in range(coin, amount + 1): ways[value] += ways[value-coin]
        return ways[amount]
    """, COIN_CASES, 6, "O(amount·coins)", "O(amount)", "Processing coin types outside the amount loop avoids counting different orders separately.", "For each distinct coin, add ways from amount-coin into larger amounts."),
    S("exact-coin-reachability", "Exact Coin Reachability", "Return whether reusable coins can form amount exactly.", ["dynamic-programming"], "exact_coin_reachability", [("coins", "list[int]", "raw"), ("amount", "int", "raw")], "bool", """
        reachable = [True] + [False] * amount
        for value in range(1, amount + 1): reachable[value] = any(coin <= value and reachable[value-coin] for coin in coins)
        return reachable[amount]
    """, COIN_CASES, 3, "O(amount·coins)", "O(amount)", "An amount is reachable when subtracting one allowed coin reaches a known state.", "Build a boolean table from zero through the target."),
    S("minimum-single-use-coins", "Minimum Single-Use Coins", "Return the fewest listed coin occurrences that form amount, or -1.", ["dynamic-programming", "knapsack"], "minimum_single_use_coins", [("coins", "list[int]", "raw"), ("amount", "int", "raw")], "int", """
        best = [amount + 1] * (amount + 1); best[0] = 0
        for coin in coins:
            for value in range(amount, coin-1, -1): best[value] = min(best[value], 1 + best[value-coin])
        return -1 if best[amount] > len(coins) else best[amount]
    """, COIN_CASES, 6, "O(amount·coins)", "O(amount)", "Descending amount order prevents one coin occurrence from being reused in its own iteration.", "Apply 0/1 knapsack updates from amount down to coin."),
)

# Recursive generation and backtracking, including an advanced recursion problem.
add(
    S("unique-text-permutations", "Unique Text Permutations", "Return all distinct permutations of the input text.", ["backtracking", "recursion", "strings"], "unique_text_permutations", [("text", "str", "raw")], "list[str]", """
        answer = []
        def build(prefix, remaining):
            if not remaining: answer.append(prefix); return
            for i, char in enumerate(remaining):
                if i and char == remaining[i-1]: continue
                build(prefix+char, remaining[:i]+remaining[i+1:])
        build("", "".join(sorted(text))); return answer
    """, SMALL_TEXT_CASES, 6, "O(n·n!)", "O(n)", "Sorting makes equal choices adjacent so one recursion level can skip duplicates.", "Choose each distinct remaining character, recurse, and restore via immutable slices.", comparator="unordered"),
    S("unique-text-subsequences", "Unique Text Subsequences", "Return every distinct subsequence, including the empty string.", ["backtracking", "recursion", "strings"], "unique_text_subsequences", [("text", "str", "raw")], "list[str]", """
        values = set()
        def build(index, path):
            if index == len(text): values.add(path); return
            build(index+1, path); build(index+1, path+text[index])
        build(0, ""); return sorted(values)
    """, SMALL_TEXT_CASES, 5, "O(2ⁿ)", "O(2ⁿ)", "Every character creates include and exclude recursive branches.", "Recurse on the next index twice and deduplicate completed strings.", comparator="unordered"),
    S("palindrome-partitions", "Palindrome Partitions", "Return every partition of the text into palindromic pieces.", ["backtracking", "recursion", "strings"], "palindrome_partitions", [("text", "str", "raw")], "list[list[str]]", """
        answer = []
        def build(start, path):
            if start == len(text): answer.append(path[:]); return
            for end in range(start+1, len(text)+1):
                piece = text[start:end]
                if piece == piece[::-1]: path.append(piece); build(end,path); path.pop()
        build(0, []); return answer
    """, SMALL_TEXT_CASES, 8, "O(n·2ⁿ)", "O(n)", "A valid recursion edge consumes one palindromic prefix of the remaining suffix.", "Try every end position, recurse only for palindromic pieces, and backtrack the path."),
    S("letter-case-variations", "Letter Case Variations", "Return every string formed by independently toggling each letter's case.", ["backtracking", "recursion", "strings"], "letter_case_variations", [("text", "str", "raw")], "list[str]", """
        answer = []
        def build(index, path):
            if index == len(text): answer.append(path); return
            char = text[index]
            if char.isalpha(): build(index+1, path+char.lower()); build(index+1, path+char.upper())
            else: build(index+1, path+char)
        build(0, ""); return answer
    """, SMALL_TEXT_CASES, 4, "O(2ˡ)", "O(n)", "Letters branch into lower and upper choices while nonletters have one branch.", "Advance one position per recursive call and append at the text-length base case."),
)

# Greedy and sequence reasoning.
add(
    S("increasing-triplet-exists", "Increasing Triplet Exists", "Return whether three indices form a strictly increasing subsequence.", ["greedy", "arrays"], "increasing_triplet_exists", [("nums", "list[int]", "raw")], "bool", """
        first = second = float('inf')
        for value in nums:
            if value <= first: first = value
            elif value <= second: second = value
            else: return True
        return False
    """, ARRAY_CASES, 5, "O(n)", "O(1)", "The smallest first and second values maximize the chance of a later third.", "Greedily lower the first two thresholds and succeed when a value exceeds both."),
    S("maximum-circular-subarray", "Maximum Circular Subarray", "Return the greatest nonempty subarray sum when the ends are adjacent, or 0 for empty input.", ["dynamic-programming", "arrays"], "maximum_circular_subarray", [("nums", "list[int]", "raw")], "int", """
        if not nums: return 0
        total = sum(nums); max_end = min_end = max_best = min_best = nums[0]
        for value in nums[1:]:
            max_end = max(value, max_end+value); max_best = max(max_best,max_end)
            min_end = min(value, min_end+value); min_best = min(min_best,min_end)
        return max_best if max_best < 0 else max(max_best, total-min_best)
    """, ARRAY_CASES, 6, "O(n)", "O(1)", "A wrapping maximum equals total sum minus a minimum middle segment.", "Compare the ordinary maximum with total minus the minimum, guarding the all-negative case."),
    S("minimum-increments-unique", "Minimum Increments for Uniqueness", "Return the fewest +1 operations needed to make all values distinct.", ["greedy", "sorting"], "minimum_increments_unique", [("nums", "list[int]", "raw")], "int", """
        moves = 0; next_allowed = float('-inf')
        for value in sorted(nums):
            placed = max(value, next_allowed); moves += placed-value; next_allowed = placed+1
        return moves
    """, ARRAY_CASES, 5, "O(n log n)", "O(n)", "In sorted order, the cheapest legal placement is one above the previous placement.", "Place each value at max(original, next_allowed) and accumulate its movement."),
    S("three-equal-sum-parts", "Three Equal-Sum Parts", "Return whether the list can be split into three nonempty contiguous parts with equal sums.", ["greedy", "prefix-sums"], "three_equal_sum_parts", [("nums", "list[int]", "raw")], "bool", """
        total = sum(nums)
        if len(nums) < 3 or total % 3: return False
        target = total // 3; running = parts = 0
        for i, value in enumerate(nums[:-1]):
            running += value
            if running == target: parts += 1; running = 0
            if parts == 2 and i < len(nums)-1: return True
        return False
    """, ARRAY_CASES, 5, "O(n)", "O(1)", "After finding two target-sum prefixes, the remaining suffix must have the third target sum.", "Scan only through the penultimate value and reset the running sum after each completed part."),
)

# Hash-map and prefix-sum questions with a numeric target.
add(
    S("target-subarray-count", "Target Subarray Count", "Count contiguous subarrays whose sum equals target.", ["prefix-sums", "hash-maps"], "target_subarray_count", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        from collections import defaultdict
        counts = defaultdict(int, {0:1}); prefix = answer = 0
        for value in nums: prefix += value; answer += counts[prefix-target]; counts[prefix] += 1
        return answer
    """, TARGET_CASES, 5, "O(n)", "O(n)", "A target-sum subarray exists between prefixes differing by target.", "Count previous prefix sums and query prefix-target at each position."),
    S("target-pair-count", "Target Pair Count", "Count index pairs i < j whose values sum to target.", ["hash-maps", "arrays"], "target_pair_count", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        from collections import defaultdict
        counts = defaultdict(int); answer = 0
        for value in nums: answer += counts[target-value]; counts[value] += 1
        return answer
    """, TARGET_CASES, 4, "O(n)", "O(n)", "Every previous complement forms one pair with the current value.", "Add the stored complement frequency before storing the current value."),
    S("longest-target-sum-subarray", "Longest Target-Sum Subarray", "Return the maximum length of a contiguous subarray summing to target.", ["prefix-sums", "hash-maps"], "longest_target_sum_subarray", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", """
        earliest = {0:-1}; prefix = best = 0
        for i, value in enumerate(nums):
            prefix += value
            if prefix-target in earliest: best = max(best, i-earliest[prefix-target])
            earliest.setdefault(prefix, i)
        return best
    """, TARGET_CASES, 6, "O(n)", "O(n)", "The earliest matching prefix produces the longest ending subarray.", "Store each prefix only on first occurrence and compare against prefix-target."),
    S("nearest-value-to-target", "Nearest Value to Target", "Return the list value closest to target, choosing the smaller value on ties, or None when empty.", ["arrays"], "nearest_value_to_target", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int | None", "return min(nums, key=lambda value: (abs(value-target), value)) if nums else None", TARGET_CASES, 2, "O(n)", "O(1)", "A tuple key can encode distance first and tie-breaking value second.", "Scan for the minimum (absolute difference, value) pair."),
)

# Explicit recursion foundations progress from easy base cases to memoized recurrence.
add(
    S("recursive-step-combinations", "Recursive Step Combinations", "Return the number of ordered ways to cover n steps using moves of one or two steps.", ["recursion", "dynamic-programming"], "recursive_step_combinations", [("n", "int", "raw")], "int", """
        memo = {0: 1, 1: 1}
        def ways(remaining):
            if remaining not in memo: memo[remaining] = ways(remaining - 1) + ways(remaining - 2)
            return memo[remaining]
        return ways(n)
    """, CLIMB_CASES, 3, "O(n)", "O(n)", "Every valid final move comes from a solution with one or two fewer steps.", "Use the two recursive predecessor states and memoize them so each step count is solved once."),
    S("recursive-digit-sum", "Recursive Digit Sum", "Return the sum of the decimal digits of a nonnegative integer recursively.", ["recursion", "math"], "recursive_digit_sum", [("n", "int", "raw")], "int", """
        if n < 10: return n
        return n % 10 + recursive_digit_sum(n // 10)
    """, RECURSION_CASES, 3, "O(log n)", "O(log n)", "Integer division removes the final digit and modulo reads it.", "Use a single-digit base case, then recurse on n//10."),
    S("recursive-power-of-two", "Recursive Power of Two", "Return 2 raised to nonnegative n using divide-and-conquer recursion.", ["recursion", "divide-and-conquer", "math"], "recursive_power_of_two", [("n", "int", "raw")], "int", """
        if n == 0: return 1
        half = recursive_power_of_two(n // 2)
        return half * half * (2 if n % 2 else 1)
    """, RECURSION_CASES, 4, "O(log n)", "O(log n)", "Even exponents square one half-power; odd exponents need one extra factor.", "Recurse on n//2 once, square the result, and handle parity."),
    S("recursive-catalan-number", "Recursive Catalan Number", "Return the nth Catalan number using memoized recursive splits.", ["recursion", "dynamic-programming", "combinatorics"], "recursive_catalan_number", [("n", "int", "raw")], "int", """
        memo = {0:1}
        def solve(value):
            if value not in memo: memo[value] = sum(solve(left) * solve(value-1-left) for left in range(value))
            return memo[value]
        return solve(n)
    """, RECURSION_CASES, 8, "O(n²)", "O(n)", "Every root choice splits the structure into independent left and right Catalan subproblems.", "Memoize the recurrence that sums products across every split."),
)


DISTINCT_PROBLEMS = [build_problem(spec) for spec in SPECS]

if len(DISTINCT_PROBLEMS) != 76:
    raise ValueError(f"expected 76 distinct additional problems, built {len(DISTINCT_PROBLEMS)}")
