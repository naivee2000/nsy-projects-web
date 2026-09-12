"""First reviewed import batch: reusable definitions and independent test oracles.

These implementations and explanations were written for the app. Workbook examples
and source contracts are reconciled by LeetCode ID. Import code is an offline tool;
the web app never imports this module or executes these generators.
"""
from __future__ import annotations

from itertools import combinations
import random
from textwrap import dedent


def add_oracle(arguments):
    a, b = arguments
    total = sum(value * 10**i for i, value in enumerate(a)) + sum(value * 10**i for i, value in enumerate(b))
    return [int(digit) for digit in str(total)[::-1]]


def tree_oracle(arguments):
    # Build canonical heap-index/value maps from queue-serialized trees. This is
    # independent of the reference's recursive pairwise node comparison.
    def positions(values):
        if not values or values[0] is None:
            return {}
        result, queue, i = {1: values[0]}, [1], 1
        for parent in queue:
            for position in (parent * 2, parent * 2 + 1):
                if i >= len(values):
                    return result
                if values[i] is not None:
                    result[position] = values[i]
                    queue.append(position)
                i += 1
        return result
    return positions(arguments[0]) == positions(arguments[1])


def word_oracle(arguments):
    board, word = arguments
    # Exhaustive simple paths with explicit immutable visited sets, no recursive
    # mutation or restoration as used by the reference implementation.
    rows, cols = len(board), len(board[0])
    stack = [(r, c, 0, frozenset()) for r in range(rows) for c in range(cols)]
    while stack:
        r, c, index, visited = stack.pop()
        if not (0 <= r < rows and 0 <= c < cols) or (r, c) in visited or board[r][c] != word[index]:
            continue
        if index == len(word) - 1:
            return True
        seen = visited | {(r, c)}
        stack.extend((r + dr, c + dc, index + 1, seen) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return False


def water_oracle(arguments):
    height, = arguments
    return max((j - i) * min(height[i], height[j]) for i, j in combinations(range(len(height)), 2))


def random_add(rng):
    def digits():
        n = rng.randint(1, 18)
        return [rng.randrange(10) for _ in range(n - 1)] + [rng.randint(1 if n > 1 else 0, 9)]
    return [digits(), digits()]


def random_tree(rng):
    def tree():
        if rng.random() < .15:
            return []
        values, pending = [rng.randrange(-10, 11)], 1
        while pending and len(values) < 31:
            pending -= 1
            for _ in range(2):
                value = None if rng.random() < .4 else rng.randrange(-10, 11)
                values.append(value)
                pending += value is not None
        while values and values[-1] is None:
            values.pop()
        return values
    left = tree()
    return [left, left.copy() if rng.random() < .5 else tree()]


def random_word(rng):
    rows, cols = rng.randint(1, 3), rng.randint(1, 3)
    board = [[rng.choice("ABC") for _ in range(cols)] for _ in range(rows)]
    return [board, "".join(rng.choice("ABC") for _ in range(rng.randint(1, 7)))]


def random_water(rng):
    return [[rng.randrange(30) for _ in range(rng.randint(2, 24))]]


ADD_REFERENCE = dedent('''\
def add_two_numbers(l1, l2):
    dummy = ListNode()
    tail = dummy
    carry = 0
    while l1 is not None or l2 is not None or carry:
        total = carry
        if l1 is not None:
            total += l1.val
            l1 = l1.next
        if l2 is not None:
            total += l2.val
            l2 = l2.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next
''')
TREE_REFERENCE = dedent('''\
def same_tree(p, q):
    if p is None or q is None:
        return p is q
    return p.val == q.val and same_tree(p.left, q.left) and same_tree(p.right, q.right)
''')
WORD_REFERENCE = dedent('''\
def word_search(board, word):
    rows, cols = len(board), len(board[0])
    def visit(row, col, index):
        if not (0 <= row < rows and 0 <= col < cols) or board[row][col] != word[index]:
            return False
        if index == len(word) - 1:
            return True
        letter = board[row][col]
        board[row][col] = None
        found = any(visit(row + dr, col + dc, index + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[row][col] = letter
        return found
    return any(visit(row, col, 0) for row in range(rows) for col in range(cols))
''')
WATER_REFERENCE = dedent('''\
def max_water_area(height):
    left, right, best = 0, len(height) - 1, 0
    while left < right:
        best = max(best, (right - left) * min(height[left], height[right]))
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1
    return best
''')

BATCH = {
    2: dict(name="add_two_numbers", topics=["linked-lists", "math"],
        params=[("l1", "ListNode | None", "listnode"), ("l2", "ListNode | None", "listnode")],
        returns="ListNode | None", adapter="listnode", difficulty=5,
        constraints=["Each input list has 1–100 nodes.", "Each node value is a digit from 0 through 9.",
                     "Digits are stored least significant first. Only the number zero has a most significant zero."],
        time="O(m + n)", space="O(m + n) including the output",
        examples=[([[2, 4, 3], [5, 6, 4]], "The lists represent 342 and 465. Their sum is 807, stored as [7, 0, 8]."),
                  ([[9, 9], [1]], "99 + 1 = 100. Carrying across both input digits creates one new output node: [0, 0, 1].")],
        boundaries=[[[0], [0]], [[0], [5]], [[9], [9]], [[1], [9]], [[1], [2, 3]],
                    [[2, 3], [1]], [[9, 9, 9], [9, 9]], [[1, 0, 1], [9, 9]],
                    [[5, 4], [5, 5]], [[9] * 100, [1]], [[0], [9] * 100], [[1, 2, 3], [4, 5, 6]]],
        reference=ADD_REFERENCE, oracle=add_oracle, generator=random_add,
        wrong=[ADD_REFERENCE.replace(" or carry:", ":"), ADD_REFERENCE.replace("total = carry", "total = 0")],
        wrong_reasons=["Drops a final carry after both lists end.", "Fails to propagate carry between digits."],
        hints=["Column addition needs a carry between positions.",
               "Traverse both chains together, treating an exhausted chain's digit as zero.",
               "While either node or carry remains: sum the digits and carry, divide by ten, append the remainder, and advance nodes.",
               "A dummy head and moving tail let you append each result digit without a special first-node branch."],
        editorial="Visit corresponding digit positions from least to most significant. Add both digits and the incoming carry. The remainder after division by ten is the next result digit; the quotient is the next carry. Continue after an input ends, and append any final carry. Every input node is visited once and the output has at most max(m,n)+1 nodes."),
    100: dict(name="same_tree", topics=["trees", "recursion", "depth-first-search"],
        params=[("p", "TreeNode | None", "treenode"), ("q", "TreeNode | None", "treenode")],
        returns="bool", adapter="raw", difficulty=3,
        constraints=["Each tree contains 0–100 nodes.", "Node values range from -10,000 to 10,000.",
                     "The displayed arrays use level order; null denotes a missing child."],
        time="O(n + m)", space="O(h) recursive stack",
        examples=[([[1, 2, 3], [1, 2, 3]], "Both trees have root 1, left child 2, and right child 3, so values and structure match."),
                  ([[1, 2], [1, None, 2]], "The value 2 is a left child in the first tree but a right child in the second. Equal values alone are insufficient.")],
        boundaries=[[[], []], [[1], []], [[], [1]], [[1], [1]], [[1], [2]],
                    [[1, 2, 3], [1, 3, 2]], [[0, 0], [0]], [[-1, -2], [-1, -2]],
                    [[1, None, 2, 3], [1, None, 2, 3]], [[1, None, 2, 3], [1, None, 2, None, 3]],
                    [[10000], [-10000]], [[0] * 100, [0] * 100]],
        reference=TREE_REFERENCE, oracle=tree_oracle, generator=random_tree,
        wrong=[TREE_REFERENCE.replace("p.val == q.val and ", ""),
               TREE_REFERENCE.replace("same_tree(p.right, q.right)", "True")],
        wrong_reasons=["Compares structure but ignores node values.", "Never checks the right subtrees."],
        hints=["Equal trees require both matching values and matching missing-child positions.",
               "Compare a pair of corresponding nodes, then their left and right pairs.",
               "If either node is absent, require both absent. Otherwise require equal values and two successful subtree comparisons.",
               "A recursive comparison stops immediately at a value or structure mismatch."],
        editorial="Treat empty nodes as part of the tree's structure. Two absent nodes match; exactly one absent node fails. For two present nodes, compare their values, then recursively compare corresponding left and right children. The recursion holds at most a root-to-leaf chain of calls. No subtree should be skipped just because the root values match."),
    79: dict(name="word_search", topics=["matrices", "recursion", "backtracking", "depth-first-search"],
        params=[("board", "list[list[str]]", "raw"), ("word", "str", "raw")],
        returns="bool", adapter="raw", difficulty=6,
        constraints=["The board is rectangular with 1–6 rows and 1–6 columns.", "The word has 1–15 letters.",
                     "Board cells and the word contain English letters, with case significant.",
                     "Move up, down, left, or right; a cell may be used at most once in a candidate path."],
        time="O(rows × cols × 4^L)", space="O(L)",
        examples=[([[['A','B','C','E'],['S','F','C','S'],['A','D','E','E']], "ABCCED"],
                   "A path from (0,0) follows right, right, down, down, left to spell ABCCED without reusing a cell."),
                  ([[['A','B']], "ABA"], "The last A would require returning to the starting cell, which cannot be reused, so the answer is false.")],
        boundaries=[[[['A']], "A"], [[['A']], "B"], [[['A','B']], "AB"], [[['A','B']], "BA"],
                    [[['A','X'],['X','B']], "AB"], [[['A','B'],['D','C']], "ABCD"],
                    [[['A','A'],['A','A']], "AAAA"], [[['A','A'],['A','A']], "AAAAA"],
                    [[['a','A']], "aA"], [[['A'],['B'],['C']], "CBA"],
                    [[['C','A','A'],['A','A','A'],['B','C','D']], "AAB"],
                    [[["A"] * 6 for _ in range(6)], "A" * 15]],
        reference=WORD_REFERENCE, oracle=word_oracle, generator=random_word,
        wrong=[WORD_REFERENCE.replace("board[row][col] = None", "board[row][col] = letter"),
               WORD_REFERENCE.replace("((1, 0), (-1, 0), (0, 1), (0, -1))", "((1, 0), (0, 1))")],
        wrong_reasons=["Reuses a cell already on the current path.", "Searches only down/right and misses paths that turn up/left."],
        hints=["A cell belongs to the current candidate path, not to every path tried so far.",
               "Start a depth-first search at each cell. Mark a matching cell while exploring neighbors and restore it when returning.",
               "Reject out-of-bounds or mismatching cells. Accept the final letter. Otherwise mark, search four neighbors for the next letter, restore, and return the result.",
               "Backtracking restores the board so a failed candidate does not block another starting point."],
        editorial="For each starting cell, attempt to match the word one character at a time. A recursive call represents one position in the word and one board cell. Temporarily mark a matching cell as unavailable, explore four orthogonal neighbors, then restore it before returning. Restoration is necessary even when a child succeeds so the input remains usable. Returning a global visited set across attempts would incorrectly eliminate valid paths."),
    11: dict(name="max_water_area", topics=["arrays", "two-pointers", "greedy"],
        params=[("height", "list[int]", "raw")], returns="int", adapter="raw", difficulty=5,
        constraints=["2 <= len(height) <= 100,000.", "0 <= height[i] <= 10,000.",
                     "Lines stand at their zero-based indices. Select exactly two lines; containers cannot be tilted."],
        time="O(n)", space="O(1)",
        examples=[([[1,8,6,2,5,4,8,3,7]], "Indices 1 and 8 give width 7 and limiting height 7, holding area 49."),
                  ([[1,1]], "The only pair has width 1 and height 1, so the maximum area is 1.")],
        boundaries=[[[0,0]], [[0,5]], [[5,0]], [[2,9]], [[9,2]], [[5,1,5]],
                    [[1,2,3,4,5]], [[5,4,3,2,1]], [[8,8,8,8]], [[0,9,0,9,0]],
                    [[9,1,2,3,4,5,6]], [[10000,0,10000]]],
        reference=WATER_REFERENCE, oracle=water_oracle, generator=random_water,
        wrong=[WATER_REFERENCE.replace("min(height[left], height[right])", "max(height[left], height[right])"),
               WATER_REFERENCE.replace("height[left] <= height[right]", "height[left] >= height[right]")],
        wrong_reasons=["Uses the taller line instead of the limiting shorter line.", "Moves the taller boundary and discards potentially optimal pairs."],
        hints=["Area depends on both distance and the shorter of the two lines.",
               "Begin at both ends. Moving the taller line inward cannot help while the shorter line is fixed.",
               "Record width times the shorter height; move the pointer at the shorter height; repeat until the pointers meet.",
               "Discarding the shorter boundary is safe because no narrower pair using that boundary can improve the current area."],
        editorial="Evaluate the two outermost remaining lines. The shorter height limits the water, and the index difference is the width. Any other pair retaining the shorter line has less width and cannot exceed that limiting height. Therefore it is safe to discard the shorter line and continue inward. Each pointer moves at most n times, using constant auxiliary space."),
}
