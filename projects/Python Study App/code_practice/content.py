from __future__ import annotations

import copy
import inspect
from dataclasses import dataclass
from typing import Any, Callable

from .content_solutions import ListNode, SOLUTIONS, TreeNode
from .content_oracles import ORACLES
from .example_content import examples_for
from .schemas import (
    DifficultyRubric,
    FunctionSignature,
    ParameterDefinition,
    ProblemDefinition,
    TestCase,
)
from .starter_code import with_support_classes


@dataclass(frozen=True)
class SeedSpec:
    id: str
    title: str
    summary: str
    statement: str
    topics: list[str]
    prerequisites: list[str]
    function_name: str
    parameters: list[tuple[str, str, str]]
    returns: str
    return_adapter: str
    rubric: tuple[int, int, int, int, int]
    minutes: int
    time_complexity: str
    space_complexity: str
    constraints: list[str]
    hints: list[str]
    editorial: str
    example_inputs: list[list[Any]]
    additional_inputs: list[list[Any]]
    comparator: str = "exact"


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


def _expected(spec: SeedSpec, arguments: list[Any]) -> Any:
    solver = SOLUTIONS[spec.function_name]
    adapted = []
    for value, (_name, _annotation, adapter) in zip(copy.deepcopy(arguments), spec.parameters):
        if adapter == "listnode":
            adapted.append(_listnode(value))
        elif adapter == "treenode":
            adapted.append(_treenode(value))
        else:
            adapted.append(value)
    return _serialize(solver(*adapted), spec.return_adapter)


def _starter(spec: SeedSpec) -> str:
    params = ", ".join(f"{name}: {annotation}" for name, annotation, _adapter in spec.parameters)
    if spec.id == "pair-sum-indices":
        source = (
            f"def {spec.function_name}({params}) -> {spec.returns}:\n"
            "    result = []\n"
            "    # Write your solution here. You can run this at any point.\n"
            "    return result\n\n"
            "# Working sample: Run examples to see this result while you build.\n"
            "sample_nums = [2, 7, 11, 15]\n"
            "sample_target = 9\n"
            "print(\"Current result:\", pair_sum_indices(sample_nums, sample_target))\n"
        )
    else:
        source = f"def {spec.function_name}({params}) -> {spec.returns}:\n    # Write your solution here.\n    pass\n"
    adapters = [adapter for _name, _annotation, adapter in spec.parameters]
    adapters.append(spec.return_adapter)
    return with_support_classes(source, adapters)


def _wrong_solutions(spec: SeedSpec) -> list[str]:
    params = ", ".join(name for name, _annotation, _adapter in spec.parameters)
    return [
        f"def {spec.function_name}({params}):\n    return None\n",
        f"def {spec.function_name}({params}):\n    return 0\n",
    ]


def build_problem(spec: SeedSpec) -> ProblemDefinition:
    examples = examples_for(spec.id)
    all_inputs = [arguments for arguments, _explanation in examples] + spec.additional_inputs
    tests = [
        TestCase(
            id=f"{spec.id}-case-{index + 1}",
            arguments=arguments,
            expected=_expected(spec, arguments),
            comparator=spec.comparator,
            visible=True,
            explanation=examples[index][1] if index < len(examples) else None,
        )
        for index, arguments in enumerate(all_inputs)
    ]
    return ProblemDefinition(
        id=spec.id,
        title=spec.title,
        summary=spec.summary,
        statement=spec.statement,
        constraints=spec.constraints,
        topics=spec.topics,
        prerequisites=spec.prerequisites,
        signature=FunctionSignature(
            name=spec.function_name,
            parameters=[ParameterDefinition(name=name, annotation=annotation, adapter=adapter) for name, annotation, adapter in spec.parameters],
            returns=spec.returns,
            return_adapter=spec.return_adapter,
        ),
        starter_code=_starter(spec),
        reference_solution=inspect.getsource(SOLUTIONS[spec.function_name]),
        brute_force_solution=inspect.getsource(ORACLES.get(spec.function_name, SOLUTIONS[spec.function_name])),
        known_wrong_solutions=_wrong_solutions(spec),
        target_time_complexity=spec.time_complexity,
        target_space_complexity=spec.space_complexity,
        estimated_minutes=spec.minutes,
        rubric=DifficultyRubric(
            algorithmic_insight=spec.rubric[0],
            prerequisites=spec.rubric[1],
            implementation=spec.rubric[2],
            performance_pressure=spec.rubric[3],
            edge_cases=spec.rubric[4],
        ),
        hints=spec.hints,
        editorial=spec.editorial,
        tests=tests,
    )


EASY_2 = (1, 0, 1, 0, 0)
EASY_3 = (1, 1, 1, 0, 0)
MEDIUM_4 = (2, 1, 1, 0, 0)
MEDIUM_5 = (2, 1, 1, 1, 0)
MEDIUM_6 = (2, 1, 1, 1, 1)
MEDIUM_7 = (2, 2, 1, 1, 1)
HARD_8 = (3, 2, 1, 1, 1)
HARD_9 = (3, 2, 2, 1, 1)
HARD_10 = (3, 2, 2, 2, 1)


SEEDS = [
    SeedSpec(
        "pair-sum-indices", "Pair Sum Indices", "Find two positions whose values reach a target.",
        "Return the two distinct indices whose values add to `target`. Exactly one solution exists, and the smaller index must come first.",
        ["arrays", "hash-maps"], [], "pair_sum_indices", [("nums", "list[int]", "raw"), ("target", "int", "raw")],
        "list[int]", "raw", EASY_2, 15, "O(n)", "O(n)", ["2 <= len(nums) <= 10,000", "Exactly one valid pair exists."],
        ["Remember values you have already visited.", "For each number, ask whether its complement is already known.", "Store value → index, then return when target - value appears.", "The one-pass hash-map solution uses linear time and space."],
        "Scan once while mapping each value to its index. A complement found in the map identifies the earlier position immediately.",
        [[[2, 7, 11, 15], 9], [[3, 2, 4], 6]],
        [[[3, 3], 6], [[-3, 4, 3, 90], 0], [[1, 8, 2, 7], 9], [[0, 4, 3, 0], 0], [[-1, -2, -3, -4, -5], -8], [[5, 1, 9, 2], 7], [[10, 20, 30, 40], 70], [[100, -20, 5, 15], -5], [[6, 6, 2], 12], [[1, 2, 5, 8, 11], 16], [[-10, 10, 4], 0], [[9, 1, 5, 3], 8]],
    ),
    SeedSpec(
        "valid-brackets", "Bracket Balance", "Validate a sequence of three bracket types.",
        "Return whether every opening bracket is closed by the matching type in last-opened, first-closed order.",
        ["stacks", "strings"], [], "valid_brackets", [("text", "str", "raw")], "bool", "raw", EASY_2, 15, "O(n)", "O(n)",
        ["The text contains only ()[]{}.", "0 <= len(text) <= 20,000"],
        ["Nested structures are naturally last-in, first-out.", "Push openings and compare every closing bracket with the stack top.", "Reject a closer when the stack is empty or the popped opener has the wrong type.", "A stack gives one-pass validation; it must be empty at the end."],
        "Use a stack for opening brackets and a map from closing to opening bracket. Each closer must match the most recent opener.",
        [["()[]{}"], ["([{}])"]],
        [["(]"], ["([)]"], [""], ["{"], ["}"], ["((()))"], ["[({})]"], ["(()"], ["())"], ["{[()()]}"], ["{[(])}"], ["[]{}(()[])"]],
    ),
    SeedSpec(
        "binary-search-index", "Exact Binary Search", "Locate a target in a sorted list.",
        "Return the index of `target` in ascending `nums`, or -1 when it is absent. Values are unique.",
        ["binary-search", "arrays"], [], "binary_search_index", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", "raw", EASY_2, 15, "O(log n)", "O(1)",
        ["0 <= len(nums) <= 100,000", "nums is strictly increasing."],
        ["Discard half of the remaining range after every comparison.", "Keep inclusive left and right boundaries.", "When nums[mid] is too small, move left to mid + 1; otherwise move right.", "The interval closes when left passes right."],
        "Maintain an inclusive search interval. Comparing its middle element determines which half can still contain the target.",
        [[[-1, 0, 3, 5, 9, 12], 9], [[-1, 0, 3, 5, 9, 12], 2]],
        [[[], 1], [[5], 5], [[5], 4], [[1, 2], 1], [[1, 2], 2], [[1, 3, 5, 7], 7], [[1, 3, 5, 7], 0], [[-10, -3, 0, 8], -10], [[-10, -3, 0, 8], 8], [[2, 4, 6, 8, 10], 6], [[2, 4, 6, 8, 10], 9], [[-5, -2, 4, 11, 30], -2]],
    ),
    SeedSpec(
        "reverse-linked-list", "Reverse a Linked List", "Reverse every pointer in a singly linked chain.",
        "Reverse the supplied singly linked list in place and return its new head. The input and output are displayed as arrays.",
        ["linked-lists"], [], "reverse_linked_list", [("head", "ListNode | None", "listnode")], "ListNode | None", "listnode", EASY_3, 20, "O(n)", "O(1)",
        ["0 <= node count <= 10,000", "Node values are integers."],
        ["Each node loses its original next pointer, so save it first.", "Track previous, current, and following nodes.", "Redirect current.next to previous, then advance both pointers.", "The final previous pointer is the new head."],
        "Walk through the chain once, saving the next node before reversing each pointer. No additional list is needed.",
        [[[1, 2, 3, 4]], [[7]]],
        [[[]], [[1, 2]], [[2, 1]], [[-1, 0, 1]], [[5, 5, 5]], [[1, 2, 3, 4, 5]], [[9, 8, 7, 6]], [[0]], [[-3, -2]], [[10, 20, 30]], [[1, -1, 2, -2]], [[100, 50, 0]]],
    ),
    SeedSpec(
        "merge-sorted-linked-lists", "Merge Two Sorted Linked Lists", "Splice two ordered linked chains into one sorted chain.",
        "You are given the heads of two singly linked lists whose values are sorted in nondecreasing order. Merge them by reconnecting the existing nodes, then return the head of the combined sorted list. The interface displays linked lists as arrays, but your function receives `ListNode` objects.",
        ["linked-lists", "two-pointers", "pointer-manipulation"], ["linked-lists"], "merge_sorted_linked_lists", [("list1", "ListNode | None", "listnode"), ("list2", "ListNode | None", "listnode")],
        "ListNode | None", "listnode", EASY_3, 25, "O(n + m)", "O(1)",
        ["0 <= total node count <= 50,000", "Each input list is sorted in nondecreasing order.", "Reuse the supplied nodes rather than allocating a separate node for every value."],
        ["At every step, the smaller current node must come next in the merged chain.", "Use a temporary dummy head so attaching the first real node needs no special case.", "Move a tail pointer forward after linking the smaller of `list1` and `list2`, then attach the nonempty remainder.", "A dummy head and two moving list pointers merge the chains in linear time and constant auxiliary space."],
        "Create a temporary dummy head and keep a tail at the end of the merged portion. Compare the two current node values, connect the tail to the smaller node, and advance only that input. Once either input ends, connect the remaining chain directly because it is already sorted. Return `dummy.next`; only the temporary sentinel is new, while all result nodes come from the inputs.",
        [[[1, 2, 4], [1, 3, 4]], [[], [0]]],
        [[[], []], [[1], []], [[], [-2, 5]], [[1], [2]], [[2], [1]], [[1, 1], [1, 1]], [[-3, 0, 7], [-2, 4, 8]], [[1, 3, 5], [2, 4, 6]], [[1, 2], [3, 4]], [[3, 4], [1, 2]], [[-5, -1], [-6, 0]], [[0, 2, 2, 9], [0, 2, 10]]],
    ),
    SeedSpec(
        "max-single-trade-profit", "Best Single Trade", "Choose one buy and one later sell.",
        "Given daily prices, return the greatest profit from buying once and selling on a later day. Return 0 if no profitable trade exists.",
        ["arrays", "greedy"], [], "max_single_trade_profit", [("prices", "list[int]", "raw")], "int", "raw", EASY_3, 20, "O(n)", "O(1)",
        ["0 <= len(prices) <= 100,000", "Prices are non-negative integers."],
        ["A sale is best relative to the cheapest earlier price.", "Track the minimum price seen so far.", "At each day, update best with price - minimum_so_far.", "One pass maintains both the cheapest buy and best profit."],
        "For each possible sale day, the best buy is the minimum price before it. Track that minimum and the largest difference.",
        [[[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]]],
        [[[]], [[5]], [[1, 2]], [[2, 1]], [[2, 4, 1]], [[3, 3, 3]], [[9, 1, 10]], [[1, 10, 2, 20]], [[10, 9, 8, 20]], [[0, 5]], [[5, 0, 5]], [[8, 2, 4, 1, 7]]],
    ),
    SeedSpec(
        "normalized-palindrome", "Normalized Palindrome", "Ignore punctuation and letter case while checking symmetry.",
        "Return whether the alphanumeric characters in `text` read the same forward and backward, ignoring case and all other characters.",
        ["strings", "two-pointers"], [], "normalized_palindrome", [("text", "str", "raw")], "bool", "raw", EASY_2, 15, "O(n)", "O(1)",
        ["0 <= len(text) <= 100,000", "Unicode alphanumeric checks follow Python's isalnum()."],
        ["Compare characters from both ends.", "Skip non-alphanumeric characters before comparing.", "Lowercase the current valid pair and move inward.", "Two pointers avoid building a normalized copy."],
        "Move two pointers inward, skipping punctuation and comparing valid characters case-insensitively.",
        [["A man, a plan, a canal: Panama"], ["race a car"]],
        [[""], ["."], ["a"], ["Aa"], ["0P"], ["No 'x' in Nixon"], ["ab_a"], ["12321"], ["1231"], ["Was it a car or a cat I saw?"], ["hello"], ["Able was I, ere I saw Elba"]],
    ),
    SeedSpec(
        "merge-sorted-values", "Merge Sorted Values", "Combine two ordered lists without re-sorting.",
        "Return one ascending list containing every item from the two ascending input lists.",
        ["two-pointers", "arrays"], [], "merge_sorted_values", [("left", "list[int]", "raw"), ("right", "list[int]", "raw")], "list[int]", "raw", EASY_3, 20, "O(n + m)", "O(n + m)",
        ["0 <= combined length <= 100,000", "Both inputs are sorted in nondecreasing order."],
        ["The smallest unused value must be at one of the two current positions.", "Keep one pointer for each input.", "Append the smaller pointed value, then append the remainder when one list ends.", "The two-pointer merge is linear and stable."],
        "Compare the first unused value from each list, append the smaller, and advance only that list's pointer.",
        [[[1, 3, 5], [2, 4, 6]], [[], [1, 2]]],
        [[[], []], [[1], []], [[], [1]], [[1], [1]], [[-3, 0], [-2, 4]], [[1, 2], [3, 4]], [[3, 4], [1, 2]], [[1, 1], [1, 1]], [[-5], [5]], [[0, 2, 9], [1, 3]], [[1, 10], [2, 3, 4]], [[-2, -1], [-4, 0]]],
    ),
    SeedSpec(
        "tree-max-depth", "Tree Height", "Measure the longest root-to-leaf path.",
        "Return the number of nodes on the longest path from the root to a leaf. An empty tree has depth 0.",
        ["trees", "recursion"], [], "tree_max_depth", [("root", "TreeNode | None", "treenode")], "int", "raw", EASY_3, 20, "O(n)", "O(h)",
        ["0 <= node count <= 20,000", "Trees are encoded in level order with null gaps."],
        ["A node's depth depends on the deeper child.", "The empty subtree contributes zero.", "Return 1 + max(depth(left), depth(right)).", "Depth-first recursion visits every node once."],
        "The longest path through a node is one plus the greater depth of its left and right subtrees.",
        [[[3, 9, 20, None, None, 15, 7]], [[]]],
        [[[1]], [[1, 2]], [[1, None, 2]], [[1, 2, 3]], [[1, 2, None, 3, None, 4]], [[1, None, 2, None, 3]], [[5, 3, 8, 2, 4, 7, 9]], [[0, -1, 1]], [[1, 2, 3, 4]], [[1, None, 2, 3]], [[9, 8, None, 7]], [[2, 1, 3, None, None, None, 4]]],
    ),
    SeedSpec(
        "longest-unique-span", "Longest Unique Span", "Find the longest substring without repeated characters.",
        "Return the length of the longest contiguous span of `text` containing no repeated character.",
        ["sliding-window", "strings", "hash-maps"], ["strings"], "longest_unique_span", [("text", "str", "raw")], "int", "raw", MEDIUM_4, 25, "O(n)", "O(k)",
        ["0 <= len(text) <= 100,000", "Characters are case-sensitive."],
        ["Maintain a window that is always duplicate-free.", "When a repeat appears, move the left edge beyond its previous occurrence.", "Map each character to its latest index and never move left backward.", "A sliding window visits each position a constant number of times."],
        "Track the latest position of every character. A duplicate inside the current window advances the left boundary.",
        [["abcabcbb"], ["bbbbb"]],
        [[""], ["pwwkew"], ["dvdf"], ["abba"], [" "] , ["au"], ["tmmzuxt"], ["abcdef"], ["aab"], ["anviaj"], ["AaBb"], ["abcadeaf"]],
    ),
    SeedSpec(
        "group-anagram-words", "Group Rearranged Words", "Collect words with identical letter inventories.",
        "Group words that are anagrams. Group order and word order inside groups do not matter.",
        ["hash-maps", "strings"], ["hash-maps"], "group_anagram_words", [("words", "list[str]", "raw")], "list[list[str]]", "raw", MEDIUM_4, 25, "O(n · k log k)", "O(n · k)",
        ["0 <= len(words) <= 10,000", "Words contain lowercase English letters."],
        ["Anagrams share a canonical representation.", "A sorted word can serve as a hashable key.", "Map each tuple(sorted(word)) to the words having that key.", "Return the collected dictionary values."],
        "Canonicalize each word by sorting its letters, then group words sharing that key.",
        [[['eat', 'tea', 'tan', 'ate', 'nat', 'bat']], [[""]]],
        [[[]], [["a"]], [["ab", "ba"]], [["abc", "def"]], [["listen", "silent", "enlist"]], [["aa", "aa"]], [["rat", "tar", "art", "car"]], [["b", "bb", "bbb"]], [["ab", "a", "ba"]], [["tea", "eat", "ate", "eta"]], [["abc", "bca", "cab", "xyz"]], [["no", "on", "no"]]], "unordered_nested",
    ),
    SeedSpec(
        "three-sum-zero", "Three Values to Zero", "Find unique triples whose sum is zero.",
        "Return every unique sorted triple of values from distinct indices that sums to zero. Result order does not matter.",
        ["two-pointers", "arrays"], ["two-pointers"], "three_sum_zero", [("nums", "list[int]", "raw")], "list[list[int]]", "raw", MEDIUM_6, 35, "O(n²)", "O(n) for sorting/output", 
        ["0 <= len(nums) <= 3,000", "Duplicate input values are allowed."],
        ["Sorting exposes useful order and makes duplicates adjacent.", "Fix one number, then search the suffix with two pointers.", "Move left for a small sum and right for a large sum; skip repeated values.", "Sorting plus an outer loop and inner two-pointer scan gives O(n²)."],
        "Sort the values, fix each distinct first value, and use two pointers to find complementary pairs while skipping duplicates.",
        [[[-1, 0, 1, 2, -1, -4]], [[0, 1, 1]]],
        [[[]], [[0]], [[0, 0, 0]], [[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[-1, -1, 2]], [[-3, -2, -1, 0, 1, 2, 3]], [[1, 2, -3]], [[1, 2, 3]], [[-4, 2, 2]], [[-5, 0, 5, 10, -10]], [[-2, -2, 0, 2, 2]]], "unordered_nested",
    ),
    SeedSpec(
        "days-until-warmer", "Next Warmer Day", "Measure the wait for a warmer reading.",
        "For every temperature, return how many later days pass before a strictly warmer temperature. Use 0 when none exists.",
        ["stacks", "arrays"], ["stacks"], "days_until_warmer", [("temperatures", "list[int]", "raw")], "list[int]", "raw", MEDIUM_5, 25, "O(n)", "O(n)",
        ["0 <= len(temperatures) <= 100,000", "Temperatures are integers."],
        ["Unresolved days can wait in a stack.", "A warmer current day resolves earlier colder stack entries.", "Store indices in decreasing temperature order.", "Each index enters and leaves the monotonic stack at most once."],
        "Maintain indices whose next warmer day is unknown. A warmer value pops and resolves every smaller temperature on top.",
        [[[73, 74, 75, 71, 69, 72, 76, 73]], [[30, 40, 50, 60]]],
        [[[]], [[50]], [[60, 50, 40]], [[40, 40, 40]], [[40, 41]], [[41, 40, 42]], [[70, 71, 70, 72]], [[1, 3, 2, 4]], [[90, 80, 70, 60, 100]], [[10, 20, 10, 20]], [[0, -1, 1]], [[5, 4, 3, 2, 1, 6]]],
    ),
    SeedSpec(
        "rotated-array-search", "Search a Rotated Array", "Use binary search across a single rotation.",
        "A strictly increasing array was rotated at an unknown position. Return the target index or -1.",
        ["binary-search", "arrays"], ["binary-search"], "rotated_array_search", [("nums", "list[int]", "raw"), ("target", "int", "raw")], "int", "raw", MEDIUM_6, 35, "O(log n)", "O(1)",
        ["0 <= len(nums) <= 100,000", "All values are unique."],
        ["At least one half around the midpoint remains sorted.", "Identify the sorted half before deciding where the target could lie.", "Keep the half whose inclusive range contains target; discard the other.", "Modified binary search preserves logarithmic time."],
        "At every step, one side of the midpoint is sorted. Range checks identify whether the target is inside that side.",
        [[[4, 5, 6, 7, 0, 1, 2], 0], [[4, 5, 6, 7, 0, 1, 2], 3]],
        [[[], 1], [[1], 1], [[1], 0], [[3, 1], 1], [[3, 1], 3], [[5, 1, 3], 5], [[5, 1, 3], 3], [[6, 7, 1, 2, 3, 4, 5], 4], [[2, 3, 4, 5, 1], 2], [[2, 3, 4, 5, 1], 1], [[8, 9, 2, 3, 4], 7], [[0, 1, 2, 3, 4], 2]],
    ),
    SeedSpec(
        "merge-intervals", "Merge Overlapping Reservations", "Collapse overlapping closed intervals.",
        "Merge all overlapping closed intervals and return the non-overlapping result ordered by start.",
        ["intervals", "sorting"], ["arrays"], "merge_intervals", [("intervals", "list[list[int]]", "raw")], "list[list[int]]", "raw", MEDIUM_4, 25, "O(n log n)", "O(n)",
        ["0 <= len(intervals) <= 20,000", "Each interval has start <= end."],
        ["Process intervals in starting-time order.", "Only the most recently merged interval can overlap the next one.", "Extend the last end when next.start <= last.end; otherwise append.", "Sorting dominates the running time."],
        "Sort by start, then either extend the last merged interval or begin a new one.",
        [[[[1, 3], [2, 6], [8, 10], [15, 18]]], [[[1, 4], [4, 5]]]],
        [[[]], [[[1, 2]]], [[[5, 7], [1, 3]]], [[[1, 10], [2, 3]]], [[[1, 2], [3, 4]]], [[[1, 5], [2, 6], [7, 8]]], [[[0, 0], [0, 1]]], [[[-3, -1], [-2, 2]]], [[[1, 4], [0, 2], [3, 5]]], [[[1, 2], [2, 3], [3, 4]]], [[[10, 12], [2, 4], [6, 8]]], [[[1, 100], [50, 60], [101, 102]]]],
    ),
    SeedSpec(
        "tree-level-order", "Tree Levels", "Read a tree one depth at a time.",
        "Return node values grouped by depth from left to right, beginning with the root level.",
        ["trees", "queues"], ["trees"], "tree_level_order", [("root", "TreeNode | None", "treenode")], "list[list[int]]", "raw", MEDIUM_4, 25, "O(n)", "O(w)",
        ["0 <= node count <= 20,000", "Input uses level-order encoding."],
        ["Breadth-first search naturally processes a tree by depth.", "The queue length at the start of a round is that level's size.", "Pop exactly level_size nodes, enqueue their children, then append the collected values.", "The queue stores at most one tree width."],
        "Use breadth-first search. Snapshot the queue length before each level so newly enqueued children belong to the next group.",
        [[[3, 9, 20, None, None, 15, 7]], [[1]]],
        [[[]], [[1, 2, 3]], [[1, 2, None, 3]], [[1, None, 2, None, 3]], [[5, 3, 8, 2, 4, 7, 9]], [[0, -1, 1]], [[1, 2, 3, 4, 5]], [[1, None, 2, 3]], [[9, 8, None, 7]], [[2, 1, 3, None, None, None, 4]], [[10, 5, 15, 2, 7, 12, 20]], [[1, 2, 3, None, 4, None, 5]]],
    ),
    SeedSpec(
        "valid-binary-search-tree", "Validate Search-Tree Ordering", "Check global ordering constraints in a binary tree.",
        "Return whether every node is strictly greater than all values in its left subtree and strictly smaller than all values in its right subtree.",
        ["trees", "recursion"], ["trees"], "is_valid_bst", [("root", "TreeNode | None", "treenode")], "bool", "raw", MEDIUM_5, 30, "O(n)", "O(h)",
        ["0 <= node count <= 20,000", "Duplicate values make the tree invalid."],
        ["Comparing only a node with its children is insufficient.", "Carry the legal lower and upper bound down the tree.", "The left child inherits the upper bound node.val; the right inherits the lower bound.", "Every node must fall strictly inside its inherited range."],
        "Depth-first search carries bounds imposed by every ancestor, which enforces the global search-tree property.",
        [[[2, 1, 3]], [[5, 1, 4, None, None, 3, 6]]],
        [[[]], [[1]], [[2, 2, 3]], [[2, 1, 2]], [[10, 5, 15, None, None, 6, 20]], [[10, 5, 15, 2, 7, 12, 20]], [[0, -1, 1]], [[1, None, 2, None, 3]], [[3, 2, 5, 1, 4]], [[5, 3, 7, 2, 4, 6, 8]], [[5, 3, 7, None, 6]], [[8, 4, 12, 2, 6, 10, 14]]],
    ),
    SeedSpec(
        "count-islands", "Count Connected Islands", "Count four-directional land components.",
        "A grid contains '1' for land and '0' for water. Return the number of four-directionally connected land regions.",
        ["graphs", "breadth-first-search"], ["queues"], "count_islands", [("grid", "list[list[str]]", "raw")], "int", "raw", MEDIUM_5, 30, "O(rows · columns)", "O(rows · columns)",
        ["The grid may be empty.", "All non-empty rows have equal length."],
        ["Each island is a connected component.", "When unvisited land is found, count once and traverse its whole component.", "BFS or DFS marks four-directional neighbors as visited.", "Every cell is processed at most once."],
        "Scan the grid. Each unvisited land cell starts one traversal that marks exactly one complete island.",
        [[[['1','1','0'],['1','0','0'],['0','0','1']]], [[['0','0'],['0','0']]]],
        [[[]], [[['1']]], [[['0']]], [[['1','1'],['1','1']]], [[['1','0'],['0','1']]], [[['1','0','1']]], [[['1'],['0'],['1']]], [[['1','1','0','1'],['0','1','0','1']]], [[['0','1','0'],['1','1','1'],['0','1','0']]], [[['1','0','0'],['0','1','0'],['0','0','1']]], [[['1','1','1'],['0','0','0'],['1','1','1']]], [[['1','0'],['1','0'],['0','1']]]],
    ),
    SeedSpec(
        "shortest-clear-path", "Shortest Clear Grid Path", "Find an eight-directional path through open cells.",
        "In a rectangular 0/1 grid, return the number of cells in the shortest path from top-left to bottom-right through zero cells using eight directions. Return -1 when impossible.",
        ["graphs", "breadth-first-search"], ["graphs"], "shortest_clear_path", [("grid", "list[list[int]]", "raw")], "int", "raw", MEDIUM_6, 35, "O(rows · columns)", "O(rows · columns)",
        ["1 <= rows, columns <= 200", "Cells contain only 0 or 1."],
        ["All moves have equal cost, which points to breadth-first search.", "Start distance at one because path length counts cells.", "Enqueue each unseen zero neighbor in all eight directions.", "The first visit to the destination is shortest."],
        "Breadth-first search explores every path length in order. Mark cells when enqueued to prevent duplicate work.",
        [[[[0,1],[1,0]]], [[[0,0,0],[1,1,0],[1,1,0]]]],
        [[[[1]]], [[[0]]], [[[0,1],[1,1]]], [[[0,0],[0,0]]], [[[0,1,0],[0,1,0],[0,0,0]]], [[[0,0,1],[1,0,1],[1,0,0]]], [[[0,1,1],[1,0,1],[1,1,0]]], [[[0,0,0,0]]], [[[0],[0],[0]]], [[[0,1,0],[1,1,0],[0,0,0]]], [[[0,0,1],[0,1,0],[0,0,0]]], [[[0,0],[1,0],[1,0]]]],
    ),
    SeedSpec(
        "top-k-frequent", "Most Frequent Values", "Return the k values occurring most often.",
        "Return the `k` most frequent distinct values. Test data never ties across the selection boundary; result order does not matter.",
        ["heaps", "hash-maps", "buckets"], ["hash-maps"], "top_k_frequent", [("nums", "list[int]", "raw"), ("k", "int", "raw")], "list[int]", "raw", MEDIUM_5, 30, "O(n)", "O(n)",
        ["1 <= k <= number of distinct values", "Boundary frequencies are unique."],
        ["First count every distinct value.", "A frequency cannot exceed len(nums), so frequencies can index buckets.", "Place values into frequency buckets and read buckets from high to low.", "Bucket counting avoids sorting all distinct values."],
        "Count values, bucket them by frequency, then traverse buckets from most frequent until k values are collected.",
        [[[1,1,1,2,2,3], 2], [[1], 1]],
        [[[[4,4,4,3,3,2],1][0], 1], [[-1,-1,2,2,2,3], 2], [[0,0,0,1,1,2], 1], [[5,5,4,4,4,3,3,3,3], 2], [[1,2,3,3,3], 1], [[8,8,7,7,7,6], 2], [[1,1,2,3,3,3], 2], [[9,9,9,8,7], 1], [[2,2,2,1,1,3,4], 2], [[10,20,20,30,30,30], 2], [[-2,-2,-2,-1,-1,0], 2], [[6,6,5,5,5,4,4,4,4], 1]], "unordered",
    ),
    SeedSpec(
        "combination-sum-once", "One-Use Combination Sum", "Choose unique combinations that reach a target.",
        "Each candidate occurrence may be used at most once. Return all unique nondecreasing combinations summing to target; result order does not matter.",
        ["backtracking", "sorting"], ["recursion"], "combination_sum_once", [("candidates", "list[int]", "raw"), ("target", "int", "raw")], "list[list[int]]", "raw", MEDIUM_7, 40, "O(2ⁿ)", "O(n) excluding output",
        ["1 <= candidate <= 50", "0 <= len(candidates) <= 20", "1 <= target <= 100"],
        ["Sort first so duplicates become adjacent and large values can stop a branch.", "At one recursion depth, skip a candidate equal to the previous candidate.", "Recurse with index + 1 because each occurrence is single-use.", "Backtracking explores choices while duplicate skipping keeps outputs unique."],
        "Sort candidates, explore include choices from a moving start index, and skip equal siblings at each recursive depth.",
        [[[10,1,2,7,6,1,5], 8], [[2,5,2,1,2], 5]],
        [[[], 3], [[1], 1], [[1], 2], [[1,1], 1], [[1,1], 2], [[1,2,3], 3], [[2,3,6,7], 7], [[2,2,2], 4], [[3,1,3,5,1,1], 8], [[4,4,2,2], 6], [[5,6,7], 4], [[1,2,2,2,5], 5]], "unordered_nested",
    ),
    SeedSpec(
        "minimum-window", "Minimum Required Window", "Find the shortest substring covering a character multiset.",
        "Return the shortest substring of `text` containing every character of `required` with multiplicity. Return the earliest on ties and empty when impossible.",
        ["sliding-window", "hash-maps", "strings"], ["sliding-window", "hash-maps"], "minimum_window", [("text", "str", "raw"), ("required", "str", "raw")], "str", "raw", HARD_8, 50, "O(n + m)", "O(k)",
        ["0 <= combined length <= 200,000", "Characters are case-sensitive."],
        ["Expand until every required character count is satisfied.", "Track how many distinct required counts are currently complete.", "Once complete, move the left edge while preserving validity and record improvements.", "Two moving boundaries plus frequency maps give linear time."],
        "Use a frequency-aware sliding window. Expand to become valid, then shrink greedily to find the smallest valid window.",
        [["ADOBECODEBANC", "ABC"], ["a", "aa"]],
        [["", "a"], ["abc", ""], ["a", "a"], ["aa", "aa"], ["ab", "b"], ["bba", "ab"], ["aaab", "aab"], ["this is a test", "tist"], ["abcabdebac", "abc"], ["xyyzyzyx", "xyz"], ["Aabc", "Aa"], ["cabefgecdaecf", "cae"]],
    ),
    SeedSpec(
        "word-ladder-steps", "Word Transformation Ladder", "Find a shortest one-letter-at-a-time transformation.",
        "Return the number of words in the shortest sequence from `begin` to `end`, changing one letter at a time and using only listed intermediate words. Return 0 if impossible.",
        ["graphs", "breadth-first-search", "strings"], ["graphs"], "word_ladder_steps", [("begin", "str", "raw"), ("end", "str", "raw"), ("words", "list[str]", "raw")], "int", "raw", HARD_8, 50, "O(N · L · 26)", "O(N)",
        ["All words have equal lowercase length.", "1 <= word length <= 10", "0 <= len(words) <= 5,000"],
        ["Treat words as graph nodes and one-letter changes as edges.", "Breadth-first search finds the fewest transformations.", "Generate neighbors by replacing each position with every lowercase letter.", "Remove discovered words immediately so each is enqueued once."],
        "Breadth-first search from begin explores transformation counts in order. Generated valid neighbors are removed from the remaining set when queued.",
        [["hit", "cog", ["hot","dot","dog","lot","log","cog"]], ["hit", "cog", ["hot","dot","dog","lot","log"]]],
        [["a", "c", ["a","b","c"]], ["hot", "dog", ["hot","dog"]], ["hot", "dog", ["hot","dot","dog"]], ["red", "tax", ["ted","tex","red","tax","tad","den","rex","pee"]], ["same", "same", ["same"]], ["abc", "xyz", []], ["abc", "abd", ["abd"]], ["lost", "cost", ["most","fist","lost","cost","fish"]], ["talk", "tail", ["talk","tons","fall","tail","gale","hall"]], ["cat", "dog", ["cot","cog","dog"]], ["aaa", "bbb", ["aab","abb","bbb"]], ["aaa", "ccc", ["aac","acc","ccc"]]],
    ),
    SeedSpec(
        "weighted-job-schedule", "Weighted Schedule", "Select compatible jobs with maximum total profit.",
        "Jobs have start, end, and profit arrays. Select non-overlapping jobs with maximum profit; a job ending when another starts is compatible.",
        ["dynamic-programming", "binary-search", "intervals"], ["binary-search", "intervals"], "max_weighted_schedule", [("starts", "list[int]", "raw"), ("ends", "list[int]", "raw"), ("profits", "list[int]", "raw")], "int", "raw", HARD_9, 60, "O(n log n)", "O(n)",
        ["Arrays have equal length up to 50,000.", "start < end and profit is non-negative."],
        ["Sort jobs by finish time.", "For each job, compare skipping it with taking it after the best compatible prefix.", "Binary search the finish times to locate the last job ending no later than this start.", "A one-dimensional DP over finish-sorted jobs captures the optimum."],
        "Sort by end time. DP[index] stores the best profit among the first index jobs; binary search finds the compatible prefix for taking each job.",
        [[[1,2,3,3], [3,4,5,6], [50,10,40,70]], [[1,2,3,4,6], [3,5,10,6,9], [20,20,100,70,60]]],
        [[[], [], []], [[1],[2],[5]], [[1,2],[2,3],[5,6]], [[1,1],[3,2],[5,10]], [[1,3,6],[3,5,9],[20,20,100]], [[1,2,4],[4,4,6],[5,6,5]], [[1,5,10],[4,9,12],[10,20,30]], [[0,2,4,6],[2,4,6,8],[1,2,3,4]], [[1,2,3],[10,4,5],[100,5,5]], [[1,3,5],[2,4,6],[10,10,10]], [[1,2,50],[2,50,51],[5,100,5]], [[2,4,6,8],[5,7,9,10],[20,30,25,50]]],
    ),
    SeedSpec(
        "median-sorted-arrays", "Median of Two Sorted Arrays", "Partition two sorted arrays without fully merging them.",
        "Return the median of two ascending arrays. At least one array is non-empty. The required running time is logarithmic in the shorter array.",
        ["binary-search", "arrays", "partitioning"], ["binary-search"], "median_sorted_arrays", [("left", "list[int]", "raw"), ("right", "list[int]", "raw")], "float", "raw", HARD_10, 75, "O(log min(n, m))", "O(1)",
        ["0 <= each length <= 100,000", "At least one input is non-empty.", "Inputs are sorted."],
        ["A correct partition puts half the combined values on the left.", "Binary-search how many values to take from the shorter array.", "A partition is valid when both left-side maxima are <= both right-side minima.", "Use infinities at empty partition edges, then derive the odd or even median."],
        "Binary-search a partition in the shorter array and infer the complementary partition in the other. Adjust until cross-boundary ordering is valid.",
        [[[1,3], [2]], [[1,2], [3,4]]],
        [[[], [1]], [[1], []], [[0,0], [0,0]], [[2], [1,3]], [[1,2,3], [4,5,6]], [[1,4,7], [2,3,5,6]], [[-5,-3,-1], [-2,0]], [[1], [2,3,4,5]], [[1,2,8,9], [3,4,5,6,7]], [[-10], [10]], [[1,1], [1,1,1]], [[100,200], [-5,0,50]]], "float",
    ),
]


CORE_PROBLEMS = [build_problem(spec) for spec in SEEDS]

# The launch core is extended by 76 different callable questions. They use
# distinct function names and operations rather than repeated editions.
from .distinct_content import DISTINCT_PROBLEMS

PROBLEMS = [*CORE_PROBLEMS, *DISTINCT_PROBLEMS]
